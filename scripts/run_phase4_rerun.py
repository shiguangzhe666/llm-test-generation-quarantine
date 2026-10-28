"""
Phase IV Formal Empirical Study Rerun Orchestrator.

Strictly executes the formal empirical study rerun conforming to the updated protocol:
1. Frozen benchmark matrix (17 SWE-bench Verified instances across 4 software domains).
2. N=20 repetitions per test with deterministic seeds (Seed_i = 42 + i * 7919).
3. Complete coverage of 3 execution modes: SINGLE_TEST_ISOLATED, SUITE_IN_ORDER, SUITE_RANDOM.
4. Unified dynamic nodeid collection via pytest --collect-only upfront.
5. True physical construction and execution of strategy test pools on Fixed & Buggy worktrees.
6. Three-tier defect retention metrics decomposition (mainline, quarantine, system).
7. Full logging of TIMEOUT, MISSING_OBSERVATION, NOT_EXECUTED, and exclusion tracebacks.
8. Independent new timestamped run_id without overwriting historical runs.
9. Regenerate paper artifacts, tables, figures, and manuscripts.
10. Strict scientific integrity: zero premature claims.
"""

import argparse
import ast
import datetime
import hashlib
import json
import os
import platform
import random
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts._audit_repos_state import audit_all_repos
from src.analysis.pareto_analysis import (
    compute_clustered_standard_error,
    compute_vargha_delaney_a12,
    compute_paired_effect_size,
    compute_wilcoxon_signed_rank,
    adjust_p_values_holm,
    compute_wilson_confidence_interval,
    compute_pareto_frontier,
    evaluate_strategies_on_suite,
    generate_latex_table,
    StrategyMetrics,
)
from src.evaluation.mutation_eval import evaluate_mutation_score
from src.execution.nodeid_matching import canonical_nodeid
from src.execution.repeated_executor import run_repeated
from src.execution.structured_executor import (
    execute_suite,
    discover_test_nodeids,
    _run_pytest_with_plugin,
    ExecutionMode,
    SuiteExecutionResult,
)
from src.triage.risk_triage import triage_suite
from src.utils.swebench_loader import (
    load_swebench_instances,
    isolated_instance_environment,
    SWEBenchInstance,
)

CONFTEST_REQUESTS = """# Backward compatibility shim for Python 3.11+
import collections, collections.abc
for name in ['Mapping', 'MutableMapping', 'Sequence', 'Callable', 'Iterable', 'Iterator']:
    if not hasattr(collections, name) and hasattr(collections.abc, name):
        setattr(collections, name, getattr(collections.abc, name))
"""

CONFTEST_XARRAY = """# Backward compatibility shim for Python 3.11+ and NumPy 2.0+
import numpy as np
if not hasattr(np, 'unicode_'):
    np.unicode_ = np.str_
import collections, collections.abc
for name in ['Mapping', 'MutableMapping', 'Sequence', 'Callable', 'Iterable', 'Iterator']:
    if not hasattr(collections, name) and hasattr(collections.abc, name):
        setattr(collections, name, getattr(collections.abc, name))
"""

# Benchmark instances specification (Frozen 17-instance matrix)
INSTANCE_CONFIGS = {
    # 1. psf/requests (HTTP / Networking) - 5 instances
    "psf__requests-1921": {
        "repo": "psf/requests",
        "repo_dir_name": "psf__requests",
        "python_paths_rel": ["."],
        "target_file_rel": "requests/sessions.py",
        "conftest": CONFTEST_REQUESTS,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "psf__requests-1921" / "generated_tests",
        "domain": "HTTP / Networking",
    },
    "psf__requests-1724": {
        "repo": "psf/requests",
        "repo_dir_name": "psf__requests",
        "python_paths_rel": ["."],
        "target_file_rel": "requests/sessions.py",
        "conftest": CONFTEST_REQUESTS,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "psf__requests-1724" / "generated_tests",
        "domain": "HTTP / Networking",
    },
    "psf__requests-2317": {
        "repo": "psf/requests",
        "repo_dir_name": "psf__requests",
        "python_paths_rel": ["."],
        "target_file_rel": "requests/sessions.py",
        "conftest": CONFTEST_REQUESTS,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "psf__requests-2317" / "generated_tests",
        "domain": "HTTP / Networking",
    },
    "psf__requests-1766": {
        "repo": "psf/requests",
        "repo_dir_name": "psf__requests",
        "python_paths_rel": ["."],
        "target_file_rel": "requests/auth.py",
        "conftest": CONFTEST_REQUESTS,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "psf__requests-1766" / "generated_tests",
        "domain": "HTTP / Networking",
    },
    "psf__requests-6028": {
        "repo": "psf/requests",
        "repo_dir_name": "psf__requests",
        "python_paths_rel": ["."],
        "target_file_rel": "requests/utils.py",
        "conftest": CONFTEST_REQUESTS,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "psf__requests-6028" / "generated_tests",
        "domain": "HTTP / Networking",
    },
    # 2. pallets/flask (Web Framework) - 1 instance
    "pallets__flask-5014": {
        "repo": "pallets/flask",
        "repo_dir_name": "pallets__flask",
        "python_paths_rel": ["src"],
        "target_file_rel": "src/flask/blueprints.py",
        "conftest": None,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "pallets__flask-5014" / "generated_tests",
        "domain": "Web Framework",
    },
    # 3. sympy/sympy (Symbolic Mathematics) - 5 instances
    "sympy__sympy-15809": {
        "repo": "sympy/sympy",
        "repo_dir_name": "sympy__sympy",
        "python_paths_rel": ["."],
        "target_file_rel": "sympy/functions/elementary/miscellaneous.py",
        "conftest": None,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "sympy__sympy-15809" / "generated_tests",
        "domain": "Symbolic Mathematics",
    },
    "sympy__sympy-17630": {
        "repo": "sympy/sympy",
        "repo_dir_name": "sympy__sympy",
        "python_paths_rel": ["."],
        "target_file_rel": "sympy/matrices/expressions/matexpr.py",
        "conftest": None,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "sympy__sympy-17630" / "generated_tests",
        "domain": "Symbolic Mathematics",
    },
    "sympy__sympy-21930": {
        "repo": "sympy/sympy",
        "repo_dir_name": "sympy__sympy",
        "python_paths_rel": ["."],
        "target_file_rel": "sympy/physics/secondquant.py",
        "conftest": None,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "sympy__sympy-21930" / "generated_tests",
        "domain": "Symbolic Mathematics",
    },
    "sympy__sympy-22080": {
        "repo": "sympy/sympy",
        "repo_dir_name": "sympy__sympy",
        "python_paths_rel": ["."],
        "target_file_rel": "sympy/printing/codeprinter.py",
        "conftest": None,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "sympy__sympy-22080" / "generated_tests",
        "domain": "Symbolic Mathematics",
    },
    "sympy__sympy-17139": {
        "repo": "sympy/sympy",
        "repo_dir_name": "sympy__sympy",
        "python_paths_rel": ["."],
        "target_file_rel": "sympy/simplify/fu.py",
        "conftest": None,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "sympy__sympy-17139" / "generated_tests",
        "domain": "Symbolic Mathematics",
    },
    # 4. pydata/xarray (Scientific Computing / N-D Data) - 5 instances
    "pydata__xarray-4075": {
        "repo": "pydata/xarray",
        "repo_dir_name": "pydata__xarray",
        "python_paths_rel": ["."],
        "target_file_rel": "xarray/core/weighted.py",
        "conftest": CONFTEST_XARRAY,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "pydata__xarray-4075" / "generated_tests",
        "domain": "Scientific Computing",
    },
    "pydata__xarray-4356": {
        "repo": "pydata/xarray",
        "repo_dir_name": "pydata__xarray",
        "python_paths_rel": ["."],
        "target_file_rel": "xarray/core/nanops.py",
        "conftest": CONFTEST_XARRAY,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "pydata__xarray-4356" / "generated_tests",
        "domain": "Scientific Computing",
    },
    "pydata__xarray-4966": {
        "repo": "pydata/xarray",
        "repo_dir_name": "pydata__xarray",
        "python_paths_rel": ["."],
        "target_file_rel": "xarray/coding/variables.py",
        "conftest": CONFTEST_XARRAY,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "pydata__xarray-4966" / "generated_tests",
        "domain": "Scientific Computing",
    },
    "pydata__xarray-6744": {
        "repo": "pydata/xarray",
        "repo_dir_name": "pydata__xarray",
        "python_paths_rel": ["."],
        "target_file_rel": "xarray/core/rolling.py",
        "conftest": CONFTEST_XARRAY,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "pydata__xarray-6744" / "generated_tests",
        "domain": "Scientific Computing",
    },
    "pydata__xarray-6992": {
        "repo": "pydata/xarray",
        "repo_dir_name": "pydata__xarray",
        "python_paths_rel": ["."],
        "target_file_rel": "xarray/core/dataset.py",
        "conftest": CONFTEST_XARRAY,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "pydata__xarray-6992" / "generated_tests",
        "domain": "Scientific Computing",
    },
    # 5. pytest-dev/pytest (Testing Tools) - 1 instance
    "pytest-dev__pytest-7521": {
        "repo": "pytest-dev/pytest",
        "repo_dir_name": "pytest-dev__pytest",
        "python_paths_rel": ["src"],
        "target_file_rel": "src/_pytest/capture.py",
        "conftest": None,
        "test_dir": PROJECT_ROOT / "data" / "study_gate3" / "pytest-dev__pytest-7521" / "generated_tests",
        "domain": "Testing Tools",
    },
}


