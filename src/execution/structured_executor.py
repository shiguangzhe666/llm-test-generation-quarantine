"""
Structured Pytest Executor with Full Observability.

Provides robust, reproducible test execution across three execution modes:
1. Single-test isolated: Each test function runs in a dedicated subprocess.
2. Suite in-order: Suite runs in standard file-order in a single subprocess.
3. Suite randomized: Suite runs in explicitly shuffled order with recorded seed.

Guarantees:
- Preserves full canonical nodeids (classes, parameterized `[param]`, functions).
- Differentiates outcomes: PASSED, ASSERTION_FAILED, IMPORT_ERROR, COLLECTION_ERROR,
  TIMEOUT, SKIPPED, EXCEPTION, NOT_EXECUTED, MISSING_OBSERVATION.
- On abort/crash/timeout: Retains already completed tests; marks the active test
  as TIMEOUT/CRASH; marks unreached planned tests as NOT_EXECUTED (never blanket TIMEOUT).
- If report is missing: Explicitly marks MISSING_OBSERVATION (never assumes pass on exit_code=0).
- Tracks planned order vs actual runtime order from reporter events.
"""

import enum
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PLUGIN_MODULE = "src.execution.pytest_structured_plugin"

from src.execution.nodeid_matching import (
    canonical_nodeid,
    match_nodeids,
    find_test_in_report_data,
    NodeIDMatchResult,
)


class ExecutionMode(str, enum.Enum):
    SINGLE_TEST_ISOLATED = "single_test_isolated"
    SUITE_IN_ORDER = "suite_in_order"
    SUITE_RANDOM = "suite_random"


@dataclass
class TestExecutionResult:
    nodeid: str
    outcome: str  # PASSED, ASSERTION_FAILED, IMPORT_ERROR, COLLECTION_ERROR, TIMEOUT, SKIPPED, EXCEPTION, NOT_EXECUTED, MISSING_OBSERVATION
    duration_seconds: float = 0.0
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def is_passed(self) -> bool:
        return self.outcome == "PASSED"

    @property
    def is_valid_observation(self) -> bool:
        return self.outcome in ("PASSED", "ASSERTION_FAILED", "IMPORT_ERROR", "COLLECTION_ERROR", "TIMEOUT", "SKIPPED", "EXCEPTION")

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SuiteExecutionResult:
    suite_target: str
    execution_mode: str
    random_seed: Optional[int]
    planned_order: List[str]
    actual_runtime_order: List[str]
    duration_seconds: float
    total_planned_tests: int = 0
    valid_observations_count: int = 0
    missing_observations_count: int = 0
    passed_count: int = 0
    assertion_failed_count: int = 0
    import_error_count: int = 0
    collection_error_count: int = 0
    timeout_count: int = 0
    skipped_count: int = 0
    exception_count: int = 0
    not_executed_count: int = 0
    tests: Dict[str, TestExecutionResult] = field(default_factory=dict)
    collection_errors: List[dict] = field(default_factory=list)
    exit_code: Optional[int] = None
    planned_nodeids: List[str] = field(default_factory=list)
    observed_nodeids: List[str] = field(default_factory=list)
    missing_nodeids: List[str] = field(default_factory=list)
    unknown_nodeids: List[str] = field(default_factory=list)
    duplicate_nodeids: List[str] = field(default_factory=list)
    ambiguous_nodeids: List[str] = field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    report_path: Optional[str] = None
    report_integrity: bool = True
    report_error: Optional[str] = None

    # Backward compatibility property
    @property
    def total_tests(self) -> int:
        return len(self.tests)

    # Backward compatibility property
    @property
    def execution_order(self) -> List[str]:
        return self.actual_runtime_order if self.actual_runtime_order else self.planned_order

    def to_dict(self) -> dict:
        return asdict(self)


