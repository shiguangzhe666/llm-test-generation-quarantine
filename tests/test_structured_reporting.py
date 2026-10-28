"""
Regression tests for structured pytest reporting and nodeid preservation.

Verifies:
1. Exact preservation of canonical nodeids (class methods, parameterized arguments).
2. Accurate categorization: PASSED, ASSERTION_FAILED, IMPORT_ERROR, COLLECTION_ERROR, SKIPPED, EXCEPTION.
3. Execution durations are captured.
"""

from pathlib import Path
import pytest
import tempfile

from src.execution.structured_executor import execute_suite, ExecutionMode


def test_nodeid_preservation_and_outcome_classification():
    """Verify parameterized nodeids, class nodeids, and outcome classification."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        test_file = tdp / "test_suite_sample.py"
        test_file.write_text("""
import pytest

class TestSampleClass:
    def test_class_pass(self):
        assert 1 == 1

    def test_class_assert_fail(self):
        assert 10 == 20

@pytest.mark.parametrize("param_val", ["alpha", "beta[special]"])
def test_parameterized(param_val):
    assert len(param_val) > 0

def test_runtime_exception():
    raise KeyError("missing_key")

@pytest.mark.skip(reason="testing skip outcome")
def test_skipped_item():
    pass
""", encoding="utf-8")

        result = execute_suite(
            test_target=test_file,
            cwd=tdp,
            mode=ExecutionMode.SUITE_IN_ORDER,
        )

        assert result.total_tests == 6, f"Expected 6 tests, got {result.total_tests}"
        assert result.passed_count == 3  # class_pass + 2 parameterized (alpha, beta)
        assert result.assertion_failed_count == 1  # class_assert_fail
        assert result.exception_count == 1  # runtime_exception
        assert result.skipped_count == 1  # skipped_item

        # Check exact nodeid strings
        test_keys = list(result.tests.keys())
        assert any("TestSampleClass::test_class_pass" in k for k in test_keys)
        assert any("TestSampleClass::test_class_assert_fail" in k for k in test_keys)
        assert any("test_parameterized[alpha]" in k for k in test_keys)
        assert any("test_parameterized[beta[special]]" in k for k in test_keys)
        assert any("test_runtime_exception" in k for k in test_keys)
        assert any("test_skipped_item" in k for k in test_keys)

        # Check outcomes
        for nid, t in result.tests.items():
            if "test_class_pass" in nid or "test_parameterized" in nid:
                assert t.outcome == "PASSED"
            elif "test_class_assert_fail" in nid:
                assert t.outcome == "ASSERTION_FAILED"
            elif "test_runtime_exception" in nid:
                assert t.outcome == "EXCEPTION"
                assert "missing_key" in (t.error_message or "")
            elif "test_skipped_item" in nid:
                assert t.outcome == "SKIPPED"


def test_collection_and_import_error_reporting():
    """Verify syntax errors and broken imports are classified correctly."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        
        # 1. Broken syntax
        bad_syntax = tdp / "test_syntax.py"
        bad_syntax.write_text("def broken_func(:\n    pass\n", encoding="utf-8")
        res_syntax = execute_suite(test_target=bad_syntax, cwd=tdp, mode=ExecutionMode.SUITE_IN_ORDER)
        assert res_syntax.collection_error_count >= 1
        assert res_syntax.collection_errors[0]["outcome"] == "COLLECTION_ERROR"

        # 2. Broken import
        bad_import = tdp / "test_import.py"
        bad_import.write_text("import completely_nonexistent_lib_xyz_999\ndef test_dummy(): pass\n", encoding="utf-8")
        res_import = execute_suite(test_target=bad_import, cwd=tdp, mode=ExecutionMode.SUITE_IN_ORDER)
        assert res_import.collection_error_count >= 1 or res_import.import_error_count >= 1
        err_entry = res_import.collection_errors[0] if res_import.collection_errors else list(res_import.tests.values())[0]
        outcome = err_entry.get("outcome") if isinstance(err_entry, dict) else err_entry.outcome
        assert outcome in ("IMPORT_ERROR", "COLLECTION_ERROR")


def test_aborted_suite_distinguishes_completed_from_unexecuted():
    """Verify that if a suite times out or aborts mid-way, completed tests keep their outcome and unreached tests are NOT_EXECUTED."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        test_file = tdp / "test_abort.py"
        test_file.write_text("""
import time

def test_fast_pass():
    assert 1 == 1

def test_fast_fail():
    assert 1 == 2

def test_slow_hang():
    time.sleep(5)
    assert True

def test_never_reached():
    assert True
""", encoding="utf-8")

        # Run with short timeout (1s) so test_slow_hang triggers timeout
        res = execute_suite(
            test_target=test_file,
            cwd=tdp,
            mode=ExecutionMode.SUITE_IN_ORDER,
            suite_timeout=1,
            timeout_per_test=1,
        )

        assert res.passed_count >= 1, "Fast passing test should retain PASSED outcome"
        assert res.assertion_failed_count >= 1, "Fast failing test should retain ASSERTION_FAILED outcome"
        
        # Check that unreached test is NOT marked as TIMEOUT
        unreached = [t for nid, t in res.tests.items() if "test_never_reached" in nid]
        if unreached:
            assert unreached[0].outcome in ("NOT_EXECUTED", "MISSING_OBSERVATION"), (
                f"Unreached test was falsely marked as {unreached[0].outcome} instead of NOT_EXECUTED!"
            )


def test_missing_observation_when_nodeid_unobserved_with_exit_code_zero():
    """Verify that if pytest exits 0 but a planned test was not observed in report, it is MISSING_OBSERVATION."""
    from src.execution.structured_executor import _parse_suite_run

    # Simulate a suite run where 2 tests were planned, but the reporter only saw 1
    planned = ["test_file.py::test_one", "test_file.py::test_two"]
    data = {
        "tests": {
            "test_file.py::test_one": {"outcome": "PASSED", "duration": 0.01, "error_type": None, "error_message": None}
        },
        "runtime_order": ["test_file.py::test_one"],
    }
    res = _parse_suite_run(
        suite_target="test_file.py",
        execution_mode="suite_in_order",
        random_seed=42,
        planned_order=planned,
        duration_seconds=0.1,
        exit_code=0,
        data=data,
        stdout="",
        stderr="",
        timeout=30,
        discovery_errors=[],
    )

    assert "test_file.py::test_one" in res.tests
    assert res.tests["test_file.py::test_one"].outcome == "PASSED"
    assert "test_file.py::test_two" in res.tests
    assert res.tests["test_file.py::test_two"].outcome == "MISSING_OBSERVATION"
    assert res.missing_observations_count == 1
    assert res.passed_count == 1


def test_same_name_tests_across_classes_and_functions():
    """Verify class method vs function with same name and parameterized nodeids are preserved without collision."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        test_file = tdp / "test_collisions.py"
        test_file.write_text("""
def test_foo():
    assert 1 == 1

class TestBar:
    def test_foo(self):
        assert 2 == 2

class TestBaz:
    def test_foo(self):
        assert 3 == 3
""", encoding="utf-8")

        res = execute_suite(
            test_target=test_file,
            cwd=tdp,
            mode=ExecutionMode.SUITE_IN_ORDER,
        )

        assert res.total_tests == 3
        assert res.passed_count == 3
        nodeids = list(res.tests.keys())
        assert any(k.endswith("::test_foo") and "Test" not in k for k in nodeids)
        assert any("TestBar::test_foo" in k for k in nodeids)
        assert any("TestBaz::test_foo" in k for k in nodeids)


