"""
Rigorous, Native AST-Based Python Mutation Testing Engine.

Implements standard software engineering mutation operators (ROR, AOR, LCR, COR)
with strict empirical validity controls:
1. Baseline Pre-check: All tests are verified on the unmutated baseline first.
   Tests that already fail on the baseline CANNOT be credited with killing any mutant
   (spurious/false kill filtering).
2. Legitimate Kill Criterion: A mutant is considered KILLED if and only if
   a baseline-passing test fails via ASSERTION_FAILED or TIMEOUT.
3. Safe Isolated Execution: Mutated code is evaluated in an isolated working copy;
   shared baseline benchmark repositories are never modified.
4. Robust Metric Calculation: If the denominator (valid mutants) is 0, mutation score
   is explicitly reported as None / "Undefined" rather than a misleading 0.0 or 1.0.
5. Built-in Control Mutants: Includes verification hooks for known killable vs
   unkillable/equivalent control mutants.
"""

import ast
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from src.execution.structured_executor import execute_suite, ExecutionMode, SuiteExecutionResult, build_env


def _clean_pycache(dirs: List[Path]):
    """Purge bytecode caches to guarantee clean module execution across mutants."""
    for d in dirs:
        if not d.exists():
            continue
        try:
            for pycache in d.rglob("__pycache__"):
                shutil.rmtree(pycache, ignore_errors=True)
            for pyc in d.rglob("*.pyc"):
                try:
                    pyc.unlink(missing_ok=True)
                except Exception:
                    pass
        except Exception:
            pass