def build_env(python_paths: Optional[List[str]] = None, seed: Optional[int] = None, extra_env: Optional[dict] = None) -> dict:
    """Construct environment dictionary with complete PYTHONPATH and optional hash seed."""
    env = os.environ.copy()
    paths_to_add = []
    if python_paths:
        paths_to_add.extend(str(p) for p in python_paths)
    paths_to_add.append(str(PROJECT_ROOT))
    existing_pythonpath = env.get("PYTHONPATH", "")
    if existing_pythonpath:
        paths_to_add.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(paths_to_add)
    # Prevent bytecode compilation/caching across test and mutant executions
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if seed is not None:
        env["PYTHONHASHSEED"] = str(seed)
    if extra_env:
        env.update(extra_env)
    return env


def discover_test_nodeids(
    test_target: Union[Path, str],
    cwd: Path,
    python_paths: Optional[List[str]] = None,
    timeout: int = 30,
) -> Tuple[List[str], List[dict]]:
    """
    Discover all canonical test nodeids using pytest --collect-only.
    Returns (nodeids, collection_errors).
    """
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_target),
        "--collect-only", "-q",
        "--assert=plain", "-p", "no:anyio",
    ]
    env = build_env(python_paths)
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), env=env, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return [], [{"nodeid": str(test_target), "outcome": "TIMEOUT", "error_message": "Discovery timed out"}]

    nodeids = []
    collection_errors = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if "::" in line and not line.startswith("="):
            if line.startswith("::"):
                nodeids.append(f"{test_target}{line}")
            else:
                nodeids.append(line)

    if proc.returncode != 0 and not nodeids:
        err_out = (proc.stderr or proc.stdout).strip()
        cat = "IMPORT_ERROR" if "ImportError" in err_out or "ModuleNotFoundError" in err_out else "COLLECTION_ERROR"
        collection_errors.append({
            "nodeid": str(test_target),
            "outcome": cat,
            "error_type": cat,
            "error_message": err_out[:1000],
        })

    return nodeids, collection_errors


def _run_pytest_with_plugin(
    test_args: List[str],
    cwd: Path,
    report_file: Path,
    python_paths: Optional[List[str]] = None,
    seed: Optional[int] = None,
    timeout: int = 60,
    extra_env: Optional[dict] = None,
) -> Tuple[int, dict, str, str]:
    """Invoke pytest with the structured plugin and parse the output JSON."""
    env = build_env(python_paths, seed=seed, extra_env=extra_env)
    env["PYTEST_STRUCTURED_REPORT_PATH"] = str(report_file)

    cmd = [
        sys.executable, "-m", "pytest",
        *test_args,
        "-p", PLUGIN_MODULE,
        "-v", "--assert=plain", "--tb=short", "--no-header",
        "-p", "no:anyio",
    ]

    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), env=env, capture_output=True, text=True, timeout=timeout
        )
        stdout, stderr, exit_code = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if (hasattr(exc, "stdout") and exc.stdout) else ""
        stderr = exc.stderr if (hasattr(exc, "stderr") and exc.stderr) else ""
        exit_code = -1
        stderr = f"TimeoutExpired after {timeout}s: {stderr}"

    report_data = {}
    report_integrity = True
    report_error = None
    err_file = Path(f"{report_file}.error")
    if err_file.exists():
        try:
            report_error = err_file.read_text(encoding="utf-8").strip()
            report_integrity = False
            stderr += f"\n[PLUGIN_WRITE_ERROR] {report_error}"
        except Exception:
            pass

    if report_file.exists():
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                report_data = json.load(f)
            if not isinstance(report_data, dict) or "tests" not in report_data:
                report_integrity = False
                report_error = "Report JSON lacks expected 'tests' dictionary"
        except Exception as e:
            report_integrity = False
            report_error = f"Failed to read/parse report file: {e}"
            stderr += f"\nFailed to read report file: {e}"
    else:
        report_integrity = False
        if not report_error:
            report_error = f"Report file was not created (exit_code={exit_code})"

    if isinstance(report_data, dict):
        report_data["_integrity"] = report_integrity
        report_data["_report_error"] = report_error

    return exit_code, report_data, stdout, stderr


