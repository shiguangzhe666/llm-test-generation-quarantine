"""
Repeated Test Executor for Flakiness Detection.

Executes a test file or individual test nodeids N times using structured execution
under specified execution modes (SINGLE_TEST_ISOLATED, SUITE_IN_ORDER, SUITE_RANDOM).
Tracks pass/fail status, flakiness rate, error classification, and duration statistics.
"""

import argparse
import json
import math
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.execution.structured_executor import execute_suite, ExecutionMode, SuiteExecutionResult, TestExecutionResult


@dataclass
class SingleRunSummary:
    """Summary of one repetition run."""
    run_id: int
    seed: Optional[int]
    passed: bool
    duration_seconds: float
    total_tests: int
    passed_count: int
    failed_count: int
    error_count: int
    execution_order: List[str]
    missing_count: int = 0
    not_executed_count: int = 0
    exit_code: Optional[int] = None
    tests: Dict[str, dict] = field(default_factory=dict)


@dataclass
class PerTestFlakinessRecord:
    """Flakiness tracking for an individual canonical test nodeid."""
    nodeid: str
    planned_runs: int = 0
    observed_runs: int = 0
    total_runs: int = 0  # Alias for observed_runs for backward compatibility
    pass_count: int = 0
    assertion_fail_count: int = 0
    timeout_count: int = 0
    skip_count: int = 0
    exception_count: int = 0
    not_executed_count: int = 0
    missing_observation_count: int = 0
    fail_count: int = 0  # assertion_fail + timeout + exception
    is_flaky: bool = False
    flakiness_rate: Optional[float] = None
    flakiness_rate_str: str = "Undefined"
    flakiness_category: str = "unknown"  # stable_pass, stable_fail, rare_flaky, occasional_flaky, frequent_flaky, incomplete, unstable_skip, undefined
    error_types: List[str] = field(default_factory=list)
    duration_mean: float = 0.0


@dataclass
class RepeatedExecutionReport:
    """Aggregated report across N repetitions."""
    test_file: str
    project_dir: str
    execution_mode: str
    total_runs: int
    timestamp: str
    python_version: str
    runs: List[SingleRunSummary] = field(default_factory=list)
    tests_summary: Dict[str, PerTestFlakinessRecord] = field(default_factory=dict)
    suite_pass_count: int = 0
    suite_fail_count: int = 0
    is_suite_flaky: bool = False
    suite_flakiness_rate: Optional[float] = None
    suite_flakiness_rate_str: str = "Undefined"

    def to_dict(self) -> dict:
        return asdict(self)