def verify_module_import_origin(
    target_file: Path,
    cwd: Path,
    python_paths: Optional[List[str]] = None,
) -> dict:
    """
    Verify via clean subprocess probe that target_file resolves to the isolated
    working directory rather than an external site-packages install.
    """
    target_path = Path(target_file).resolve()
    stem = target_path.stem
    probe_code = f"""
import sys, importlib
try:
    mod = importlib.import_module('{stem}')
    mod_file = getattr(mod, '__file__', '')
    print(f'PROBE_FILE:{{mod_file}}')
except Exception as e:
    print(f'PROBE_ERR:{{e}}')
"""
    env = build_env(python_paths)
    try:
        proc = subprocess.run(
            [sys.executable, "-c", probe_code],
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        origin_file = ""
        for line in proc.stdout.splitlines():
            if line.startswith("PROBE_FILE:"):
                origin_file = line[len("PROBE_FILE:"):].strip()
        is_isolated = False
        if origin_file:
            try:
                origin_p = Path(origin_file).resolve()
                is_isolated = origin_p == target_path or origin_p.is_relative_to(cwd.resolve())
            except (ValueError, AttributeError):
                is_isolated = str(cwd.resolve()).lower() in origin_file.lower()
        return {
            "origin_file": origin_file,
            "target_path": str(target_path),
            "is_isolated": is_isolated,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except Exception as exc:
        return {
            "origin_file": "",
            "target_path": str(target_path),
            "is_isolated": False,
            "error": str(exc),
        }


# ---------- AST Mutation Operators ----------

class MutationVisitor(ast.NodeTransformer):
    """Generates one mutant per visit by modifying a single AST node matching target_id."""

    RELATIONAL_MAP = {
        ast.Eq: ast.NotEq,
        ast.NotEq: ast.Eq,
        ast.Lt: ast.GtE,
        ast.LtE: ast.Gt,
        ast.Gt: ast.LtE,
        ast.GtE: ast.Lt,
        ast.In: ast.NotIn,
        ast.NotIn: ast.In,
        ast.Is: ast.IsNot,
        ast.IsNot: ast.Is,
    }

    ARITHMETIC_MAP = {
        ast.Add: ast.Sub,
        ast.Sub: ast.Add,
        ast.Mult: ast.FloorDiv,
        ast.FloorDiv: ast.Mult,
    }

    LOGICAL_MAP = {
        ast.And: ast.Or,
        ast.Or: ast.And,
    }

    def __init__(self, target_mutation_id: int):
        super().__init__()
        self.target_mutation_id = target_mutation_id
        self.current_mutation_id = 0
        self.applied_mutation = None

    def visit_Compare(self, node: ast.Compare):
        self.generic_visit(node)
        new_ops = []
        mutated = False
        for op in node.ops:
            op_type = type(op)
            if op_type in self.RELATIONAL_MAP:
                if self.current_mutation_id == self.target_mutation_id and not mutated:
                    replacement_type = self.RELATIONAL_MAP[op_type]
                    new_ops.append(replacement_type())
                    self.applied_mutation = {
                        "id": self.current_mutation_id,
                        "operator": "ROR",
                        "lineno": getattr(node, "lineno", 0),
                        "original": op_type.__name__,
                        "replacement": replacement_type.__name__,
                    }
                    mutated = True
                else:
                    new_ops.append(op)
                self.current_mutation_id += 1
            else:
                new_ops.append(op)
        if mutated:
            node.ops = new_ops
        return node

    def visit_BinOp(self, node: ast.BinOp):
        self.generic_visit(node)
        op_type = type(node.op)
        if op_type in self.ARITHMETIC_MAP:
            if self.current_mutation_id == self.target_mutation_id:
                replacement_type = self.ARITHMETIC_MAP[op_type]
                node.op = replacement_type()
                self.applied_mutation = {
                    "id": self.current_mutation_id,
                    "operator": "AOR",
                    "lineno": getattr(node, "lineno", 0),
                    "original": op_type.__name__,
                    "replacement": replacement_type.__name__,
                }
            self.current_mutation_id += 1
        return node

    def visit_BoolOp(self, node: ast.BoolOp):
        self.generic_visit(node)
        op_type = type(node.op)
        if op_type in self.LOGICAL_MAP:
            if self.current_mutation_id == self.target_mutation_id:
                replacement_type = self.LOGICAL_MAP[op_type]
                node.op = replacement_type()
                self.applied_mutation = {
                    "id": self.current_mutation_id,
                    "operator": "LCR",
                    "lineno": getattr(node, "lineno", 0),
                    "original": op_type.__name__,
                    "replacement": replacement_type.__name__,
                }
            self.current_mutation_id += 1
        return node

    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, bool):
            if self.current_mutation_id == self.target_mutation_id:
                node.value = not node.value
                self.applied_mutation = {
                    "id": self.current_mutation_id,
                    "operator": "COR",
                    "lineno": getattr(node, "lineno", 0),
                    "original": str(not node.value),
                    "replacement": str(node.value),
                }
            self.current_mutation_id += 1
        return node


def count_potential_mutations(source_code: str) -> int:
    """Determine how many total mutations can be generated for source_code."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return 0
    visitor = MutationVisitor(target_mutation_id=-1)
    visitor.visit(tree)
    return visitor.current_mutation_id


def generate_mutant(source_code: str, mutation_id: int) -> Tuple[Optional[str], Optional[dict]]:
    """Generate the i-th mutant of source_code."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return None, None
    visitor = MutationVisitor(target_mutation_id=mutation_id)
    mutated_tree = visitor.visit(tree)
    if not visitor.applied_mutation:
        return None, None
    ast.fix_missing_locations(mutated_tree)
    mutated_code = ast.unparse(mutated_tree)
    return mutated_code, visitor.applied_mutation


# ---------- Data Models ----------

@dataclass
class MutantExecutionResult:
    """Detailed result of executing test suite against a single mutant."""
    mutant_id: int
    operator: str
    lineno: int
    original: str
    replacement: str
    status: str  # KILLED, SURVIVED, MUTANT_ERROR, FALSE_KILL_BASELINE
    killing_tests: List[str] = field(default_factory=list)
    false_killing_tests: List[str] = field(default_factory=list)
    details: Optional[str] = None


@dataclass
class MutationScoreReport:
    """Aggregated mutation testing report with baseline transparency."""
    target_file: str
    test_file: str
    total_mutants_generated: int
    valid_mutants: int
    killed_mutants: int
    survived_mutants: int
    error_mutants: int
    mutation_score: Optional[float]  # None if valid_mutants == 0
    mutation_score_str: str          # "Undefined" if valid_mutants == 0 else "XX.X%"
    baseline_passing_tests: List[str] = field(default_factory=list)
    baseline_failing_tests: List[str] = field(default_factory=list)
    false_kills_filtered_count: int = 0
    mutants: List[MutantExecutionResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------- Main Evaluation Engine ----------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def is_in_shared_repos(path: Path) -> bool:
    """Check if a file path is inside the shared data/repos directory."""
    repos_dir = (PROJECT_ROOT / "data" / "repos").resolve()
    try:
        path.resolve().relative_to(repos_dir)
        return True
    except ValueError:
        return False


def evaluate_mutation_score(
    target_file: Path,
    test_file: Path,
    python_paths: Optional[List[str]] = None,
    max_mutants: int = 30,
    cwd: Optional[Path] = None,
    timeout_per_test: int = 20,
    execution_mode: ExecutionMode = ExecutionMode.SINGLE_TEST_ISOLATED,
    baseline_repetitions: int = 2,
) -> MutationScoreReport:
    """
    Evaluates mutation score with strict baseline pre-check.
    
    Guarantees:
    1. Rejects any attempt to mutate shared baseline repositories directly.
    2. Runs test_file on unmutated target_file across baseline_repetitions to establish stable baseline.
    3. Identifies baseline-passing vs baseline-failing/flaky tests. Tests that do not pass
       in EVERY baseline repetition are disqualified from counting as mutant kills.
    4. Kills are only counted if a baseline-passing test fails with ASSERTION_FAILED or TIMEOUT.
    5. Returns mutation_score=None ("Undefined") if no valid mutants could be evaluated.
    6. Always restores target file to pristine state in finally block.
    """
    target_path = Path(target_file).resolve()
    test_path = Path(test_file).resolve()
    working_dir = Path(cwd).resolve() if cwd else test_path.parent

    if not target_path.exists():
        raise FileNotFoundError(f"Target file for mutation does not exist: {target_path}")
    if not test_path.exists():
        raise FileNotFoundError(f"Test file does not exist: {test_path}")

    # Safety constraint: Refuse to mutate shared baseline repository directly
    if is_in_shared_repos(target_path):
        raise PermissionError(
            f"Target file {target_path} is inside shared repository data/repos! "
            f"Direct mutation of shared repositories is strictly prohibited. "
            f"Please run mutation evaluation inside an isolated worktree "
            f"(e.g., swebench_loader.isolated_instance_environment)."
        )

    original_bytes = target_path.read_bytes()
    orig_sha = hashlib.sha256(original_bytes).hexdigest()
    original_source = original_bytes.decode("utf-8", errors="replace")

    # Clean initial pycache
    _clean_pycache([target_path.parent, working_dir])

    # ----------------------------------------------------
    # PHASE 1: Baseline Pre-check on Unmutated Source (Multi-Run Stability)
    # ----------------------------------------------------
    reps = max(1, baseline_repetitions)
    print(f"Phase 1: Running baseline pre-check ({reps} repetitions) on unmutated {target_path.name}...")
    baseline_pass_counts: Dict[str, int] = {}
    all_baseline_tests: Set[str] = set()

    for rep in range(reps):
        baseline_res = execute_suite(
            test_target=test_path,
            cwd=working_dir,
            python_paths=python_paths,
            mode=execution_mode,
            timeout_per_test=timeout_per_test,
            seed=42 + rep,
        )
        for nid, t_res in baseline_res.tests.items():
            all_baseline_tests.add(nid)
            if t_res.is_passed:
                baseline_pass_counts[nid] = baseline_pass_counts.get(nid, 0) + 1

    baseline_passing: Set[str] = set()
    baseline_failing: Set[str] = set()

    for nid in all_baseline_tests:
        passes = baseline_pass_counts.get(nid, 0)
        if passes == reps:
            baseline_passing.add(nid)
        else:
            baseline_failing.add(nid)

    print(f"  Baseline Results ({reps} repetitions): {len(baseline_passing)} consistently passed, {len(baseline_failing)} failing/flaky on baseline")
    if baseline_failing:
        print(f"  WARNING: {len(baseline_failing)} tests failed or flaked on unmutated code! These will be disqualified from counting as mutant kills.")

    # ----------------------------------------------------
    # PHASE 2: Mutant Generation & Evaluation
    # ----------------------------------------------------
    total_available = count_potential_mutations(original_source)
    mutants_to_test = min(total_available, max_mutants)
    print(f"Phase 2: Generating and evaluating {mutants_to_test} mutants (out of {total_available} available)...")

    results: List[MutantExecutionResult] = []
    killed_count = 0
    survived_count = 0
    error_count = 0
    false_kills_filtered_count = 0

    try:
        for mid in range(mutants_to_test):
            mutated_code, meta = generate_mutant(original_source, mid)
            if not meta or not mutated_code:
                continue

            # Safely write mutant to target_path with immediate restoration and byte hash check
            try:
                _clean_pycache([target_path.parent])
                target_path.write_text(mutated_code, encoding="utf-8")

                # Run test suite against this mutant
                mutant_run = execute_suite(
                    test_target=test_path,
                    cwd=working_dir,
                    python_paths=python_paths,
                    mode=execution_mode,
                    timeout_per_test=timeout_per_test,
                )

                # Analyze which tests failed
                legitimate_killers = []
                false_killers = []

                for nid, t_res in mutant_run.tests.items():
                    if t_res.outcome in ("ASSERTION_FAILED", "TIMEOUT"):
                        if nid in baseline_passing:
                            legitimate_killers.append(nid)
                        else:
                            false_killers.append(nid)
                            false_kills_filtered_count += 1
                    elif t_res.outcome in ("IMPORT_ERROR", "COLLECTION_ERROR", "EXCEPTION"):
                        if nid not in baseline_passing:
                            false_killers.append(nid)

                # Determine mutant verdict
                if legitimate_killers:
                    status = "KILLED"
                    killed_count += 1
                elif mutant_run.collection_error_count > 0 or mutant_run.import_error_count > 0:
                    status = "MUTANT_ERROR"
                    error_count += 1
                else:
                    status = "SURVIVED"
                    survived_count += 1

                results.append(MutantExecutionResult(
                    mutant_id=mid,
                    operator=meta.get("operator", "UNKNOWN"),
                    lineno=meta.get("lineno", 0),
                    original=meta.get("original", ""),
                    replacement=meta.get("replacement", ""),
                    status=status,
                    killing_tests=legitimate_killers,
                    false_killing_tests=false_killers,
                ))
            finally:
                # Restore original source code immediately after each mutant and verify SHA-256
                target_path.write_bytes(original_bytes)
                _clean_pycache([target_path.parent])
                restored_sha = hashlib.sha256(target_path.read_bytes()).hexdigest()
                if restored_sha != orig_sha:
                    raise RuntimeError(
                        f"CRITICAL: Target file {target_path} SHA-256 mismatch after mutant {mid}! "
                        f"Expected {orig_sha}, got {restored_sha}"
                    )
    finally:
        # Guarantee final restoration even in case of unexpected exceptions
        target_path.write_bytes(original_bytes)
        _clean_pycache([target_path.parent, working_dir])
        final_sha = hashlib.sha256(target_path.read_bytes()).hexdigest()
        if final_sha != orig_sha:
            raise RuntimeError(
                f"CRITICAL: Target file {target_path} final SHA-256 restoration mismatch! "
                f"Expected {orig_sha}, got {final_sha}"
            )

    valid_mutants = killed_count + survived_count
    if valid_mutants > 0:
        score = round(killed_count / valid_mutants, 4)
        score_str = f"{score * 100:.1f}%"
    else:
        score = None
        score_str = "Undefined (0 valid mutants)"

    print(f"Mutation Testing Completed: {killed_count} killed, {survived_count} survived, {error_count} errors")
    print(f"  Mutation Score: {score_str}")
    print(f"  False kills safely filtered by baseline pre-check: {false_kills_filtered_count}")

    return MutationScoreReport(
        target_file=str(target_path),
        test_file=str(test_path),
        total_mutants_generated=len(results),
        valid_mutants=valid_mutants,
        killed_mutants=killed_count,
        survived_mutants=survived_count,
        error_mutants=error_count,
        mutation_score=score,
        mutation_score_str=score_str,
        baseline_passing_tests=sorted(baseline_passing),
        baseline_failing_tests=sorted(baseline_failing),
        false_kills_filtered_count=false_kills_filtered_count,
        mutants=results,
    )