def execute_suite(
    test_target: Union[Path, str],
    cwd: Path,
    python_paths: Optional[List[str]] = None,
    mode: ExecutionMode = ExecutionMode.SUITE_IN_ORDER,
    seed: Optional[int] = None,
    timeout_per_test: int = 30,
    suite_timeout: int = 120,
    extra_env: Optional[dict] = None,
) -> SuiteExecutionResult:
    """
    Execute tests according to specified ExecutionMode:
    - SINGLE_TEST_ISOLATED: Every nodeid runs in a separate process.
    - SUITE_IN_ORDER: File-order execution in a single run.
    - SUITE_RANDOM: Nodeids shuffled deterministically by seed and passed in order.
    """
    start_total = time.perf_counter()
    target_str = str(test_target)

    # Discovery
    discovered_nodeids, discovery_errors = discover_test_nodeids(
        test_target, cwd=cwd, python_paths=python_paths, timeout=timeout_per_test
    )

    # ----------------------------------------------------
    # MODE 1: Single-Test Isolated Mode
    # ----------------------------------------------------
    if mode == ExecutionMode.SINGLE_TEST_ISOLATED:
        planned = list(discovered_nodeids)
        actual_order: List[str] = []
        test_results: Dict[str, TestExecutionResult] = {}
        individual_exit_codes: List[int] = []
        combined_stdout: List[str] = []
        combined_stderr: List[str] = []
        all_observed_nids: List[str] = []
        all_report_errors: List[str] = []

        if not planned and discovery_errors:
            total_duration = time.perf_counter() - start_total
            return SuiteExecutionResult(
                suite_target=target_str,
                execution_mode=mode.value,
                random_seed=seed,
                planned_order=[],
                actual_runtime_order=[],
                duration_seconds=round(total_duration, 4),
                collection_error_count=len(discovery_errors),
                collection_errors=discovery_errors,
                exit_code=1,
            )

        for nid in planned:
            actual_order.append(nid)
            with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
                tmp_rep = Path(tf.name)
            try:
                code, data, out, err = _run_pytest_with_plugin(
                    [nid], cwd=cwd, report_file=tmp_rep,
                    python_paths=python_paths, seed=seed, timeout=timeout_per_test, extra_env=extra_env
                )
                individual_exit_codes.append(code)
                if out:
                    combined_stdout.append(out)
                if err:
                    combined_stderr.append(err)
                if data.get("_report_error"):
                    all_report_errors.append(f"{nid}: {data['_report_error']}")

                tests_map = data.get("tests", {})
                for k in tests_map:
                    all_observed_nids.append(k)

                matched_k, t_info, status = find_test_in_report_data(nid, tests_map)

                if code == -1:
                    test_results[nid] = TestExecutionResult(
                        nodeid=nid,
                        outcome="TIMEOUT",
                        duration_seconds=float(timeout_per_test),
                        error_type="TIMEOUT",
                        error_message=f"Timeout after {timeout_per_test}s",
                    )
                elif t_info is not None:
                    test_results[nid] = TestExecutionResult(
                        nodeid=nid,
                        outcome=t_info.get("outcome", "PASSED"),
                        duration_seconds=round(t_info.get("duration", 0.0), 4),
                        error_type=t_info.get("error_type"),
                        error_message=t_info.get("error_message"),
                    )
                else:
                    # Neither timeout nor valid test report entry -> MISSING_OBSERVATION
                    test_results[nid] = TestExecutionResult(
                        nodeid=nid,
                        outcome="MISSING_OBSERVATION",
                        duration_seconds=0.0,
                        error_type="MISSING_OBSERVATION",
                        error_message=f"No observation recorded in structured report for {nid} (exit_code={code}, match_status={status}): {err[:300]}",
                    )
            finally:
                tmp_rep.unlink(missing_ok=True)

        total_duration = time.perf_counter() - start_total
        # Compute aggregate exit code across single-test runs
        if any(c == -1 for c in individual_exit_codes):
            agg_exit_code = -1
        elif any(c != 0 for c in individual_exit_codes):
            agg_exit_code = next(c for c in individual_exit_codes if c != 0)
        else:
            agg_exit_code = 0

        match_res = match_nodeids(planned, all_observed_nids)
        return _build_suite_result(
            suite_target=target_str,
            execution_mode=mode.value,
            random_seed=seed,
            planned_order=planned,
            actual_runtime_order=actual_order,
            duration_seconds=total_duration,
            test_results=test_results,
            collection_errors=discovery_errors,
            exit_code=agg_exit_code,
            planned_nodeids=match_res.planned_nodeids,
            observed_nodeids=match_res.observed_nodeids,
            missing_nodeids=match_res.missing,
            unknown_nodeids=match_res.unknown,
            duplicate_nodeids=match_res.duplicates,
            ambiguous_nodeids=match_res.ambiguous,
            stdout="\n".join(combined_stdout),
            stderr="\n".join(combined_stderr),
            report_integrity=len(all_report_errors) == 0,
            report_error="; ".join(all_report_errors) if all_report_errors else None,
        )

    # ----------------------------------------------------
    # MODE 2: Suite In-Order Mode
    # ----------------------------------------------------
    elif mode == ExecutionMode.SUITE_IN_ORDER:
        planned = list(discovered_nodeids)
        test_args = [target_str] if not planned else planned
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            tmp_rep = Path(tf.name)
        try:
            code, data, out, err = _run_pytest_with_plugin(
                test_args, cwd=cwd, report_file=tmp_rep,
                python_paths=python_paths, seed=seed, timeout=suite_timeout, extra_env=extra_env
            )
            total_duration = time.perf_counter() - start_total
            return _parse_suite_run(
                suite_target=target_str,
                execution_mode=mode.value,
                random_seed=seed,
                planned_order=planned,
                duration_seconds=total_duration,
                exit_code=code,
                data=data,
                stdout=out,
                stderr=err,
                timeout=suite_timeout,
                discovery_errors=discovery_errors,
            )
        finally:
            tmp_rep.unlink(missing_ok=True)

    # ----------------------------------------------------
    # MODE 3: Suite Randomized Mode
    # ----------------------------------------------------
    elif mode == ExecutionMode.SUITE_RANDOM:
        effective_seed = seed if seed is not None else 42
        planned = list(discovered_nodeids)
        rng = random.Random(effective_seed)
        rng.shuffle(planned)

        test_args = planned if planned else [target_str]
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            tmp_rep = Path(tf.name)
        try:
            code, data, out, err = _run_pytest_with_plugin(
                test_args, cwd=cwd, report_file=tmp_rep,
                python_paths=python_paths, seed=effective_seed, timeout=suite_timeout, extra_env=extra_env
            )
            total_duration = time.perf_counter() - start_total
            return _parse_suite_run(
                suite_target=target_str,
                execution_mode=mode.value,
                random_seed=effective_seed,
                planned_order=planned,
                duration_seconds=total_duration,
                exit_code=code,
                data=data,
                stdout=out,
                stderr=err,
                timeout=suite_timeout,
                discovery_errors=discovery_errors,
            )
        finally:
            tmp_rep.unlink(missing_ok=True)

    else:
        raise ValueError(f"Unknown execution mode: {mode}")


