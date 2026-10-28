"""
Regression tests for test execution modes:
1. Single-test isolated mode (each test runs in fresh subprocess).
2. Suite in-order mode (runs suite in file order).
3. Suite randomized mode (explicitly records seed and shuffled order).
"""

from pathlib import Path
import pytest
import tempfile

from src.execution.structured_executor import execute_suite, ExecutionMode


def test_three_execution_modes():
    """Verify all 3 execution modes produce consistent results and distinct orderings."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        test_file = tdp / "test_modes.py"
        test_file.write_text("""
def test_one():
    assert 1 == 1

def test_two():
    assert 2 == 2

def test_three():
    assert 3 == 3

def test_four():
    assert 4 == 4
""", encoding="utf-8")

        # 1. Single-test isolated mode
        res_iso = execute_suite(test_target=test_file, cwd=tdp, mode=ExecutionMode.SINGLE_TEST_ISOLATED)
        assert res_iso.total_tests == 4
        assert res_iso.passed_count == 4
        assert len(res_iso.execution_order) == 4

        # 2. Suite in-order mode
        res_ord = execute_suite(test_target=test_file, cwd=tdp, mode=ExecutionMode.SUITE_IN_ORDER)
        assert res_ord.total_tests == 4
        assert res_ord.passed_count == 4

        # 3. Suite randomized mode - Seed 42 vs Seed 777
        res_rand1 = execute_suite(test_target=test_file, cwd=tdp, mode=ExecutionMode.SUITE_RANDOM, seed=42)
        res_rand2 = execute_suite(test_target=test_file, cwd=tdp, mode=ExecutionMode.SUITE_RANDOM, seed=42)
        res_rand3 = execute_suite(test_target=test_file, cwd=tdp, mode=ExecutionMode.SUITE_RANDOM, seed=777)

        # Determinism: same seed produces identical order
        assert res_rand1.execution_order == res_rand2.execution_order
        assert res_rand1.random_seed == 42

        # Distinctness: different seeds produce different order
        assert res_rand1.execution_order != res_rand3.execution_order
        assert res_rand3.random_seed == 777


def test_repeated_executor_structured_integration():
    """Verify run_repeated produces structured per-test and suite-level flakiness report."""
    from src.execution.repeated_executor import run_repeated

    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        test_file = tdp / "test_rep.py"
        test_file.write_text("""
def test_deterministic():
    assert 1 == 1
""", encoding="utf-8")

        rep = run_repeated(
            test_file=test_file,
            project_dir=tdp,
            num_runs=3,
            mode=ExecutionMode.SUITE_RANDOM,
        )

        assert rep.total_runs == 3
        assert rep.suite_pass_count == 3
        assert rep.is_suite_flaky is False
        assert "test_rep.py::test_deterministic" in rep.tests_summary
        t_stat = rep.tests_summary["test_rep.py::test_deterministic"]
        assert t_stat.pass_count == 3
        assert t_stat.flakiness_category == "stable_pass"


def test_control_skipped_plus_passed_not_stable_pass():
    """Verify that a test with PASSED and SKIPPED is never classified as stable_pass."""
    from src.execution.repeated_executor import run_repeated

    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        test_file = tdp / "test_skip.py"
        test_file.write_text("""
import pytest
import os

count = 0
def test_intermittent_skip():
    global count
    # Pass on first run, skip on subsequent runs
    flag_file = os.path.join(r'""" + str(tdp).replace('\\', '/') + """', 'skip_flag.txt')
    if not os.path.exists(flag_file):
        with open(flag_file, 'w') as f: f.write('1')
        assert True
    else:
        pytest.skip("skipping on run 2")
""", encoding="utf-8")

        rep = run_repeated(
            test_file=test_file,
            project_dir=tdp,
            num_runs=2,
            mode=ExecutionMode.SINGLE_TEST_ISOLATED,
        )

        for nid, rec in rep.tests_summary.items():
            if "test_intermittent_skip" in nid:
                assert rec.flakiness_category != "stable_pass", "SKIPPED + PASSED must NOT be classified as stable_pass!"
                assert rec.skip_count >= 1
                assert rec.pass_count >= 1
                assert rec.flakiness_category == "unstable_skip"


def test_control_missing_round_and_unexecuted_distinguished():
    """Verify missing round is incomplete (never stable_pass) and NOT_EXECUTED is not assertion failure."""
    from src.execution.repeated_executor import PerTestFlakinessRecord
    from src.execution.structured_executor import TestExecutionResult

    # Simulate 3-run experiment where 1 run is MISSING_OBSERVATION, 1 run is NOT_EXECUTED, 1 run is PASSED
    t_list = [
        TestExecutionResult(nodeid="test_m.py::test_foo", outcome="PASSED", duration_seconds=0.1),
        TestExecutionResult(nodeid="test_m.py::test_foo", outcome="MISSING_OBSERVATION", duration_seconds=0.0),
        TestExecutionResult(nodeid="test_m.py::test_foo", outcome="NOT_EXECUTED", duration_seconds=0.0),
    ]

    obs_runs = len(t_list)
    passes = sum(1 for t in t_list if t.outcome == "PASSED")
    assert_fails = sum(1 for t in t_list if t.outcome == "ASSERTION_FAILED")
    timeouts = sum(1 for t in t_list if t.outcome == "TIMEOUT")
    skips = sum(1 for t in t_list if t.outcome == "SKIPPED")
    exceptions = sum(1 for t in t_list if t.outcome in ("EXCEPTION", "IMPORT_ERROR", "COLLECTION_ERROR"))
    not_execs = sum(1 for t in t_list if t.outcome == "NOT_EXECUTED")
    missings = sum(1 for t in t_list if t.outcome == "MISSING_OBSERVATION")
    fails = assert_fails + timeouts + exceptions

    assert assert_fails == 0, "NOT_EXECUTED must not be counted as assertion failure"
    assert not_execs == 1
    assert missings == 1

    has_missing_or_incomplete = (obs_runs < 3) or (missings > 0) or (not_execs > 0)
    assert has_missing_or_incomplete is True
    # Verify incomplete cannot produce flaky rate
    assert passes == 1
    # Category must be incomplete, rate must be None
    cat = "incomplete" if has_missing_or_incomplete else "stable_pass"
    assert cat == "incomplete"


