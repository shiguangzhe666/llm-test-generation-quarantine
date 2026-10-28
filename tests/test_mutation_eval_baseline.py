"""
Regression tests for mutation evaluation engine.

Verifies:
1. Baseline pre-check correctly identifies baseline failing tests and blocks them
   from being counted as legitimate kills (spurious kill prevention).
2. Legitimate kills are correctly attributed to tests that passed on baseline.
3. Denominator transparency: if valid mutants == 0, score is None ("Undefined").
4. Permission guard blocks direct in-place mutation of shared repos.
"""

from pathlib import Path
import pytest
import tempfile

from src.evaluation.mutation_eval import evaluate_mutation_score, is_in_shared_repos, PROJECT_ROOT


def test_baseline_precheck_blocks_false_kills():
    """Verify that a broken test failing on unmutated code cannot kill mutants."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        target = tdp / "sample_service.py"
        target.write_text("""
def check_boundary(val):
    if val >= 10:
        return "HIGH"
    return "LOW"
""", encoding="utf-8")

        test_file = tdp / "test_service.py"
        test_file.write_text("""
from sample_service import check_boundary

def test_boundary_good():
    # Valid test: passes on baseline, fails when val >= 10 mutated to val > 10
    assert check_boundary(10) == "HIGH"

def test_baseline_broken():
    # Flawed test: fails even on unmutated baseline!
    assert check_boundary(10) == "WRONG_OUTPUT_ALWAYS"
""", encoding="utf-8")

        report = evaluate_mutation_score(
            target_file=target,
            test_file=test_file,
            python_paths=[str(tdp)],
            cwd=tdp,
            max_mutants=5,
        )

        assert "test_service.py::test_boundary_good" in report.baseline_passing_tests
        assert "test_service.py::test_baseline_broken" in report.baseline_failing_tests
        assert report.false_kills_filtered_count >= 1

        # The broken test must NEVER appear as a legitimate killer in any mutant
        for m in report.mutants:
            assert "test_service.py::test_baseline_broken" not in m.killing_tests, (
                "Baseline-failing test was falsely recorded as a legitimate mutant killer!"
            )


def test_mutation_score_zero_denominator():
    """Verify score is reported as None / Undefined when 0 mutants can be generated."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        target = tdp / "empty_file.py"
        target.write_text("# Empty python file with no mutable AST operations\npass\n", encoding="utf-8")

        test_file = tdp / "test_empty.py"
        test_file.write_text("def test_pass(): pass\n", encoding="utf-8")

        report = evaluate_mutation_score(
            target_file=target,
            test_file=test_file,
            python_paths=[str(tdp)],
            cwd=tdp,
        )

        assert report.valid_mutants == 0
        assert report.mutation_score is None
        assert "Undefined" in report.mutation_score_str


def test_shared_repo_mutation_blocked_by_guard():
    """Verify that attempting to mutate a file inside data/repos raises PermissionError."""
    shared_file = PROJECT_ROOT / "data" / "repos" / "psf__requests" / "requests" / "sessions.py"
    if not shared_file.exists():
        pytest.skip("requests repo not cloned")

    assert is_in_shared_repos(shared_file) is True

    dummy_test = PROJECT_ROOT / "tests" / "test_structured_reporting.py"
    with pytest.raises(PermissionError) as exc_info:
        evaluate_mutation_score(
            target_file=shared_file,
            test_file=dummy_test,
        )
    assert "Direct mutation of shared repositories is strictly prohibited" in str(exc_info.value)
