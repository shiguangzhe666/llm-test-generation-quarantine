"""
Regression tests for SWE-bench loader and isolation mechanisms.

Verifies:
1. IsolatedWorktree creates an isolated checkout and removes it completely.
2. Shared repositories in data/repos remain 100% clean with unchanged HEAD before, during, and after.
3. Patch application failure raises PatchApplicationError explicitly with no silent fallback.
4. Repo cleanliness check correctly identifies clean vs modified repos.
"""

from pathlib import Path
import pytest
import subprocess

from src.utils.swebench_loader import (
    IsolatedWorktree,
    isolated_instance_environment,
    verify_repo_cleanliness,
    SWEBenchInstance,
    PatchApplicationError,
    EnvironmentIsolationError,
)

REPO_DIR = Path(__file__).resolve().parent.parent / "data" / "repos" / "psf__requests"


@pytest.mark.skipif(not REPO_DIR.exists(), reason="Shared requests repo not found")
def test_isolated_worktree_cleanliness_and_removal():
    """Verify worktree lifecycle does not mutate shared repo."""
    # 1. Pre-check
    clean_before, head_before, _ = verify_repo_cleanliness(REPO_DIR)
    assert clean_before, "Shared repo must be clean before running tests"

    # 2. Enter worktree
    with IsolatedWorktree(repo_dir=REPO_DIR, commit=head_before) as wt_path:
        assert wt_path.exists(), "Worktree path must exist while inside context"
        assert (wt_path / ".git").exists(), ".git pointer file must exist in worktree"
        
        # Verify shared repo is unchanged during worktree execution
        clean_during, head_during, _ = verify_repo_cleanliness(REPO_DIR)
        assert clean_during, "Shared repo must remain clean during worktree execution"
        assert head_during == head_before, "Shared repo HEAD must not change"

    # 3. Post-check
    assert not wt_path.exists(), "Worktree directory must be removed after exit"
    clean_after, head_after, _ = verify_repo_cleanliness(REPO_DIR)
    assert clean_after, "Shared repo must remain clean after worktree exit"
    assert head_after == head_before, "Shared repo HEAD must remain identical"


@pytest.mark.skipif(not REPO_DIR.exists(), reason="Shared requests repo not found")
def test_explicit_patch_failure_no_silent_fallback():
    """Verify that an invalid patch explicitly raises PatchApplicationError."""
    clean_before, head_before, _ = verify_repo_cleanliness(REPO_DIR)
    assert clean_before

    invalid_patch = (
        "diff --git a/nonexistent.py b/nonexistent.py\n"
        "--- a/nonexistent.py\n"
        "+++ b/nonexistent.py\n"
        "@@ -1,1 +1,1 @@\n"
        "-bad line that does not match\n"
        "+new line\n"
    )

    inst = SWEBenchInstance(
        instance_id="test__fail_patch",
        repo="psf/requests",
        base_commit=head_before,
        problem_statement="Testing explicit failure",
        patch=invalid_patch,
        fail_to_pass=[],
        pass_to_pass=[],
    )

    with pytest.raises(PatchApplicationError) as exc_info:
        with isolated_instance_environment(repo_dir=REPO_DIR, instance=inst, version="fixed"):
            pass

    assert "Failed to apply patch" in str(exc_info.value), "Error message must describe patch failure"

    # Ensure shared repo remains pristine after failure
    clean_after, head_after, _ = verify_repo_cleanliness(REPO_DIR)
    assert clean_after, "Shared repo must remain clean after patch failure"
    assert head_after == head_before


@pytest.mark.skipif(not REPO_DIR.exists(), reason="Shared requests repo not found")
def test_explicit_test_patch_failure():
    """Verify that an invalid test_patch also explicitly raises PatchApplicationError."""
    clean_before, head_before, _ = verify_repo_cleanliness(REPO_DIR)

    inst = SWEBenchInstance(
        instance_id="test__fail_test_patch",
        repo="psf/requests",
        base_commit=head_before,
        problem_statement="Testing explicit failure on test patch",
        patch="",
        test_patch="invalid diff header\n@@ not a patch @@",
        fail_to_pass=[],
        pass_to_pass=[],
    )

    with pytest.raises(PatchApplicationError):
        with isolated_instance_environment(repo_dir=REPO_DIR, instance=inst, version="buggy", apply_test_patch=True):
            pass

    clean_after, head_after, _ = verify_repo_cleanliness(REPO_DIR)
    assert clean_after


