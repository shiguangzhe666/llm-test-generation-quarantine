"""
Dedicated Control Test Cases for Mutation Evaluation and Test Execution.

Explicitly separates synthetic control test cases from real SWE-bench benchmark instances.
Covers:
1. Known Killable Mutant: Verified detection via assertion failure.
2. Known Surviving Mutant: Incomplete test assertion leaves mutant alive.
3. Baseline Failing Test: Filtered out so it cannot produce false kills.
4. Runtime Exception Test: Distinguishes EXCEPTION from ASSERTION_FAILED.
5. Missing Observation / Unexecuted Test: Handled cleanly during crashes/timeouts.
6. Baseline Stability / Flaky Filtering: Multi-run baseline blocks flaky tests from killer status.
"""

from pathlib import Path
import tempfile
import pytest

from src.execution.structured_executor import execute_suite, ExecutionMode
from src.evaluation.mutation_eval import evaluate_mutation_score, count_potential_mutations


def test_control_known_killable_and_surviving_mutants():
    """Verify that a thorough test kills a mutant while an incomplete test allows it to survive."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        
        target_file = tdp / "calculator.py"
        target_file.write_text("""
def is_positive(x):
    return x > 0

def unused_helper(y):
    return y == 42
""", encoding="utf-8")

        # Test only exercises is_positive, never unused_helper
        test_file = tdp / "test_calculator.py"
        test_file.write_text("""
from calculator import is_positive

def test_is_positive_true():
    assert is_positive(5) is True

def test_is_positive_false():
    assert is_positive(-5) is False
""", encoding="utf-8")

        report = evaluate_mutation_score(
            target_file=target_file,
            test_file=test_file,
            cwd=tdp,
            python_paths=[str(tdp)],
            execution_mode=ExecutionMode.SUITE_IN_ORDER,
            baseline_repetitions=2,
        )

        assert report.valid_mutants > 0
        assert report.killed_mutants >= 1, "Expected at least 1 killed mutant on is_positive"
        assert report.survived_mutants >= 1, "Expected at least 1 surviving mutant on unused_helper"
        assert report.false_kills_filtered_count == 0
        assert len(report.baseline_failing_tests) == 0


def test_control_baseline_failing_prevented_from_false_kill():
    """Verify that a test failing on the pristine baseline is NEVER credited with killing mutants."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)

        target_file = tdp / "service.py"
        target_file.write_text("""
def compute(x):
    return x + 1
""", encoding="utf-8")

        test_file = tdp / "test_service.py"
        test_file.write_text("""
from service import compute

def test_passing_spec():
    assert compute(2) == 3

def test_deliberate_baseline_fail():
    # This test is broken on the pristine code
    assert compute(2) == 9999
""", encoding="utf-8")

        report = evaluate_mutation_score(
            target_file=target_file,
            test_file=test_file,
            cwd=tdp,
            python_paths=[str(tdp)],
            execution_mode=ExecutionMode.SUITE_IN_ORDER,
            baseline_repetitions=2,
        )

        assert any("test_deliberate_baseline_fail" in t for t in report.baseline_failing_tests)
        assert any("test_passing_spec" in t for t in report.baseline_passing_tests)
        assert report.false_kills_filtered_count >= 1, "Baseline failing test should be registered as false killer"

        # Ensure deliberate_baseline_fail is NOT in killing_tests of any mutant
        for m in report.mutants:
            for killer in m.killing_tests:
                assert "test_deliberate_baseline_fail" not in killer


def test_control_runtime_exception_vs_assertion_failure():
    """Verify that runtime errors (e.g. ZeroDivisionError, KeyError) are not marked as PASSED or ASSERTION_FAILED."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)

        test_file = tdp / "test_exceptions.py"
        test_file.write_text("""
def test_normal_assertion_failure():
    assert 10 == 20

def test_zero_division():
    _ = 10 / 0

def test_key_error():
    d = {}
    _ = d["missing"]
""", encoding="utf-8")

        res = execute_suite(
            test_target=test_file,
            cwd=tdp,
            mode=ExecutionMode.SUITE_IN_ORDER,
        )

        assert res.assertion_failed_count == 1
        assert res.exception_count == 2
        for nid, t in res.tests.items():
            if "test_normal_assertion_failure" in nid:
                assert t.outcome == "ASSERTION_FAILED"
            elif "test_zero_division" in nid:
                assert t.outcome == "EXCEPTION"
                assert "ZeroDivisionError" in (t.error_type or "")
            elif "test_key_error" in nid:
                assert t.outcome == "EXCEPTION"
                assert "KeyError" in (t.error_type or "")


def test_control_baseline_flakiness_disqualification():
    """Verify that a test which fails on any baseline repetition is disqualified from baseline_passing."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)

        target_file = tdp / "stateful.py"
        target_file.write_text("counter = 0\ndef get_val(): return 42\n", encoding="utf-8")

        # Test uses a file on disk to pass on 1st run and fail on 2nd run
        flag_file = tdp / "run_flag.txt"
        test_file = tdp / "test_flaky_baseline.py"
        test_file.write_text(f"""
from pathlib import Path
flag = Path(r"{flag_file}")

def test_flaky_on_baseline():
    if not flag.exists():
        flag.write_text("done", encoding="utf-8")
        assert True
    else:
        assert False, "Failed on second run!"
""", encoding="utf-8")

        report = evaluate_mutation_score(
            target_file=target_file,
            test_file=test_file,
            cwd=tdp,
            python_paths=[str(tdp)],
            execution_mode=ExecutionMode.SUITE_IN_ORDER,
            baseline_repetitions=2,
        )

        # Because it fails on the 2nd repetition, it MUST NOT be in baseline_passing
        assert any("test_flaky_on_baseline" in t for t in report.baseline_failing_tests), (
            "Flaky baseline test must be disqualified and marked baseline_failing"
        )
        assert not any("test_flaky_on_baseline" in t for t in report.baseline_passing_tests)


def test_control_byte_level_restoration_verification():
    """Verify that after evaluating mutants, the target file retains exact byte-level SHA-256."""
    import hashlib

    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        target_file = tdp / "mod_restore.py"
        content = "def func_a(x):\n    return x == 10\n\ndef func_b(y):\n    return y + 5\n"
        target_file.write_text(content, encoding="utf-8")
        orig_sha = hashlib.sha256(target_file.read_bytes()).hexdigest()

        test_file = tdp / "test_mod_restore.py"
        test_file.write_text("""
from mod_restore import func_a
def test_a():
    assert func_a(10) is True
""", encoding="utf-8")

        report = evaluate_mutation_score(
            target_file=target_file,
            test_file=test_file,
            cwd=tdp,
            python_paths=[str(tdp)],
            max_mutants=5,
            baseline_repetitions=1,
        )

        after_sha = hashlib.sha256(target_file.read_bytes()).hexdigest()
        assert after_sha == orig_sha, f"Byte hash mismatch: expected {orig_sha}, got {after_sha}"
        assert report.valid_mutants > 0


def test_control_module_import_origin():
    """Verify verify_module_import_origin detects whether target module is imported from cwd/isolated path."""
    from src.evaluation.mutation_eval import verify_module_import_origin

    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        mod_file = tdp / "local_probe_module.py"
        mod_file.write_text("VAL = 12345\n", encoding="utf-8")

        res = verify_module_import_origin(
            target_file=mod_file,
            cwd=tdp,
            python_paths=[str(tdp)],
        )

        assert res["is_isolated"] is True, f"Expected module to be isolated: {res}"
        assert "local_probe_module" in res["origin_file"]