def _parse_suite_run(
    suite_target: str,
    execution_mode: str,
    random_seed: Optional[int],
    planned_order: List[str],
    duration_seconds: float,
    exit_code: int,
    data: dict,
    stdout: str,
    stderr: str,
    timeout: int,
    discovery_errors: List[dict],
) -> SuiteExecutionResult:
    """
    Construct SuiteExecutionResult from whole-suite execution run using unified NodeID matching.
    On crashes/timeouts: Uses incremental records to distinguish completed tests,
    actively executing test, and unexecuted planned tests.
    """
    coll_errors = list(discovery_errors) + data.get("collection_errors", [])
    test_map = data.get("tests", {})
    runtime_order = data.get("runtime_order", [])
    active_test = data.get("active_test")
    test_results: Dict[str, TestExecutionResult] = {}

    match_res = match_nodeids(planned_order, list(test_map.keys()))

    # 1. Populate matched tests
    for p_nid, o_nid in match_res.matched.items():
        info = test_map.get(o_nid, {})
        test_results[p_nid] = TestExecutionResult(
            nodeid=p_nid,
            outcome=info.get("outcome", "PASSED"),
            duration_seconds=round(info.get("duration", 0.0), 4),
            error_type=info.get("error_type"),
            error_message=info.get("error_message"),
        )

    # Populate any unknown tests observed in report that were not in planned
    for u_nid in match_res.unknown:
        if u_nid not in test_results:
            info = test_map.get(u_nid, {})
            test_results[u_nid] = TestExecutionResult(
                nodeid=u_nid,
                outcome=info.get("outcome", "PASSED"),
                duration_seconds=round(info.get("duration", 0.0), 4),
                error_type=info.get("error_type"),
                error_message=info.get("error_message"),
            )

    # 2. Handle timeout or abnormal exit for missing / unreached tests
    if exit_code == -1:
        if active_test and active_test not in test_results:
            test_results[active_test] = TestExecutionResult(
                nodeid=active_test, outcome="TIMEOUT", duration_seconds=float(timeout),
                error_type="TIMEOUT", error_message=f"Timed out while actively executing after {timeout}s",
            )
        for nid in match_res.missing:
            if nid not in test_results:
                test_results[nid] = TestExecutionResult(
                    nodeid=nid, outcome="NOT_EXECUTED", duration_seconds=0.0,
                    error_type="NOT_EXECUTED", error_message="Suite timed out before this test was reached",
                )
    elif exit_code != 0 and len(test_results) < len(planned_order):
        if active_test and active_test not in test_results:
            test_results[active_test] = TestExecutionResult(
                nodeid=active_test, outcome="EXCEPTION", duration_seconds=0.0,
                error_type="PROCESS_ABORT", error_message=f"Process aborted while executing this test: {stderr[:300]}",
            )
        for nid in match_res.missing:
            if nid not in test_results:
                test_results[nid] = TestExecutionResult(
                    nodeid=nid, outcome="NOT_EXECUTED", duration_seconds=0.0,
                    error_type="NOT_EXECUTED", error_message="Suite process aborted before test was reached",
                )
    elif not test_results and not coll_errors:
        for nid in match_res.missing:
            test_results[nid] = TestExecutionResult(
                nodeid=nid, outcome="MISSING_OBSERVATION", duration_seconds=0.0,
                error_type="MISSING_OBSERVATION", error_message=f"No structured report captured (exit_code={exit_code})",
            )
    else:
        for nid in match_res.missing:
            test_results[nid] = TestExecutionResult(
                nodeid=nid, outcome="MISSING_OBSERVATION", duration_seconds=0.0,
                error_type="MISSING_OBSERVATION", error_message=f"Planned test not observed in suite report (exit_code={exit_code})",
            )

    # Record ambiguous nodes explicitly
    for a_nid in match_res.ambiguous:
        if a_nid not in test_results:
            test_results[a_nid] = TestExecutionResult(
                nodeid=a_nid, outcome="MISSING_OBSERVATION", duration_seconds=0.0,
                error_type="AMBIGUOUS_NODEID", error_message=f"Ambiguous NodeID candidates detected in report for {a_nid}",
            )

    return _build_suite_result(
        suite_target=suite_target,
        execution_mode=execution_mode,
        random_seed=random_seed,
        planned_order=planned_order,
        actual_runtime_order=runtime_order,
        duration_seconds=duration_seconds,
        test_results=test_results,
        collection_errors=coll_errors,
        exit_code=exit_code,
        planned_nodeids=match_res.planned_nodeids,
        observed_nodeids=match_res.observed_nodeids,
        missing_nodeids=match_res.missing,
        unknown_nodeids=match_res.unknown,
        duplicate_nodeids=match_res.duplicates,
        ambiguous_nodeids=match_res.ambiguous,
        stdout=stdout,
        stderr=stderr,
        report_integrity=data.get("_integrity", True),
        report_error=data.get("_report_error"),
    )