def run_repeated(
    test_file: Union[Path, str],
    project_dir: Path,
    num_runs: int = 20,
    python_paths: Optional[List[str]] = None,
    mode: ExecutionMode = ExecutionMode.SUITE_RANDOM,
    timeout_per_test: int = 30,
    suite_timeout: int = 120,
    base_seed: int = 42,
) -> RepeatedExecutionReport:
    """
    Repeatedly execute a test target N times across seeds and aggregate results.
    """
    test_path = Path(test_file)
    proj_dir = Path(project_dir)

    report = RepeatedExecutionReport(
        test_file=str(test_file),
        project_dir=str(project_dir),
        execution_mode=mode.value,
        total_runs=num_runs,
        timestamp=datetime.now().isoformat(),
        python_version=sys.version.split()[0],
    )

    per_test_runs: Dict[str, List[TestExecutionResult]] = {}

    for i in range(num_runs):
        seed = base_seed + (i * 7919)
        run_res: SuiteExecutionResult = execute_suite(
            test_target=test_path,
            cwd=proj_dir,
            python_paths=python_paths,
            mode=mode,
            seed=seed,
            timeout_per_test=timeout_per_test,
            suite_timeout=suite_timeout,
        )

        suite_passed = (run_res.assertion_failed_count == 0 and
                        run_res.import_error_count == 0 and
                        run_res.collection_error_count == 0 and
                        run_res.timeout_count == 0 and
                        run_res.exception_count == 0 and
                        run_res.missing_observations_count == 0 and
                        run_res.not_executed_count == 0 and
                        run_res.passed_count > 0)

        if suite_passed:
            report.suite_pass_count += 1
        else:
            report.suite_fail_count += 1

        run_summary = SingleRunSummary(
            run_id=i,
            seed=seed,
            passed=suite_passed,
            duration_seconds=run_res.duration_seconds,
            total_tests=run_res.total_planned_tests,
            passed_count=run_res.passed_count,
            failed_count=run_res.assertion_failed_count + run_res.timeout_count,
            error_count=run_res.import_error_count + run_res.collection_error_count + run_res.exception_count,
            execution_order=run_res.execution_order,
            missing_count=run_res.missing_observations_count,
            not_executed_count=run_res.not_executed_count,
            exit_code=run_res.exit_code,
            tests={k: asdict(v) for k, v in run_res.tests.items()},
        )
        report.runs.append(run_summary)

        # Accumulate per-test records
        for nid, t_res in run_res.tests.items():
            if nid not in per_test_runs:
                per_test_runs[nid] = []
            per_test_runs[nid].append(t_res)

    # Compute Suite-level flakiness
    if num_runs > 0:
        has_pass = report.suite_pass_count > 0
        has_fail = report.suite_fail_count > 0
        report.is_suite_flaky = has_pass and has_fail
        rate = round(min(report.suite_pass_count, report.suite_fail_count) / num_runs, 4)
        report.suite_flakiness_rate = rate
        report.suite_flakiness_rate_str = f"{rate:.1%}"
    else:
        report.suite_flakiness_rate = None
        report.suite_flakiness_rate_str = "Undefined (0 runs)"

    # Compute Per-test flakiness
    for nid, t_list in per_test_runs.items():
        passes = sum(1 for t in t_list if t.outcome == "PASSED")
        assert_fails = sum(1 for t in t_list if t.outcome == "ASSERTION_FAILED")
        timeouts = sum(1 for t in t_list if t.outcome == "TIMEOUT")
        skips = sum(1 for t in t_list if t.outcome == "SKIPPED")
        exceptions = sum(1 for t in t_list if t.outcome in ("EXCEPTION", "IMPORT_ERROR", "COLLECTION_ERROR"))
        not_execs = sum(1 for t in t_list if t.outcome == "NOT_EXECUTED")
        missings = sum(1 for t in t_list if t.outcome == "MISSING_OBSERVATION")
        fails = assert_fails + timeouts + exceptions
        valid_executions = passes + fails
        # Only true executions/observations count as observed_runs (never MISSING_OBSERVATION or NOT_EXECUTED)
        obs_runs = passes + fails + skips

        durations = [t.duration_seconds for t in t_list if t.outcome not in ("MISSING_OBSERVATION", "NOT_EXECUTED")]
        avg_dur = round(sum(durations) / max(len(durations), 1), 4)
        err_types = sorted(set(t.error_type for t in t_list if t.error_type))

        # Check for incomplete or missing rounds
        has_missing_or_incomplete = (obs_runs < num_runs) or (missings > 0) or (not_execs > 0)
        has_skips = skips > 0

        if has_missing_or_incomplete:
            # Cannot determine flakiness or stable_pass if rounds are missing or unobserved
            is_flaky = False
            t_rate = None
            t_rate_str = f"Undefined (incomplete: {obs_runs}/{num_runs} observed, missing={missings}, not_executed={not_execs})"
            cat = "incomplete"
        elif has_skips:
            # SKIPPED + PASSED != stable_pass
            is_flaky = False
            t_rate = None
            t_rate_str = f"Undefined (contains {skips} skips)"
            cat = "unstable_skip"
        elif valid_executions == num_runs:
            if passes == num_runs and fails == 0:
                is_flaky = False
                t_rate = 0.0
                t_rate_str = "0.0%"
                cat = "stable_pass"
            elif fails == num_runs and passes == 0:
                is_flaky = False
                t_rate = 0.0
                t_rate_str = "0.0%"
                cat = "stable_fail"
            elif passes > 0 and fails > 0:
                is_flaky = True
                t_rate = round(min(passes, fails) / valid_executions, 4)
                t_rate_str = f"{t_rate:.1%}"
                if t_rate < 0.1:
                    cat = "rare_flaky"
                elif t_rate < 0.3:
                    cat = "occasional_flaky"
                else:
                    cat = "frequent_flaky"
            else:
                is_flaky = False
                t_rate = None
                t_rate_str = "Undefined"
                cat = "undefined"
        else:
            is_flaky = False
            t_rate = None
            t_rate_str = "Undefined"
            cat = "undefined"

        report.tests_summary[nid] = PerTestFlakinessRecord(
            nodeid=nid,
            planned_runs=num_runs,
            observed_runs=obs_runs,
            total_runs=obs_runs,
            pass_count=passes,
            assertion_fail_count=assert_fails,
            timeout_count=timeouts,
            skip_count=skips,
            exception_count=exceptions,
            not_executed_count=not_execs,
            missing_observation_count=missings,
            fail_count=fails,
            is_flaky=is_flaky,
            flakiness_rate=t_rate,
            flakiness_rate_str=t_rate_str,
            flakiness_category=cat,
            error_types=err_types,
            duration_mean=avg_dur,
        )

    return report


def main():
    parser = argparse.ArgumentParser(description="Repeated test executor with structured reporting.")
    parser.add_argument("--test-file", required=True, help="Path to test file")
    parser.add_argument("--project-dir", default=".", help="Project root directory")
    parser.add_argument("--runs", type=int, default=20, help="Number of repetitions")
    parser.add_argument("--mode", default="suite_random", choices=["single_test_isolated", "suite_in_order", "suite_random"])
    parser.add_argument("--output", default=None, help="Output JSON report path")
    args = parser.parse_args()

    mode_map = {
        "single_test_isolated": ExecutionMode.SINGLE_TEST_ISOLATED,
        "suite_in_order": ExecutionMode.SUITE_IN_ORDER,
        "suite_random": ExecutionMode.SUITE_RANDOM,
    }

    report = run_repeated(
        test_file=args.test_file,
        project_dir=Path(args.project_dir),
        num_runs=args.runs,
        mode=mode_map[args.mode],
    )

    print(f"\nExecution Summary for {args.test_file}:")
    print(f"  Mode: {report.execution_mode}, Total Runs: {report.total_runs}")
    print(f"  Suite Flakiness: {report.is_suite_flaky} (Rate: {report.suite_flakiness_rate_str})")
    print(f"  Tests Monitored: {len(report.tests_summary)}")
    for nid, t_stat in report.tests_summary.items():
        print(f"    - {nid}: {t_stat.flakiness_category} (Pass: {t_stat.pass_count}/{t_stat.total_runs}, Rate: {t_stat.flakiness_rate_str})")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"Report saved to {out_path}")


if __name__ == "__main__":
    main()
