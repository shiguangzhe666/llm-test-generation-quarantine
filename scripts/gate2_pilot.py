"""
Gate 2 Feasibility Pilot — End-to-end validation of RQ1 + RQ2 on 3 SWE-bench instances.

This script orchestrates:
1. Load SWE-bench instance metadata (patch, FAIL_TO_PASS, problem statement)
2. Clone repos and extract buggy/fixed source files
3. Generate tests using local Ollama (qwen3:8b, free)
4. Run repeated execution (20x) on fixed version → flakiness classification
5. Run on buggy version → bug-detection assessment  
6. Cross-reference: which flaky tests also detect the real bug?
7. Evaluate failure conditions F1–F3

Zero cost — all computation is local.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.swebench_loader import (
    load_swebench_instances,
    clone_repo,
    extract_source_at_commits,
    print_instance_summary,
    SWEBenchInstance,
)
from src.generation.generate_tests import generate_tests, call_ollama, extract_code_from_response


# ---------- Configuration ----------

PILOT_INSTANCES = [
    "psf__requests-1921",
    "pytest-dev__pytest-7521",
    "sympy__sympy-15809",
]

MODELS = ["qwen3:8b"]
TEMPLATES = ["basic"]  # Start with basic only for pilot
NUM_GENERATIONS = 3     # 3 independent generations per instance per template
REPEAT_RUNS = 20        # 20 repeated executions for flakiness detection
TIMEOUT_PER_RUN = 30    # seconds

DATA_DIR = PROJECT_ROOT / "data"
REPOS_DIR = DATA_DIR / "repos"
PILOT_DIR = DATA_DIR / "pilot_gate2"
RESULTS_DIR = PROJECT_ROOT / "results" / "gate2"

# Prompt template for project-level test generation
PROJECT_LEVEL_TEMPLATE = """You are a Python testing expert. Generate pytest unit tests for the following Python source code.

## Context
This code is from the open-source project "{repo_name}".
The specific file being tested is: {filepath}

{problem_hint}

## Requirements
- Write thorough pytest test functions that test the code's behavior
- Include edge cases and boundary conditions
- Use descriptive test function names starting with test_
- Each test should have clear, specific assertions
- Import the module under test correctly
- Do NOT use any external services, network calls, or mock servers
- Do NOT use sleep() or time-dependent assertions
- Use pytest fixtures where appropriate
- Tests should be self-contained and independent of each other

## Source Code Under Test

```python
{source}
```

## Output