def _build_suite_result(
    suite_target: str,
    execution_mode: str,
    random_seed: Optional[int],
    planned_order: List[str],
    actual_runtime_order: List[str],
    duration_seconds: float,
    test_results: Dict[str, TestExecutionResult],
    collection_errors: List[dict],
    exit_code: Optional[int] = None,
    planned_nodeids: Optional[List[str]] = None,
    observed_nodeids: Optional[List[str]] = None,
    missing_nodeids: Optional[List[str]] = None,
    unknown_nodeids: Optional[List[str]] = None,
    duplicate_nodeids: Optional[List[str]] = None,
    ambiguous_nodeids: Optional[List[str]] = None,
    stdout: str = "",
    stderr: str = "",
    report_path: Optional[str] = None,
    report_integrity: bool = True,
    report_error: Optional[str] = None,
) -> SuiteExecutionResult:
    """Aggregate fine-grained counts and return full SuiteExecutionResult."""
    passed = sum(1 for t in test_results.values() if t.outcome == "PASSED")
    assert_fail = sum(1 for t in test_results.values() if t.outcome == "ASSERTION_FAILED")
    import_err = sum(1 for t in test_results.values() if t.outcome == "IMPORT_ERROR")
    coll_err = len(collection_errors) + sum(1 for t in test_results.values() if t.outcome == "COLLECTION_ERROR")
    timed_out = sum(1 for t in test_results.values() if t.outcome == "TIMEOUT")
    skipped = sum(1 for t in test_results.values() if t.outcome == "SKIPPED")
    exc_err = sum(1 for t in test_results.values() if t.outcome == "EXCEPTION")
    not_exec = sum(1 for t in test_results.values() if t.outcome == "NOT_EXECUTED")
    missing = sum(1 for t in test_results.values() if t.outcome == "MISSING_OBSERVATION")
    valid_obs = sum(1 for t in test_results.values() if t.is_valid_observation)

    return SuiteExecutionResult(
        suite_target=suite_target,
        execution_mode=execution_mode,
        random_seed=random_seed,
        planned_order=planned_order,
        actual_runtime_order=actual_runtime_order,
        duration_seconds=round(duration_seconds, 4),
        total_planned_tests=len(planned_order) if planned_order else len(test_results),
        valid_observations_count=valid_obs,
        missing_observations_count=missing,
        passed_count=passed,
        assertion_failed_count=assert_fail,
        import_error_count=import_err,
        collection_error_count=coll_err,
        timeout_count=timed_out,
        skipped_count=skipped,
        exception_count=exc_err,
        not_executed_count=not_exec,
        tests=test_results,
        collection_errors=collection_errors,
        exit_code=exit_code,
        planned_nodeids=planned_nodeids if planned_nodeids is not None else list(planned_order),
        observed_nodeids=observed_nodeids if observed_nodeids is not None else list(test_results.keys()),
        missing_nodeids=missing_nodeids if missing_nodeids is not None else [],
        unknown_nodeids=unknown_nodeids if unknown_nodeids is not None else [],
        duplicate_nodeids=duplicate_nodeids if duplicate_nodeids is not None else [],
        ambiguous_nodeids=ambiguous_nodeids if ambiguous_nodeids is not None else [],
        stdout=stdout,
        stderr=stderr,
        report_path=report_path,
        report_integrity=report_integrity,
        report_error=report_error,
    )