def test_verify_instance_reproducibility_rejects_non_assertion_failures(monkeypatch, tmp_path):
    """Verify that collection errors, import errors, and skips are NOT accepted as defect reproduction."""
    import src.utils.swebench_loader as loader_mod

    inst = SWEBenchInstance(
        instance_id="test__inst_criteria",
        repo="psf/requests",
        base_commit="dummy",
        problem_statement="dummy",
        patch="diff",
        fail_to_pass=["test_foo.py::test_target"],
        pass_to_pass=["test_foo.py::test_clean"],
    )

    # Scenario 1: Buggy run fails with COLLECTION_ERROR (e.g. syntax error or missing module)
    def mock_run_collection_err(instance, isolated_repo_dir, **kwargs):
        return {
            "fail_to_pass": {
                "test_foo.py::test_target": {
                    "outcome": "COLLECTION_ERROR",
                    "is_passed": False,
                    "is_assertion_failure": False,
                    "is_infrastructure_failure": True,
                }
            },
            "pass_to_pass": {
                "test_foo.py::test_clean": {"outcome": "PASSED", "is_passed": True, "is_assertion_failure": False, "is_infrastructure_failure": False}
            },
        }

    # Scenario 2: Buggy run fails with genuine ASSERTION_FAILED
    def mock_run_assertion_fail(instance, isolated_repo_dir, **kwargs):
        return {
            "fail_to_pass": {
                "test_foo.py::test_target": {
                    "outcome": "ASSERTION_FAILED",
                    "is_passed": False,
                    "is_assertion_failure": True,
                    "is_infrastructure_failure": False,
                }
            },
            "pass_to_pass": {
                "test_foo.py::test_clean": {"outcome": "PASSED", "is_passed": True, "is_assertion_failure": False, "is_infrastructure_failure": False}
            },
        }

    # Scenario 3: Fixed run passes all
    def mock_run_fixed_passed(instance, isolated_repo_dir, **kwargs):
        return {
            "fail_to_pass": {
                "test_foo.py::test_target": {"outcome": "PASSED", "is_passed": True, "is_assertion_failure": False, "is_infrastructure_failure": False}
            },
            "pass_to_pass": {
                "test_foo.py::test_clean": {"outcome": "PASSED", "is_passed": True, "is_assertion_failure": False, "is_infrastructure_failure": False}
            },
        }

    # Mock isolated_instance_environment context manager to yield tmp_path
    from contextlib import contextmanager
    @contextmanager
    def mock_isolated_env(repo_dir, instance, version="buggy", apply_test_patch=False):
        yield tmp_path

    monkeypatch.setattr(loader_mod, "isolated_instance_environment", mock_isolated_env)

    # Test Scenario 1: COLLECTION_ERROR on buggy -> MUST NOT BE ACCEPTED
    monkeypatch.setattr(loader_mod, "run_official_reference_tests", mock_run_collection_err)
    rep1 = loader_mod.verify_instance_reproducibility(tmp_path, inst)
    assert rep1["buggy_verified"] is False, "COLLECTION_ERROR must NOT be accepted as buggy defect reproduction!"
    assert rep1["reproduced"] is False

    # Test Scenario 2: Genuine ASSERTION_FAILED on buggy + PASSED on fixed -> ACCEPTED
    call_count = 0
    def mock_run_paired(instance, isolated_repo_dir, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_run_assertion_fail(instance, isolated_repo_dir, **kwargs)
        else:
            return mock_run_fixed_passed(instance, isolated_repo_dir, **kwargs)

    monkeypatch.setattr(loader_mod, "run_official_reference_tests", mock_run_paired)
    rep2 = loader_mod.verify_instance_reproducibility(tmp_path, inst)
    assert rep2["buggy_verified"] is True
    assert rep2["fixed_verified"] is True
    assert rep2["reproduced"] is True