Write ONLY valid Python pytest test code. Start with necessary imports.
Do NOT include any explanation, markdown formatting, or comments about what you're doing.
"""


@dataclass
class TestGenerationRecord:
    """Record of a single test generation attempt."""
    instance_id: str
    model: str
    template: str
    generation_id: int
    timestamp: str
    duration_seconds: float
    test_code: str
    test_code_length: int
    is_valid_python: bool
    num_test_functions: int


@dataclass
class FlakinessResult:
    """Per-test flakiness result from repeated execution."""
    test_name: str
    total_runs: int
    pass_count: int
    fail_count: int
    error_count: int
    is_flaky: bool
    flakiness_rate: float
    category: str  # stable_pass, stable_fail, flaky
    failure_messages: list[str] = field(default_factory=list)


@dataclass
class BugDetectionResult:
    """Whether a test detects the real bug."""
    test_name: str
    passes_on_fixed: bool    # Should be True for a good test
    fails_on_buggy: bool     # True = detects the bug
    is_bug_detecting: bool   # passes_on_fixed AND fails_on_buggy
    fixed_error: str = ""
    buggy_error: str = ""


@dataclass
class PilotInstanceResult:
    """Complete result for one SWE-bench instance."""
    instance_id: str
    repo: str
    version: str
    num_fail_to_pass: int
    num_patched_files: int
    target_functions: list[str]
    
    # Generation
    generations: list[dict] = field(default_factory=list)
    total_tests_generated: int = 0
    valid_tests_generated: int = 0
    
    # Flakiness (RQ1)
    flakiness_results: list[dict] = field(default_factory=list)
    total_tests_executed: int = 0
    stable_pass_count: int = 0
    stable_fail_count: int = 0
    flaky_count: int = 0
    flakiness_rate: float = 0.0
    
    # Bug detection (RQ2)
    bug_detection_results: list[dict] = field(default_factory=list)
    bug_detecting_tests: int = 0
    bug_detecting_and_flaky: int = 0  # THE KEY METRIC
    bug_detecting_and_stable: int = 0
    
    # Derived
    overlap_rate: float = 0.0  # flaky ∩ bug-detecting / flaky


def count_test_functions(code: str) -> int:
    """Count the number of test functions in Python code."""
    return len(re.findall(r"^\s*def\s+test_\w+", code, re.MULTILINE))


def is_valid_python(code: str) -> bool:
    """Check if code is syntactically valid Python."""
    try:
        compile(code, "<test>", "exec")
        return True
    except SyntaxError:
        return False


def run_test_file(
    test_file: Path,
    project_dir: Path,
    env_extras: dict = None,
    timeout: int = 30,
) -> dict:
    """Run a test file once and return structured results."""
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v", "--tb=short", "-q",
        "--no-header",
    ]
    
    env = os.environ.copy()
    if env_extras:
        env.update(env_extras)
    
    # Ensure the project dir is in PYTHONPATH
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{project_dir}{os.pathsep}{existing}" if existing else str(project_dir)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True,
            timeout=timeout,
            cwd=str(project_dir),
            env=env,
        )
        
        # Parse individual test results from verbose output
        test_results = {}
        for line in result.stdout.split("\n"):
            # Match lines like "test_file.py::test_name PASSED" or "FAILED"
            match = re.search(r"(test_\w+)\s+(PASSED|FAILED|ERROR)", line)
            if match:
                test_results[match.group(1)] = match.group(2)
        
        return {
            "exit_code": result.returncode,
            "passed": result.returncode == 0,
            "test_results": test_results,
            "stdout": result.stdout[-2000:],  # Last 2000 chars
            "stderr": result.stderr[-1000:],
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": -1,
            "passed": False,
            "test_results": {},
            "stdout": "TIMEOUT",
            "stderr": "",
        }
    except Exception as e:
        return {
            "exit_code": -2,
            "passed": False,
            "test_results": {},
            "stdout": "",
            "stderr": str(e),
        }


def run_repeated_per_test(
    test_file: Path,
    project_dir: Path,
    num_runs: int = 20,
    timeout: int = 30,
) -> list[FlakinessResult]:
    """
    Run a test file N times and compute per-test flakiness.
    
    Returns a FlakinessResult for each individual test function.
    """
    # Aggregate per-test results across runs
    test_verdicts = {}  # test_name -> list of "PASSED"/"FAILED"/"ERROR"
    test_errors = {}    # test_name -> list of error messages
    
    for run_id in range(num_runs):
        seed = run_id * 7919 + 42
        env_extras = {"PYTHONHASHSEED": str(seed)}
        
        result = run_test_file(test_file, project_dir, env_extras, timeout)
        
        for tname, verdict in result["test_results"].items():
            if tname not in test_verdicts:
                test_verdicts[tname] = []
                test_errors[tname] = []
            test_verdicts[tname].append(verdict)
            if verdict != "PASSED" and result["stdout"]:
                # Extract relevant error for this test
                test_errors[tname].append(verdict)
        
        status = "PASS" if result["passed"] else "FAIL"
        n_tests = len(result["test_results"])
        print(f"    Run {run_id+1:2d}/{num_runs}: {status} ({n_tests} tests)")
    
    # Compute flakiness for each test
    results = []
    for tname, verdicts in test_verdicts.items():
        pass_count = verdicts.count("PASSED")
        fail_count = verdicts.count("FAILED")
        error_count = verdicts.count("ERROR")
        total = len(verdicts)
        
        is_flaky = (pass_count > 0 and (fail_count + error_count) > 0)
        flakiness_rate = min(pass_count, fail_count + error_count) / total if total > 0 else 0
        
        if not is_flaky:
            category = "stable_pass" if pass_count == total else "stable_fail"
        elif flakiness_rate < 0.1:
            category = "rare_flaky"
        elif flakiness_rate < 0.3:
            category = "occasional_flaky"
        else:
            category = "frequent_flaky"
        
        results.append(FlakinessResult(
            test_name=tname,
            total_runs=total,
            pass_count=pass_count,
            fail_count=fail_count,
            error_count=error_count,
            is_flaky=is_flaky,
            flakiness_rate=round(flakiness_rate, 4),
            category=category,
            failure_messages=test_errors.get(tname, [])[:5],
        ))
    
    return results


def evaluate_bug_detection(
    test_file: Path,
    fixed_dir: Path,
    buggy_dir: Path,
    source_files: list[str],
    timeout: int = 30,
) -> list[BugDetectionResult]:
    """
    Evaluate whether each test detects the real bug by:
    1. Running with the FIXED source → should PASS
    2. Running with the BUGGY source → should FAIL if bug-detecting
    """
    results = []
    
    # We create temporary workspaces with the test file + fixed/buggy source
    for version_name, source_dir in [("fixed", fixed_dir), ("buggy", buggy_dir)]:
        work_dir = test_file.parent / f"_eval_{version_name}"
        work_dir.mkdir(exist_ok=True)
        
        # Copy source files into the workspace
        for sf in source_files:
            src = source_dir / sf
            if src.exists():
                dst = work_dir / Path(sf).name
                shutil.copy2(src, dst)
        
        # Copy the test file
        shutil.copy2(test_file, work_dir / test_file.name)
        
        # Run tests
        run_result = run_test_file(
            work_dir / test_file.name,
            work_dir,
            timeout=timeout,
        )
        
        if version_name == "fixed":
            fixed_results = run_result["test_results"]
        else:
            buggy_results = run_result["test_results"]
        
        # Clean up
        shutil.rmtree(work_dir, ignore_errors=True)
    
    # Compare fixed vs buggy for each test
    all_tests = set(list(fixed_results.keys()) + list(buggy_results.keys()))
    for tname in sorted(all_tests):
        fixed_verdict = fixed_results.get(tname, "MISSING")
        buggy_verdict = buggy_results.get(tname, "MISSING")
        
        passes_on_fixed = (fixed_verdict == "PASSED")
        fails_on_buggy = (buggy_verdict in ("FAILED", "ERROR"))
        
        results.append(BugDetectionResult(
            test_name=tname,
            passes_on_fixed=passes_on_fixed,
            fails_on_buggy=fails_on_buggy,
            is_bug_detecting=passes_on_fixed and fails_on_buggy,
            fixed_error="" if passes_on_fixed else fixed_verdict,
            buggy_error=buggy_verdict if fails_on_buggy else "",
        ))
    
    return results


def run_pilot_instance(
    instance: SWEBenchInstance,
    model: str = "qwen3:8b",
    num_generations: int = 3,
    num_runs: int = 20,
) -> PilotInstanceResult:
    """Run the complete pilot pipeline for one SWE-bench instance."""
    
    print(f"\n{'='*60}")
    print(f"PILOT: {instance.instance_id}")
    print(f"{'='*60}")
    
    pilot_result = PilotInstanceResult(
        instance_id=instance.instance_id,
        repo=instance.repo,
        version=instance.version,
        num_fail_to_pass=len(instance.fail_to_pass),
        num_patched_files=len(instance.patched_files),
        target_functions=instance.target_functions,
    )
    
    # --- Step 1: Clone repo and extract source ---
    print("\n[Step 1] Cloning repo and extracting source...")
    
    instance_dir = PILOT_DIR / instance.instance_id
    instance_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        repo_dir = clone_repo(
            instance.repo,
            instance.base_commit,
            REPOS_DIR,
        )
    except Exception as e:
        print(f"  ERROR cloning repo: {e}")
        return pilot_result
    
    source_info = extract_source_at_commits(repo_dir, instance, instance_dir)
    
    if not source_info["files"]:
        print("  ERROR: No source files extracted (only test files in patch?)")
        return pilot_result
    
    print(f"  Extracted {len(source_info['files'])} source files:")
    for f in source_info["files"]:
        print(f"    - {f}")
    
    # --- Step 2: Read source code for test generation ---
    print("\n[Step 2] Preparing source for LLM test generation...")
    
    fixed_dir = Path(source_info["fixed_dir"])
    buggy_dir = Path(source_info["buggy_dir"])
    
    # Concatenate all non-test source files for the prompt
    source_code_parts = []
    for sf in source_info["files"]:
        fixed_file = fixed_dir / sf
        if fixed_file.exists():
            content = fixed_file.read_text(encoding="utf-8", errors="replace")
            source_code_parts.append(f"# File: {sf}\n{content}")
    
    if not source_code_parts:
        print("  ERROR: No fixed source files available")
        return pilot_result
    
    combined_source = "\n\n".join(source_code_parts)
    
    # Truncate if too long for the LLM context
    if len(combined_source) > 8000:
        combined_source = combined_source[:8000] + "\n# ... (truncated)"
    
    # --- Step 3: Generate tests ---
    print(f"\n[Step 3] Generating tests with {model} (x{num_generations})...")
    
    gen_dir = instance_dir / "generated_tests"
    gen_dir.mkdir(exist_ok=True)
    
    for gen_id in range(num_generations):
        print(f"\n  Generation {gen_id + 1}/{num_generations}:")
        
        prompt = PROJECT_LEVEL_TEMPLATE.format(
            repo_name=instance.repo,
            filepath=", ".join(source_info["files"]),
            problem_hint="",  # Don't leak the bug info!
            source=combined_source,
        )
        
        start = time.time()
        try:
            raw_response = call_ollama(model, prompt, temperature=0.7)
            duration = time.time() - start
            test_code = extract_code_from_response(raw_response)
        except Exception as e:
            print(f"    ERROR: {e}")
            continue
        
        # Validate
        valid = is_valid_python(test_code)
        num_tests = count_test_functions(test_code)
        
        print(f"    Duration: {duration:.1f}s | Valid: {valid} | Tests: {num_tests} | Chars: {len(test_code)}")
        
        record = TestGenerationRecord(
            instance_id=instance.instance_id,
            model=model,
            template="project_level",
            generation_id=gen_id,
            timestamp=datetime.now().isoformat(),
            duration_seconds=round(duration, 2),
            test_code=test_code,
            test_code_length=len(test_code),
            is_valid_python=valid,
            num_test_functions=num_tests,
        )
        pilot_result.generations.append(asdict(record))
        
        if valid and num_tests > 0:
            # Save test file
            test_file = gen_dir / f"test_gen_{gen_id:02d}.py"
            test_file.write_text(test_code, encoding="utf-8")
            pilot_result.valid_tests_generated += num_tests
        
        pilot_result.total_tests_generated += max(num_tests, 0)
    
    if pilot_result.valid_tests_generated == 0:
        print("  ERROR: No valid tests generated — F2 failure condition!")
        return pilot_result
    
    # --- Step 4: Repeated execution for flakiness (RQ1) ---
    print(f"\n[Step 4] Repeated execution for flakiness detection ({num_runs}x)...")
    
    # Create a workspace with fixed source + generated tests
    workspace = instance_dir / "workspace_fixed"
    workspace.mkdir(exist_ok=True)
    
    # Copy fixed source files
    for sf in source_info["files"]:
        src = fixed_dir / sf
        if src.exists():
            dst = workspace / Path(sf).name
            shutil.copy2(src, dst)
    
    all_flakiness = []
    test_files = sorted(gen_dir.glob("test_gen_*.py"))
    
    for test_file in test_files:
        print(f"\n  Analyzing: {test_file.name}")
        
        # Copy test to workspace
        ws_test = workspace / test_file.name
        shutil.copy2(test_file, ws_test)
        
        flakiness = run_repeated_per_test(
            ws_test, workspace, num_runs=num_runs, timeout=TIMEOUT_PER_RUN
        )
        all_flakiness.extend(flakiness)
        
        # Clean up test from workspace
        ws_test.unlink(missing_ok=True)
    
    # Aggregate flakiness stats
    for fr in all_flakiness:
        pilot_result.flakiness_results.append(asdict(fr))
        pilot_result.total_tests_executed += 1
        if fr.category == "stable_pass":
            pilot_result.stable_pass_count += 1
        elif fr.category == "stable_fail":
            pilot_result.stable_fail_count += 1
        else:
            pilot_result.flaky_count += 1
    
    if pilot_result.total_tests_executed > 0:
        pilot_result.flakiness_rate = round(
            pilot_result.flaky_count / pilot_result.total_tests_executed, 4
        )
    
    print(f"\n  Flakiness Summary:")
    print(f"    Total tests: {pilot_result.total_tests_executed}")
    print(f"    Stable pass: {pilot_result.stable_pass_count}")
    print(f"    Stable fail: {pilot_result.stable_fail_count}")
    print(f"    Flaky: {pilot_result.flaky_count} ({pilot_result.flakiness_rate:.1%})")
    
    # --- Step 5: Bug detection evaluation (RQ2) ---
    print(f"\n[Step 5] Bug detection evaluation (fixed vs buggy)...")
    
    all_bug_detection = []
    
    for test_file in test_files:
        print(f"\n  Evaluating: {test_file.name}")
        
        bug_results = evaluate_bug_detection(
            test_file, fixed_dir, buggy_dir,
            source_info["files"],
            timeout=TIMEOUT_PER_RUN,
        )
        all_bug_detection.extend(bug_results)
    
    # Aggregate bug detection stats
    for br in all_bug_detection:
        pilot_result.bug_detection_results.append(asdict(br))
        if br.is_bug_detecting:
            pilot_result.bug_detecting_tests += 1
    
    # --- Step 6: Cross-reference flaky ∩ bug-detecting ---
    print(f"\n[Step 6] Cross-referencing flakiness × bug-detection...")
    
    flaky_set = {fr.test_name for fr in all_flakiness if fr.is_flaky}
    bug_detecting_set = {br.test_name for br in all_bug_detection if br.is_bug_detecting}
    
    overlap = flaky_set & bug_detecting_set
    pilot_result.bug_detecting_and_flaky = len(overlap)
    pilot_result.bug_detecting_and_stable = len(bug_detecting_set - flaky_set)
    
    if len(flaky_set) > 0:
        pilot_result.overlap_rate = round(len(overlap) / len(flaky_set), 4)
    
    print(f"\n  ┌─────────────────────────────────────────┐")
    print(f"  │ CROSS-REFERENCE RESULTS                  │")
    print(f"  ├─────────────────────────────────────────┤")
    print(f"  │ Flaky tests:              {pilot_result.flaky_count:3d}            │")
    print(f"  │ Bug-detecting tests:      {pilot_result.bug_detecting_tests:3d}            │")
    print(f"  │ Flaky ∩ Bug-detecting:    {pilot_result.bug_detecting_and_flaky:3d}            │")
    print(f"  │ Stable ∩ Bug-detecting:   {pilot_result.bug_detecting_and_stable:3d}            │")
    print(f"  │ Overlap rate:             {pilot_result.overlap_rate:6.1%}         │")
    print(f"  └─────────────────────────────────────────┘")
    
    # Clean up workspace
    shutil.rmtree(workspace, ignore_errors=True)
    
    return pilot_result


def evaluate_failure_conditions(results: list[PilotInstanceResult]) -> dict:
    """Evaluate Gate 2 failure conditions F1–F3."""
    
    assessment = {
        "F1_flaky_bug_detecting_overlap": {
            "criterion": "flaky ∩ bug-detecting >= 5% of flaky tests",
            "status": "UNKNOWN",
            "details": "",
        },
        "F2_generation_quality": {
            "criterion": ">= 20% of generated tests are valid and executable",
            "status": "UNKNOWN",
            "details": "",
        },
        "F3_swebench_reproducibility": {
            "criterion": ">= 2 of 3 pilot instances successfully cloned and tested",
            "status": "UNKNOWN",
            "details": "",
        },
    }
    
    # F1: Flaky ∩ Bug-detecting overlap
    total_flaky = sum(r.flaky_count for r in results)
    total_overlap = sum(r.bug_detecting_and_flaky for r in results)
    
    if total_flaky > 0:
        overlap_rate = total_overlap / total_flaky
        assessment["F1_flaky_bug_detecting_overlap"]["status"] = (
            "PASS" if overlap_rate >= 0.05 else "FAIL"
        )
        assessment["F1_flaky_bug_detecting_overlap"]["details"] = (
            f"{total_overlap}/{total_flaky} = {overlap_rate:.1%}"
        )
    else:
        assessment["F1_flaky_bug_detecting_overlap"]["status"] = "INCONCLUSIVE"
        assessment["F1_flaky_bug_detecting_overlap"]["details"] = "No flaky tests observed"
    
    # F2: Generation quality
    total_gen = sum(r.total_tests_generated for r in results)
    total_valid = sum(r.valid_tests_generated for r in results)
    
    if total_gen > 0:
        valid_rate = total_valid / total_gen
        assessment["F2_generation_quality"]["status"] = (
            "PASS" if valid_rate >= 0.20 else "FAIL"
        )
        assessment["F2_generation_quality"]["details"] = (
            f"{total_valid}/{total_gen} = {valid_rate:.1%}"
        )
    else:
        assessment["F2_generation_quality"]["status"] = "FAIL"
        assessment["F2_generation_quality"]["details"] = "No tests generated"
    
    # F3: Reproducibility
    successful = sum(1 for r in results if r.total_tests_executed > 0)
    assessment["F3_swebench_reproducibility"]["status"] = (
        "PASS" if successful >= 2 else "FAIL"
    )
    assessment["F3_swebench_reproducibility"]["details"] = (
        f"{successful}/3 instances successfully tested"
    )
    
    return assessment


def main():
    """Run the complete Gate 2 feasibility pilot."""
    
    print("=" * 60)
    print("GATE 2 FEASIBILITY PILOT")
    print(f"Date: {datetime.now().isoformat()}")
    print(f"Instances: {PILOT_INSTANCES}")
    print(f"Model: {MODELS[0]}")
    print(f"Generations per instance: {NUM_GENERATIONS}")
    print(f"Repeat runs: {REPEAT_RUNS}")
    print("=" * 60)
    
    # Create output directories
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    PILOT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load SWE-bench instances
    print("\n[Phase 1] Loading SWE-bench instances...")
    instances = load_swebench_instances(instance_ids=PILOT_INSTANCES)
    
    if not instances:
        print("ERROR: No instances loaded! Check network/dataset access.")
        sys.exit(1)
    
    for inst in instances:
        print_instance_summary(inst)
    
    # Run pilot for each instance
    all_results = []
    
    for inst in instances:
        try:
            result = run_pilot_instance(
                inst,
                model=MODELS[0],
                num_generations=NUM_GENERATIONS,
                num_runs=REPEAT_RUNS,
            )
            all_results.append(result)
        except Exception as e:
            print(f"\nERROR processing {inst.instance_id}: {e}")
            import traceback
            traceback.print_exc()
    
    # Evaluate failure conditions
    print("\n" + "=" * 60)
    print("FAILURE CONDITION ASSESSMENT")
    print("=" * 60)
    
    assessment = evaluate_failure_conditions(all_results)
    
    for fc_name, fc_data in assessment.items():
        status_icon = {"PASS": "✅", "FAIL": "❌", "INCONCLUSIVE": "⚠️", "UNKNOWN": "❓"}
        icon = status_icon.get(fc_data["status"], "❓")
        print(f"\n  {icon} {fc_name}")
        print(f"     Criterion: {fc_data['criterion']}")
        print(f"     Result:    {fc_data['details']}")
        print(f"     Status:    {fc_data['status']}")
    
    # Save all results
    output = {
        "metadata": {
            "gate": "Gate 2 Feasibility Pilot",
            "timestamp": datetime.now().isoformat(),
            "pilot_instances": PILOT_INSTANCES,
            "model": MODELS[0],
            "num_generations": NUM_GENERATIONS,
            "repeat_runs": REPEAT_RUNS,
        },
        "instance_results": [asdict(r) for r in all_results],
        "failure_assessment": assessment,
        "summary": {
            "total_instances": len(all_results),
            "total_tests_generated": sum(r.total_tests_generated for r in all_results),
            "total_valid_tests": sum(r.valid_tests_generated for r in all_results),
            "total_tests_executed": sum(r.total_tests_executed for r in all_results),
            "total_flaky": sum(r.flaky_count for r in all_results),
            "total_bug_detecting": sum(r.bug_detecting_tests for r in all_results),
            "total_flaky_and_bug_detecting": sum(r.bug_detecting_and_flaky for r in all_results),
            "overall_flakiness_rate": (
                sum(r.flaky_count for r in all_results) /
                max(sum(r.total_tests_executed for r in all_results), 1)
            ),
        },
    }
    
    output_path = RESULTS_DIR / "gate2_pilot_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n\nResults saved to: {output_path}")
    
    # Print final summary
    s = output["summary"]
    print("\n" + "=" * 60)
    print("GATE 2 PILOT SUMMARY")
    print("=" * 60)
    print(f"  Instances tested:            {s['total_instances']}")
    print(f"  Tests generated:             {s['total_tests_generated']}")
    print(f"  Valid tests:                 {s['total_valid_tests']}")
    print(f"  Tests executed (repeated):   {s['total_tests_executed']}")
    print(f"  Flaky tests:                 {s['total_flaky']}")
    print(f"  Bug-detecting tests:         {s['total_bug_detecting']}")
    print(f"  Flaky ∩ Bug-detecting:       {s['total_flaky_and_bug_detecting']}")
    print(f"  Overall flakiness rate:      {s['overall_flakiness_rate']:.1%}")
    print("=" * 60)
    
    # Gate verdict
    all_pass = all(
        fc["status"] == "PASS" for fc in assessment.values()
    )
    
    if all_pass:
        print("\n🟢 GATE 2 VERDICT: PASS — Proceed to Gate 3 (Full Experiment)")
    else:
        failing = [k for k, v in assessment.items() if v["status"] != "PASS"]
        print(f"\n🔴 GATE 2 VERDICT: BLOCKED — Failing conditions: {failing}")
        print("   Review failure conditions and decide on remediation.")


if __name__ == "__main__":
    main()