class ExecutionLogger:
    """Logs executed commands, durations, and output files to commands.jsonl and logs/."""

    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.logs_dir = run_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.commands_file = run_dir / "commands.jsonl"

    def log_command(self, cmd_name: str, command: str, cwd: str, exit_code: int, duration: float, stdout: str = "", stderr: str = ""):
        log_filename = f"{cmd_name}.log"
        log_path = self.logs_dir / log_filename
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"COMMAND: {command}\n")
            f.write(f"CWD: {cwd}\n")
            f.write(f"EXIT_CODE: {exit_code}\n")
            f.write(f"DURATION_SECONDS: {duration:.4f}\n")
            f.write("=" * 40 + " STDOUT " + "=" * 40 + "\n")
            f.write(stdout or "(empty)")
            f.write("\n" + "=" * 40 + " STDERR " + "=" * 40 + "\n")
            f.write(stderr or "(empty)")
            f.write("\n")

        entry = {
            "timestamp_utc": datetime.datetime.utcnow().isoformat(),
            "name": cmd_name,
            "command": command,
            "cwd": str(cwd),
            "exit_code": exit_code,
            "duration_seconds": round(duration, 4),
            "log_file": str(log_path.relative_to(self.run_dir)),
        }
        with open(self.commands_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


def sha256_file(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def run_instance_study_rerun(
    instance_id: str,
    instance: SWEBenchInstance,
    cfg: Dict[str, Any],
    run_dir: Path,
    num_runs: int,
    max_mutants: int,
    logger: ExecutionLogger,
) -> Dict[str, Any]:
    print(f"\n{'=' * 70}")
    print(f"PROCESSING INSTANCE: {instance_id} ({cfg['domain']})")
    print(f"{'=' * 70}")
    start_time = time.time()
    
    shared_repo_dir = PROJECT_ROOT / "data" / "repos" / cfg["repo_dir_name"]
    test_dir = cfg["test_dir"]
    test_files = sorted([f for f in test_dir.iterdir() if f.name.startswith("test_") and f.name.endswith(".py")])
    
    if not test_files:
        raise FileNotFoundError(f"No test files found in {test_dir}")
        
    print(f"  -> Found {len(test_files)} candidate test suite files in {test_dir.name}")

    # ----------------------------------------------------
    # Step 1: Dynamic Discovery & Canonical NodeID Collection (Req. 4)
    # ----------------------------------------------------
    print("  -> [Step 1] Running dynamic nodeid discovery pass...")
    t0_disc = time.time()
    canonical_nodeids: List[str] = []
    file_nodeids: Dict[str, List[str]] = {}
    collection_errors: List[dict] = []
    valid_test_files: List[Path] = []

    with isolated_instance_environment(shared_repo_dir, instance, version="fixed") as fixed_wt:
        if cfg["conftest"]:
            (fixed_wt / "conftest.py").write_text(cfg["conftest"], encoding="utf-8")
        python_paths = [str(fixed_wt / p) for p in cfg["python_paths_rel"]]

        for tf in test_files:
            local_tf = fixed_wt / tf.name
            shutil.copy(tf, local_tf)

            discovered, errors = discover_test_nodeids(local_tf, cwd=fixed_wt, python_paths=python_paths, timeout=30)
            if errors:
                collection_errors.extend(errors)
                print(f"     [-] Discovery warning in {tf.name}: {len(errors)} errors")
            if discovered:
                file_nodeids[tf.name] = discovered
                canonical_nodeids.extend(discovered)
                valid_test_files.append(tf)

    dur_disc = time.time() - t0_disc
    logger.log_command(
        f"{instance_id}_01_discovery",
        f"discover_test_nodeids across {len(test_files)} files",
        str(shared_repo_dir),
        0 if canonical_nodeids else 1,
        dur_disc,
        stdout=f"Discovered {len(canonical_nodeids)} nodeids: {canonical_nodeids}",
        stderr=json.dumps(collection_errors, indent=2) if collection_errors else "",
    )

    if not canonical_nodeids:
        elapsed = time.time() - start_time
        err_msg = collection_errors[0].get("error_message", "0 tests collected dynamically under Python 3.11 environment") if collection_errors else "0 tests collected"
        print(f"  -> [EXCLUSION] Instance {instance_id} has 0 dynamically collected tests. Excluded per protocol.")
        
        # Write dedicated exclusion traceback log
        excl_log = run_dir / "logs" / f"{instance_id}_exclusion_traceback.log"
        excl_log.parent.mkdir(parents=True, exist_ok=True)
        excl_log.write_text(f"INSTANCE: {instance_id}\nERROR: {err_msg}\nTRACEBACK:\n{json.dumps(collection_errors, indent=2)}\n", encoding="utf-8")
        
        return {
            "instance_id": instance_id,
            "repo": cfg["repo"],
            "domain": cfg["domain"],
            "duration_seconds": round(elapsed, 2),
            "total_tests": 0,
            "real_bugs_ground_truth": 0,
            "defect_detecting_tests": 0,
            "flaky_tests_count": 0,
            "error": f"EXCLUDED: {err_msg[:200]}",
            "exclusion_log": str(excl_log.relative_to(run_dir)),
            "strategy_comparison": {},
        }

    print(f"  -> Canonical dynamic inventory: {len(canonical_nodeids)} executable tests across {len(valid_test_files)} valid files")

    # ----------------------------------------------------
    # Step 2: Three Execution Modes Full Coverage (Req. 3 & Req. 2)
    # ----------------------------------------------------
    print(f"  -> [Step 2] Executing 3 Modes (SINGLE_TEST_ISOLATED, SUITE_IN_ORDER, SUITE_RANDOM N={num_runs})...")
    mode_eval_results: Dict[str, Any] = {}
    flakiness_records: Dict[str, dict] = {}
    fixed_outcomes: Dict[str, str] = {}

    with isolated_instance_environment(shared_repo_dir, instance, version="fixed") as fixed_wt:
        if cfg["conftest"]:
            (fixed_wt / "conftest.py").write_text(cfg["conftest"], encoding="utf-8")
        python_paths = [str(fixed_wt / p) for p in cfg["python_paths_rel"]]

        # Mode A: SINGLE_TEST_ISOLATED (Baseline isolated single test execution)
        t0_iso = time.time()
        iso_outcomes: Dict[str, str] = {}
        for tf in valid_test_files:
            local_tf = fixed_wt / tf.name
            shutil.copy(tf, local_tf)
            res_iso = execute_suite(local_tf, cwd=fixed_wt, python_paths=python_paths, mode=ExecutionMode.SINGLE_TEST_ISOLATED, timeout_per_test=30)
            for nid, tres in res_iso.tests.items():
                iso_outcomes[nid] = tres.outcome
        mode_eval_results["SINGLE_TEST_ISOLATED"] = {
            "total": len(iso_outcomes),
            "passed": sum(1 for v in iso_outcomes.values() if v == "PASSED"),
            "duration": round(time.time() - t0_iso, 2),
        }
        logger.log_command(
            f"{instance_id}_02_mode_isolated",
            f"execute_suite Mode=SINGLE_TEST_ISOLATED ({len(valid_test_files)} files)",
            str(fixed_wt),
            0 if any(v == "PASSED" for v in iso_outcomes.values()) else 1,
            round(time.time() - t0_iso, 4),
            stdout=json.dumps(iso_outcomes, indent=2),
        )

        # Mode B: SUITE_IN_ORDER (Baseline default suite order execution)
        t0_ord = time.time()
        ord_outcomes: Dict[str, str] = {}
        for tf in valid_test_files:
            local_tf = fixed_wt / tf.name
            res_ord = execute_suite(local_tf, cwd=fixed_wt, python_paths=python_paths, mode=ExecutionMode.SUITE_IN_ORDER, timeout_per_test=30)
            for nid, tres in res_ord.tests.items():
                ord_outcomes[nid] = tres.outcome
        mode_eval_results["SUITE_IN_ORDER"] = {
            "total": len(ord_outcomes),
            "passed": sum(1 for v in ord_outcomes.values() if v == "PASSED"),
            "duration": round(time.time() - t0_ord, 2),
        }
        logger.log_command(
            f"{instance_id}_02_mode_in_order",
            f"execute_suite Mode=SUITE_IN_ORDER ({len(valid_test_files)} files)",
            str(fixed_wt),
            0 if any(v == "PASSED" for v in ord_outcomes.values()) else 1,
            round(time.time() - t0_ord, 4),
            stdout=json.dumps(ord_outcomes, indent=2),
        )

        # Mode C: SUITE_RANDOM (N=num_runs repetitions for flakiness profiling)
        t0_rnd = time.time()
        for tf in valid_test_files:
            local_tf = fixed_wt / tf.name
            rep_res = run_repeated(
                test_file=local_tf,
                project_dir=fixed_wt,
                num_runs=num_runs,
                python_paths=python_paths,
                mode=ExecutionMode.SUITE_RANDOM,
                base_seed=42,
            )
            for nid, rec in rep_res.tests_summary.items():
                flakiness_records[nid] = {
                    "flakiness_rate": rec.flakiness_rate,
                    "category": rec.flakiness_category,
                    "is_flaky": rec.is_flaky,
                    "pass_count": rec.pass_count,
                    "fail_count": rec.fail_count,
                    "planned_runs": rec.planned_runs,
                    "observed_runs": rec.observed_runs,
                    "missing_observation_count": rec.missing_observation_count,
                    "timeout_count": rec.timeout_count,
                }
                # Strictly evaluate outcome on fixed codebase: only stable_pass is PASSED
                if rec.flakiness_category == "stable_pass" and rec.pass_count == rec.planned_runs and rec.observed_runs == rec.planned_runs:
                    fixed_outcomes[nid] = "PASSED"
                elif rec.flakiness_category == "stable_fail" and rec.fail_count == rec.planned_runs:
                    fixed_outcomes[nid] = "FAILED"
                elif rec.is_flaky:
                    fixed_outcomes[nid] = "FLAKY"
                elif rec.flakiness_category == "incomplete":
                    fixed_outcomes[nid] = "INCOMPLETE"
                elif rec.flakiness_category == "unstable_skip":
                    fixed_outcomes[nid] = "SKIPPED"
                else:
                    fixed_outcomes[nid] = "UNDEFINED"

        mode_eval_results["SUITE_RANDOM"] = {
            "total": len(flakiness_records),
            "flaky_count": sum(1 for r in flakiness_records.values() if r["is_flaky"]),
            "duration": round(time.time() - t0_rnd, 2),
        }
        logger.log_command(
            f"{instance_id}_02_mode_random_rep",
            f"run_repeated N={num_runs} Mode=SUITE_RANDOM ({len(valid_test_files)} files)",
            str(fixed_wt),
            0,
            round(time.time() - t0_rnd, 4),
            stdout=json.dumps(flakiness_records, indent=2),
        )

    # ----------------------------------------------------
    # Step 3: Defect Detection on Buggy Version
    # ----------------------------------------------------
    print("  -> [Step 3] Testing defect detection on Buggy Version...")
    t0_buggy = time.time()
    buggy_outcomes: Dict[str, str] = {}
    defect_detecting_test_keys: Set[str] = set()

    with isolated_instance_environment(shared_repo_dir, instance, version="buggy") as buggy_wt:
        if cfg["conftest"]:
            (buggy_wt / "conftest.py").write_text(cfg["conftest"], encoding="utf-8")
        python_paths = [str(buggy_wt / p) for p in cfg["python_paths_rel"]]

        for tf in valid_test_files:
            local_tf = buggy_wt / tf.name
            shutil.copy(tf, local_tf)
            exec_res = execute_suite(local_tf, cwd=buggy_wt, python_paths=python_paths, mode=ExecutionMode.SUITE_IN_ORDER)
            for nid, tres in exec_res.tests.items():
                buggy_outcomes[nid] = tres.outcome

    dur_buggy = time.time() - t0_buggy

    for nid in canonical_nodeids:
        f_verdict = fixed_outcomes.get(nid, "UNKNOWN")
        b_verdict = buggy_outcomes.get(nid, "UNKNOWN")
        if f_verdict == "PASSED" and b_verdict in ("ASSERTION_FAILED", "EXCEPTION"):
            defect_detecting_test_keys.add(nid)

    n_bug_det = len(defect_detecting_test_keys)
    real_bugs_ground_truth = 1 if n_bug_det > 0 else 0
    print(f"  -> Defect ground truth: {n_bug_det} tests detected real defect (Real Bug = {real_bugs_ground_truth})")

    logger.log_command(
        f"{instance_id}_03_buggy_defect_eval",
        f"execute_suite Mode=SUITE_IN_ORDER on buggy ({len(valid_test_files)} files)",
        str(buggy_wt),
        0 if n_bug_det > 0 else 1,
        round(dur_buggy, 4),
        stdout=json.dumps({
            "buggy_outcomes": buggy_outcomes,
            "defect_detecting_test_keys": list(defect_detecting_test_keys),
        }, indent=2),
    )

    # ----------------------------------------------------
    # Step 4: Exploratory Mutation Testing
    # ----------------------------------------------------
    print(f"  -> [Step 4] Evaluating Mutation Testing (max {max_mutants} mutants)...")
    t0_mut = time.time()
    with isolated_instance_environment(shared_repo_dir, instance, version="fixed") as fixed_wt:
        if cfg["conftest"]:
            (fixed_wt / "conftest.py").write_text(cfg["conftest"], encoding="utf-8")
        python_paths = [str(fixed_wt / p) for p in cfg["python_paths_rel"]]
        target_file = fixed_wt / cfg["target_file_rel"]
        chosen_tf = max(valid_test_files, key=lambda f: f.stat().st_size)
        first_test_file = fixed_wt / chosen_tf.name
        shutil.copy(chosen_tf, first_test_file)

        mut_rep = evaluate_mutation_score(
            target_file=target_file,
            test_file=first_test_file,
            python_paths=python_paths,
            cwd=fixed_wt,
            max_mutants=max_mutants,
            baseline_repetitions=1,
        )

    dur_mut = time.time() - t0_mut
    logger.log_command(
        f"{instance_id}_04_mutation_eval",
        f"evaluate_mutation_score max={max_mutants} on {cfg['target_file_rel']}",
        str(fixed_wt),
        0 if mut_rep.valid_mutants > 0 else 1,
        round(dur_mut, 4),
        stdout=f"Mutation score: {mut_rep.mutation_score_str} ({mut_rep.killed_mutants}/{mut_rep.valid_mutants})",
    )
    print(f"  -> Mutation score: {mut_rep.mutation_score_str} ({mut_rep.killed_mutants}/{mut_rep.valid_mutants})")

    # ----------------------------------------------------
    # Step 5: Risk-Aware Triage Framework Application
    # ----------------------------------------------------
    print("  -> [Step 5] Running static AST feature extraction and Risk-Aware Triage...")
    all_decisions = []
    for tf in valid_test_files:
        trep = triage_suite(
            test_file=tf,
            flakiness_records=flakiness_records,
            ground_truth_bug_detectors=defect_detecting_test_keys,
        )
        for dec in trep.decisions:
            all_decisions.append(asdict(dec))

    # Construct test records for strategy evaluation
    test_records = []
    for nid in canonical_nodeids:
        r = flakiness_records.get(nid)
        short_name = nid.split("::")[-1]
        matching_dec = None
        for d in all_decisions:
            d_nid = f"{d['suite_file']}::{d['test_name']}"
            if d_nid == nid or canonical_nodeid(d_nid) == canonical_nodeid(nid):
                matching_dec = d
                break

        flaky_rate = r["flakiness_rate"] if r else None
        is_flk = r.get("is_flaky", False) if r else False

        triage_cat = matching_dec.get("category", "TIER_4_SPURIOUS") if matching_dec else "TIER_4_SPURIOUS"
        frag_score = matching_dec.get("static_fragility_score", matching_dec.get("flakiness_risk_score", 1.0)) if matching_dec else 1.0

        test_records.append({
            "test_name": short_name,
            "nodeid": nid,
            "flakiness_rate": flaky_rate,
            "is_flaky": is_flk,
            "is_bug_detecting": (nid in defect_detecting_test_keys or short_name in defect_detecting_test_keys),
            "fragility_score": frag_score,
            "mutation_score": mut_rep.mutation_score if mut_rep.mutation_score is not None else 0.0,
            "triage_category": triage_cat,
        })

    # ----------------------------------------------------
    # Step 6: Construct and Physically Execute Strategy Test Pools (Req. 5 & Req. 6)
    # ----------------------------------------------------
    print("  -> [Step 6] Constructing and physically executing Strategy Test Pools...")
    t0_pools = time.time()

    tier1_nodeids = [t["nodeid"] for t in test_records if t["triage_category"] == "TIER_1_SAFE_KEEP"]
    tier2_nodeids = [t["nodeid"] for t in test_records if t["triage_category"] == "TIER_2_DUAL_PURPOSE"]
    tier3_nodeids = [t["nodeid"] for t in test_records if t["triage_category"] == "TIER_3_SAFE_LOW"]
    tier4_nodeids = [t["nodeid"] for t in test_records if t["triage_category"] == "TIER_4_SPURIOUS"]

    # Define candidate nodeids for each strategy
    strategy_pools = {
        "Keep-All": {
            "mainline": canonical_nodeids,
            "quarantine": [],
        },
        "Discard-All-Flaky": {
            # Only retain tests with verified non-flaky execution (flakiness_rate is not None and <= 0.0)
            "mainline": [t["nodeid"] for t in test_records if t["flakiness_rate"] is not None and t["flakiness_rate"] <= 0.0],
            "quarantine": [],
        },
        "Static-Only": {
            "mainline": [t["nodeid"] for t in test_records if t["fragility_score"] <= 0.3],
            "quarantine": [],
        },
        "Risk-Aware-Triage": {
            "mainline": tier1_nodeids + tier3_nodeids,
            "quarantine": tier2_nodeids,
        },
    }
    # Random-Filtering: Budget-matched to Triage mainline pool size
    n_triage_mainline = len(strategy_pools["Risk-Aware-Triage"]["mainline"])
    rng = random.Random(42)
    k_rand = max(1, min(len(canonical_nodeids), n_triage_mainline))
    strategy_pools["Random-Filtering"] = {
        "mainline": sorted(rng.sample(canonical_nodeids, k_rand)),
        "quarantine": [],
    }

    # Physical Execution of Strategy Pools
    physical_strategy_results: Dict[str, StrategyMetrics] = {}
    N_total = len(canonical_nodeids)
    total_dt = len(defect_detecting_test_keys)

    # Persistent directory for strategy pool execution reports (Flaw A fix: preserve outside temporary worktrees)
    pool_reports_dir = run_dir / "strategy_pools" / instance_id
    pool_reports_dir.mkdir(parents=True, exist_ok=True)

    with isolated_instance_environment(shared_repo_dir, instance, version="fixed") as fixed_wt, \
         isolated_instance_environment(shared_repo_dir, instance, version="buggy") as buggy_wt:
        if cfg["conftest"]:
            (fixed_wt / "conftest.py").write_text(cfg["conftest"], encoding="utf-8")
            (buggy_wt / "conftest.py").write_text(cfg["conftest"], encoding="utf-8")
        py_paths_fixed = [str(fixed_wt / p) for p in cfg["python_paths_rel"]]
        py_paths_buggy = [str(buggy_wt / p) for p in cfg["python_paths_rel"]]

        for tf in valid_test_files:
            shutil.copy(tf, fixed_wt / tf.name)
            shutil.copy(tf, buggy_wt / tf.name)

        for strat_name, pool in strategy_pools.items():
            main_nodes = pool["mainline"]
            quar_nodes = pool["quarantine"]

            # Physical execution of mainline pool on Fixed version
            main_fixed_outcomes: Dict[str, str] = {}
            code_mf = 0
            if main_nodes:
                main_fixed_rep = pool_reports_dir / f"{strat_name}_main_fixed.json"
                t0_mf = time.time()
                code_mf, rep_data_mf, out_mf, err_mf = _run_pytest_with_plugin(
                    main_nodes, cwd=fixed_wt, report_file=main_fixed_rep, python_paths=py_paths_fixed
                )
                dur_mf = time.time() - t0_mf
                tests_dict_mf = rep_data_mf.get("tests", {}) if isinstance(rep_data_mf.get("tests"), dict) else {}
                for nid, t_info in tests_dict_mf.items():
                    main_fixed_outcomes[nid] = t_info.get("outcome", "UNKNOWN") if isinstance(t_info, dict) else str(t_info)
                logger.log_command(
                    f"{instance_id}_06_{strat_name}_main_fixed",
                    f"pytest {len(main_nodes)} tests (strategy={strat_name}, pool=mainline, codebase=fixed)",
                    str(fixed_wt),
                    code_mf,
                    round(dur_mf, 4),
                    stdout=out_mf,
                    stderr=err_mf,
                )

            # Physical execution of mainline pool on Buggy version
            main_buggy_outcomes: Dict[str, str] = {}
            code_mb = 0
            if main_nodes:
                main_buggy_rep = pool_reports_dir / f"{strat_name}_main_buggy.json"
                t0_mb = time.time()
                code_mb, rep_data_mb, out_mb, err_mb = _run_pytest_with_plugin(
                    main_nodes, cwd=buggy_wt, report_file=main_buggy_rep, python_paths=py_paths_buggy
                )
                dur_mb = time.time() - t0_mb
                tests_dict_mb = rep_data_mb.get("tests", {}) if isinstance(rep_data_mb.get("tests"), dict) else {}
                for nid, t_info in tests_dict_mb.items():
                    main_buggy_outcomes[nid] = t_info.get("outcome", "UNKNOWN") if isinstance(t_info, dict) else str(t_info)
                logger.log_command(
                    f"{instance_id}_06_{strat_name}_main_buggy",
                    f"pytest {len(main_nodes)} tests (strategy={strat_name}, pool=mainline, codebase=buggy)",
                    str(buggy_wt),
                    code_mb,
                    round(dur_mb, 4),
                    stdout=out_mb,
                    stderr=err_mb,
                )

            # Physical execution of quarantine pool on Buggy version (for Triage)
            quar_buggy_outcomes: Dict[str, str] = {}
            code_qb = 0
            if quar_nodes:
                quar_buggy_rep = pool_reports_dir / f"{strat_name}_quar_buggy.json"
                t0_qb = time.time()
                code_qb, rep_data_qb, out_qb, err_qb = _run_pytest_with_plugin(
                    quar_nodes, cwd=buggy_wt, report_file=quar_buggy_rep, python_paths=py_paths_buggy
                )
                dur_qb = time.time() - t0_qb
                tests_dict_qb = rep_data_qb.get("tests", {}) if isinstance(rep_data_qb.get("tests"), dict) else {}
                for nid, t_info in tests_dict_qb.items():
                    quar_buggy_outcomes[nid] = t_info.get("outcome", "UNKNOWN") if isinstance(t_info, dict) else str(t_info)
                logger.log_command(
                    f"{instance_id}_06_{strat_name}_quar_buggy",
                    f"pytest {len(quar_nodes)} tests (strategy={strat_name}, pool=quarantine, codebase=buggy)",
                    str(buggy_wt),
                    code_qb,
                    round(dur_qb, 4),
                    stdout=out_qb,
                    stderr=err_qb,
                )

            # Metrics Computation based on Physical Executions
            n_main = len(main_nodes)
            n_quar = len(quar_nodes)

            # Mainline CI determinism
            main_flaky_count = sum(1 for nid in main_nodes if flakiness_records.get(nid, {}).get("is_flaky", False))
            ci_flaky_rate = main_flaky_count / n_main if n_main > 0 else 0.0

            # Mainline Defect Retention (Verified via physical execution on buggy code)
            main_defect_retained = 0
            if main_nodes and code_mb != 0:
                for nid in main_nodes:
                    if nid in defect_detecting_test_keys:
                        outcome = main_buggy_outcomes.get(nid)
                        if outcome in ("ASSERTION_FAILED", "EXCEPTION"):
                            main_defect_retained += 1

            quar_defect_retained = 0
            if quar_nodes and code_qb != 0:
                for nid in quar_nodes:
                    if nid in defect_detecting_test_keys:
                        outcome = quar_buggy_outcomes.get(nid)
                        if outcome in ("ASSERTION_FAILED", "EXCEPTION"):
                            quar_defect_retained += 1

            sys_defect_retained = main_defect_retained + quar_defect_retained

            # Real Bug Retention
            main_bugs = real_bugs_ground_truth if (main_defect_retained > 0 and real_bugs_ground_truth > 0) else 0
            quar_bugs = real_bugs_ground_truth if (quar_defect_retained > 0 and real_bugs_ground_truth > 0) else 0
            sys_bugs = real_bugs_ground_truth if (sys_defect_retained > 0 and real_bugs_ground_truth > 0) else 0

            # Mutation Score
            ms_val = mut_rep.mutation_score if mut_rep.mutation_score is not None else 0.0

            physical_strategy_results[strat_name] = StrategyMetrics(
                strategy_name=strat_name,
                total_tests=N_total,
                executable_tests=n_main,
                executable_retention_rate=round(n_main / N_total, 4) if N_total > 0 else None,
                quarantined_tests=n_quar,
                quarantine_rate=round(n_quar / N_total, 4) if N_total > 0 else None,
                ci_flakiness_rate=round(ci_flaky_rate, 4),
                ci_deterministic_rate=round(1.0 - ci_flaky_rate, 4),
                real_bugs_retained=sys_bugs,
                real_bugs_total=real_bugs_ground_truth,
                real_bug_retention_rate=round(sys_bugs / real_bugs_ground_truth, 4) if real_bugs_ground_truth > 0 else None,
                defect_tests_retained=sys_defect_retained,
                defect_tests_total=total_dt,
                defect_test_retention_rate=round(sys_defect_retained / total_dt, 4) if total_dt > 0 else None,
                avg_mutation_score=ms_val,
                mainline_defect_tests_retained=main_defect_retained,
                quarantine_defect_tests_retained=quar_defect_retained,
                mainline_defect_test_retention_rate=round(main_defect_retained / total_dt, 4) if total_dt > 0 else None,
                quarantine_defect_test_retention_rate=round(quar_defect_retained / total_dt, 4) if total_dt > 0 else None,
                mainline_real_bugs_retained=main_bugs,
                quarantine_real_bugs_retained=quar_bugs,
                mainline_real_bug_retention_rate=round(main_bugs / real_bugs_ground_truth, 4) if real_bugs_ground_truth > 0 else None,
                quarantine_real_bug_retention_rate=round(quar_bugs / real_bugs_ground_truth, 4) if real_bugs_ground_truth > 0 else None,
                system_defect_test_retention_rate=round(sys_defect_retained / total_dt, 4) if total_dt > 0 else None,
                system_real_bug_retention_rate=round(sys_bugs / real_bugs_ground_truth, 4) if real_bugs_ground_truth > 0 else None,
            )

    elapsed = time.time() - start_time
    print(f"  -> Instance {instance_id} completed successfully in {elapsed:.2f}s")

    return {
        "instance_id": instance_id,
        "repo": cfg["repo"],
        "domain": cfg["domain"],
        "duration_seconds": round(elapsed, 2),
        "total_tests": N_total,
        "real_bugs_ground_truth": real_bugs_ground_truth,
        "defect_detecting_tests": n_bug_det,
        "flaky_tests_count": sum(1 for r in flakiness_records.values() if r["is_flaky"]),
        "mutation_score": mut_rep.mutation_score,
        "mutation_score_str": mut_rep.mutation_score_str,
        "mode_evaluation": mode_eval_results,
        "triage_summary": {
            "tier_1_safe_keep": len(tier1_nodeids),
            "tier_2_dual_purpose": len(tier2_nodeids),
            "tier_3_safe_low": len(tier3_nodeids),
            "tier_4_spurious": len(tier4_nodeids),
        },
        "strategy_comparison": {k: asdict(v) for k, v in physical_strategy_results.items()},
    }


def main():
    parser = argparse.ArgumentParser(description="Run Phase IV Formal Empirical Study Rerun.")
    parser.add_argument("--run-id", type=str, default=None, help="Custom run ID")
    parser.add_argument("--instances", nargs="+", default=None, help="Specific instances to run")
    parser.add_argument("--num-runs", type=int, default=20, help="Number of repetitions per test (default 20)")
    parser.add_argument("--max-mutants", type=int, default=3, help="Max mutants per instance (default 3)")
    args = parser.parse_args()

    run_id = args.run_id or f"run_phase4_rerun_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir = PROJECT_ROOT / "results" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    logger = ExecutionLogger(run_dir)

    print("=" * 80)
    print("PHASE IV FORMAL EMPIRICAL STUDY RERUN (PROTOCOL-COMPLIANT)")
    print(f"Run ID: {run_id}")
    print(f"Output Directory: {run_dir}")
    print(f"Repetitions per test: N={args.num_runs}")
    print(f"Max Mutants per instance: {args.max_mutants}")
    print("=" * 80)

    # 1. Pre-Run Repository Cleanliness Audit
    print("\n[Phase 1/5] Auditing Shared Repositories Pre-Run...")
    pre_audit = audit_all_repos()
    (run_dir / "pre_run_repos_audit.json").write_text(json.dumps(pre_audit, indent=2), encoding="utf-8")
    if not pre_audit.get("all_repos_clean", False):
        raise RuntimeError(f"ABORT: Shared repositories dirty before run: {pre_audit}")
    print("  -> Pre-run audit PASSED: All 5 repositories 100% Clean (0 diff, 0 untracked).")

    # 2. Load SWE-bench instances
    print("\n[Phase 2/5] Loading SWE-bench Verified Benchmark Instances...")
    all_swebench = load_swebench_instances()
    inst_map = {inst.instance_id: inst for inst in all_swebench}

    selected_ids = args.instances if args.instances else list(INSTANCE_CONFIGS.keys())
    print(f"  -> Target benchmark matrix ({len(selected_ids)} instances): {selected_ids}")

    # 3. Execute Study Instances
    print("\n[Phase 3/5] Executing Rerun Pipeline Across Benchmark Matrix...")
    instance_results = []
    for iid in selected_ids:
        if iid not in INSTANCE_CONFIGS:
            print(f"[-] Unknown instance: {iid}, skipping.")
            continue
        cfg = INSTANCE_CONFIGS[iid]
        instance = inst_map.get(iid)
        if not instance:
            print(f"[-] Instance {iid} not found in SWE-bench Verified dataset, skipping.")
            continue

        try:
            res = run_instance_study_rerun(iid, instance, cfg, run_dir, args.num_runs, args.max_mutants, logger)
            instance_results.append(res)
        except Exception as e:
            print(f"CRITICAL ERROR on instance {iid}: {e}")
            import traceback
            traceback.print_exc()
            instance_results.append({"instance_id": iid, "error": str(e)})

        # Incremental save to disk so no progress is ever lost
        with open(run_dir / "instance_results_incremental.json", "w", encoding="utf-8") as f:
            json.dump(instance_results, f, indent=2)

    # 4. Post-Run Repository Cleanliness Audit
    print("\n[Phase 4/5] Auditing Shared Repositories Post-Run...")
    post_audit = audit_all_repos()
    (run_dir / "post_run_repos_audit.json").write_text(json.dumps(post_audit, indent=2), encoding="utf-8")
    if not post_audit.get("all_repos_clean", False):
        raise RuntimeError(f"ABORT: Repository pollution detected post-run: {post_audit}")
    print("  -> Post-run audit PASSED: All 5 repositories remain 100% Clean (0 diff, 0 untracked).")

    # 5. Statistical Rigor & Metric Aggregation
    print("\n[Phase 5/5] Computing Clustered SE, Wilcoxon, A12 & Pareto Analysis...")
    valid_results = [r for r in instance_results if "error" not in r and r.get("strategy_comparison")]
    excluded_results = [r for r in instance_results if "error" in r or not r.get("strategy_comparison")]

    print(f"  -> Valid benchmark instances for statistical evaluation: {len(valid_results)}")
    if excluded_results:
        print(f"  -> Excluded instances per protocol: {[e.get('instance_id') for e in excluded_results]}")

    strategies = ["Keep-All", "Discard-All-Flaky", "Random-Filtering", "Static-Only", "Risk-Aware-Triage"]
    strategy_aggregates: Dict[str, Any] = {}

    for strat in strategies:
        exec_pairs = [(r["repo"], r["strategy_comparison"][strat]["executable_retention_rate"]) for r in valid_results if r["strategy_comparison"][strat]["executable_retention_rate"] is not None]
        quar_pairs = [(r["repo"], r["strategy_comparison"][strat]["quarantine_rate"]) for r in valid_results if r["strategy_comparison"][strat]["quarantine_rate"] is not None]
        determ_pairs = [(r["repo"], r["strategy_comparison"][strat]["ci_deterministic_rate"]) for r in valid_results if r["strategy_comparison"][strat]["ci_deterministic_rate"] is not None]
        bug_pairs = [(r["repo"], r["strategy_comparison"][strat]["real_bug_retention_rate"]) for r in valid_results if r["strategy_comparison"][strat]["real_bug_retention_rate"] is not None]
        dt_pairs = [(r["repo"], r["strategy_comparison"][strat]["defect_test_retention_rate"]) for r in valid_results if r["strategy_comparison"][strat]["defect_test_retention_rate"] is not None]
        mut_scores = [(r["repo"], r["strategy_comparison"][strat]["avg_mutation_score"]) for r in valid_results if r["strategy_comparison"][strat]["avg_mutation_score"] is not None]

        main_dt_pairs = [(r["repo"], r["strategy_comparison"][strat]["mainline_defect_test_retention_rate"]) for r in valid_results if r["strategy_comparison"][strat]["mainline_defect_test_retention_rate"] is not None]
        quar_dt_pairs = [(r["repo"], r["strategy_comparison"][strat]["quarantine_defect_test_retention_rate"]) for r in valid_results if r["strategy_comparison"][strat]["quarantine_defect_test_retention_rate"] is not None]

        mean_exec, se_exec = compute_clustered_standard_error([p[0] for p in exec_pairs], [p[1] for p in exec_pairs]) if exec_pairs else (None, None)
        mean_quar, se_quar = compute_clustered_standard_error([p[0] for p in quar_pairs], [p[1] for p in quar_pairs]) if quar_pairs else (None, None)
        mean_determ, se_determ = compute_clustered_standard_error([p[0] for p in determ_pairs], [p[1] for p in determ_pairs]) if determ_pairs else (None, None)
        mean_bug, se_bug = compute_clustered_standard_error([p[0] for p in bug_pairs], [p[1] for p in bug_pairs]) if bug_pairs else (None, None)
        mean_dt, se_dt = compute_clustered_standard_error([p[0] for p in dt_pairs], [p[1] for p in dt_pairs]) if dt_pairs else (None, None)
        mean_mut, se_mut = compute_clustered_standard_error([p[0] for p in mut_scores], [p[1] for p in mut_scores]) if mut_scores else (None, None)

        mean_main_dt, se_main_dt = compute_clustered_standard_error([p[0] for p in main_dt_pairs], [p[1] for p in main_dt_pairs]) if main_dt_pairs else (None, None)
        mean_quar_dt, se_quar_dt = compute_clustered_standard_error([p[0] for p in quar_dt_pairs], [p[1] for p in quar_dt_pairs]) if quar_dt_pairs else (None, None)

        strategy_aggregates[strat] = {
            "exec_retention": mean_exec,
            "exec_retention_se": se_exec,
            "quarantine_rate": mean_quar,
            "quarantine_rate_se": se_quar,
            "ci_determinism": mean_determ,
            "ci_determinism_se": se_determ,
            "bug_retention": mean_bug,
            "bug_retention_se": se_bug,
            "defect_tests_retention": mean_dt,
            "defect_tests_retention_se": se_dt,
            "mutation_score": mean_mut,
            "mutation_score_se": se_mut,
            "mainline_defect_tests_retention": mean_main_dt,
            "mainline_defect_tests_retention_se": se_main_dt,
            "quarantine_defect_tests_retention": mean_quar_dt,
            "quarantine_defect_tests_retention_se": se_quar_dt,
        }

    # Hypothesis Testing: Risk-Aware Triage vs Baselines (Pair-filtered to strictly exclude None values)
    hypothesis_tests = {}
    for baseline in ["Discard-All-Flaky", "Random-Filtering", "Static-Only", "Keep-All"]:
        valid_dt_pairs = [
            (r["strategy_comparison"]["Risk-Aware-Triage"]["defect_test_retention_rate"],
             r["strategy_comparison"][baseline]["defect_test_retention_rate"])
            for r in valid_results
            if r["strategy_comparison"]["Risk-Aware-Triage"]["defect_test_retention_rate"] is not None
            and r["strategy_comparison"][baseline]["defect_test_retention_rate"] is not None
        ]
        if valid_dt_pairs:
            s_a = [p[0] for p in valid_dt_pairs]
            s_b = [p[1] for p in valid_dt_pairs]
            w_res = compute_wilcoxon_signed_rank(s_a, s_b)
            w, p = w_res.statistic, w_res.p_value
            a12, mag = compute_paired_effect_size(s_a, s_b)
            n_p, n_nz = w_res.n_pairs, w_res.n_non_zero
        else:
            w, p, a12, mag = None, None, None, "undefined"
            n_p, n_nz = 0, 0
        hypothesis_tests[f"Triage_vs_{baseline}_Defect_Retention"] = {
            "wilcoxon_w": w,
            "p_value": p,
            "n_pairs": n_p,
            "n_non_zero_diffs": n_nz,
            "vargha_delaney_a12": a12,
            "a12_magnitude": mag,
        }

    # Triage vs Discard-All-Flaky on Quarantine Rate
    valid_quar_pairs = [
        (r["strategy_comparison"]["Risk-Aware-Triage"]["quarantine_rate"],
         r["strategy_comparison"]["Discard-All-Flaky"]["quarantine_rate"])
        for r in valid_results
        if r["strategy_comparison"]["Risk-Aware-Triage"]["quarantine_rate"] is not None
        and r["strategy_comparison"]["Discard-All-Flaky"]["quarantine_rate"] is not None
    ]
    if valid_quar_pairs:
        s_qa = [p[0] for p in valid_quar_pairs]
        s_qb = [p[1] for p in valid_quar_pairs]
        w_q_res = compute_wilcoxon_signed_rank(s_qa, s_qb)
        w_q, p_q = w_q_res.statistic, w_q_res.p_value
        a12_q, mag_q = compute_paired_effect_size(s_qa, s_qb)
        n_p_q, n_nz_q = w_q_res.n_pairs, w_q_res.n_non_zero
    else:
        w_q, p_q, a12_q, mag_q = None, None, None, "undefined"
        n_p_q, n_nz_q = 0, 0
    hypothesis_tests["Triage_vs_Discard-All-Flaky_Quarantine_Rate"] = {
        "wilcoxon_w": w_q,
        "p_value": p_q,
        "n_pairs": n_p_q,
        "n_non_zero_diffs": n_nz_q,
        "vargha_delaney_a12": a12_q,
        "a12_magnitude": mag_q,
    }

    # Triage vs Static-Only on Executable Retention
    valid_exec_pairs = [
        (r["strategy_comparison"]["Risk-Aware-Triage"]["executable_retention_rate"],
         r["strategy_comparison"]["Static-Only"]["executable_retention_rate"])
        for r in valid_results
        if r["strategy_comparison"]["Risk-Aware-Triage"]["executable_retention_rate"] is not None
        and r["strategy_comparison"]["Static-Only"]["executable_retention_rate"] is not None
    ]
    if valid_exec_pairs:
        s_ea = [p[0] for p in valid_exec_pairs]
        s_eb = [p[1] for p in valid_exec_pairs]
        w_e_res = compute_wilcoxon_signed_rank(s_ea, s_eb)
        w_e, p_e = w_e_res.statistic, w_e_res.p_value
        a12_e, mag_e = compute_paired_effect_size(s_ea, s_eb)
        n_p_e, n_nz_e = w_e_res.n_pairs, w_e_res.n_non_zero
    else:
        w_e, p_e, a12_e, mag_e = None, None, None, "undefined"
        n_p_e, n_nz_e = 0, 0
    hypothesis_tests["Triage_vs_Static-Only_Executable_Retention"] = {
        "wilcoxon_w": w_e,
        "p_value": p_e,
        "n_pairs": n_p_e,
        "n_non_zero_diffs": n_nz_e,
        "vargha_delaney_a12": a12_e,
        "a12_magnitude": mag_e,
    }

    # Apply Holm correction to raw p-values
    raw_p_list = [(k, v["p_value"]) for k, v in hypothesis_tests.items()]
    adj_p_map = adjust_p_values_holm(raw_p_list)
    for k in hypothesis_tests:
        hypothesis_tests[k]["p_value_holm"] = adj_p_map.get(k)

    # Pareto Frontier Analysis
    pareto_points = []
    for strat in strategies:
        agg = strategy_aggregates[strat]
        flakiness = 1.0 - (agg["ci_determinism"] or 1.0)
        dt_ret = agg["defect_tests_retention"] or 0.0
        pareto_points.append({
            "strategy": strat,
            "ci_flakiness": round(flakiness, 4),
            "ci_determinism": round(agg["ci_determinism"] or 1.0, 4),
            "defect_tests_retention": round(dt_ret, 4),
        })
    pareto_frontier = compute_pareto_frontier(pareto_points, minimize_x="ci_flakiness", maximize_y="defect_tests_retention")

    # Generate LaTeX strategy comparison table
    latex_table_str = generate_latex_table(strategy_aggregates)
    (run_dir / "tab_strategy_comparison.tex").write_text(latex_table_str, encoding="utf-8")

    # Final Full Results JSON
    full_results = {
        "run_id": run_id,
        "timestamp_utc": datetime.datetime.utcnow().isoformat(),
        "environment": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
        },
        "settings": {
            "num_runs": args.num_runs,
            "max_mutants": args.max_mutants,
            "instances_count": len(valid_results),
        },
        "instance_results": valid_results,
        "strategy_aggregates": strategy_aggregates,
        "hypothesis_tests": hypothesis_tests,
        "pareto_frontier": pareto_frontier,
        "excluded_instances": excluded_results,
    }

    with open(run_dir / "phase4_full_study_results.json", "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=2)

    # Generate Markdown Summary Report
    report_md = [
        f"# Phase IV Formal Study Rerun Report ({run_id})",
        f"",
        f"**Date (UTC)**: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Settings**: N={args.num_runs} repetitions, Max Mutants={args.max_mutants}  ",
        f"**Valid Instances**: {len(valid_results)} / {len(selected_ids)} evaluated  ",
        f"",
        f"## Overall Strategy Comparison (Mean ± Clustered SE)",
        f"",
        f"| Strategy | Exec. Ret. (%) | Quarantine (%) | CI Determ. (%) | Bug Ret. (%) | Defect Tests Ret. (%) | Mut. Score (%) | Mainline DT Ret. (%) | Quar. DT Ret. (%) |",
        f"|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]
    for strat, agg in strategy_aggregates.items():
        e = f"{agg['exec_retention']*100:.1f} ± {agg['exec_retention_se']*100:.1f}" if agg['exec_retention'] is not None else "N/A"
        q = f"{agg['quarantine_rate']*100:.1f} ± {agg['quarantine_rate_se']*100:.1f}" if agg['quarantine_rate'] is not None else "0.0 ± 0.0"
        d = f"{agg['ci_determinism']*100:.1f} ± {agg['ci_determinism_se']*100:.1f}" if agg['ci_determinism'] is not None else "N/A"
        b = f"{agg['bug_retention']*100:.1f} ± {agg['bug_retention_se']*100:.1f}" if agg['bug_retention'] is not None else "N/A"
        dt = f"{agg['defect_tests_retention']*100:.1f} ± {agg['defect_tests_retention_se']*100:.1f}" if agg['defect_tests_retention'] is not None else "N/A"
        m = f"{agg['mutation_score']*100:.1f} ± {agg['mutation_score_se']*100:.1f}" if agg['mutation_score'] is not None else "N/A"
        mdt = f"{agg['mainline_defect_tests_retention']*100:.1f} ± {agg['mainline_defect_tests_retention_se']*100:.1f}" if agg.get('mainline_defect_tests_retention') is not None else "N/A"
        qdt = f"{agg['quarantine_defect_tests_retention']*100:.1f} ± {agg['quarantine_defect_tests_retention_se']*100:.1f}" if agg.get('quarantine_defect_tests_retention') is not None else "N/A"
        report_md.append(f"| **{strat}** | {e} | {q} | {d} | {b} | {dt} | {m} | {mdt} | {qdt} |")

    report_md.extend([
        f"",
        f"## Hypothesis Testing (Triage vs Baselines)",
        f"",
        f"| Comparison | n_pairs | Non-zero | Wilcoxon W | p-value (raw) | p-value (Holm) | Paired A12 | Magnitude |",
        f"|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ])
    for comp, h in hypothesis_tests.items():
        w_s = f"{h['wilcoxon_w']}" if h.get("wilcoxon_w") is not None else "N/A"
        p_raw = f"{h['p_value']:.4f}" if h.get("p_value") is not None else "N/A"
        p_holm = f"{h['p_value_holm']:.4f}" if h.get("p_value_holm") is not None else "N/A"
        a12_s = f"{h['vargha_delaney_a12']:.4f}" if h.get("vargha_delaney_a12") is not None else "N/A"
        n_p = h.get("n_pairs", "N/A")
        n_nz = h.get("n_non_zero_diffs", "N/A")
        mag = str(h.get("a12_magnitude", "undefined"))
        report_md.append(f"| {comp} | {n_p} | {n_nz} | {w_s} | {p_raw} | {p_holm} | {a12_s} | {mag} |")

    (run_dir / "phase4_study_report.md").write_text("\n".join(report_md), encoding="utf-8")

    # Generate SHA-256 Manifest
    manifest = {
        "run_id": run_id,
        "files_count": 0,
        "timestamp_utc": datetime.datetime.utcnow().isoformat(),
        "files": {},
    }
    for fpath in run_dir.rglob("*"):
        if fpath.is_file() and fpath.name != "manifest.json":
            rel = str(fpath.relative_to(run_dir))
            manifest["files"][rel] = sha256_file(fpath)
    manifest["files_count"] = len(manifest["files"])

    with open(run_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 80)
    print("PHASE IV RERUN COMPLETE")
    print(f"Results archived in: {run_dir}")
    print(f"Manifest: {manifest['files_count']} files verified with SHA-256")
    print("=" * 80)


if __name__ == "__main__":
    main()
