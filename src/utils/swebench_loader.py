"""
SWE-bench Instance Loader and Isolated Execution Environment.

Loads SWE-bench Verified instances from HuggingFace, extracts patch metadata,
and provides strictly isolated execution environments (via Git worktrees)
to guarantee that shared benchmark repositories are treated as immutable,
read-only baseline mirrors.

Guarantees:
1. Zero mutation of data/repos (no git checkout, no in-place code swaps in shared repos).
2. Explicit failure upon patch application or build errors (NO silent fallbacks).
3. Official reference test validation (fail_to_pass / pass_to_pass).
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator, List, Optional, Tuple


# ---------- Custom Exceptions ----------

class SWEBenchError(Exception):
    """Base exception for SWE-bench operations."""
    pass


class PatchApplicationError(SWEBenchError):
    """Raised when a patch cannot be cleanly applied (no silent fallback allowed)."""
    pass


class EnvironmentIsolationError(SWEBenchError):
    """Raised when creating or removing an isolated worktree environment fails."""
    pass


# ---------- Data Structures ----------

@dataclass
class PatchedFile:
    """A file modified by the bug-fix patch."""
    filepath: str           # e.g. "requests/models.py"
    added_lines: List[str] = field(default_factory=list)
    removed_lines: List[str] = field(default_factory=list)
    hunks: List[dict] = field(default_factory=list)


@dataclass
class SWEBenchInstance:
    """Parsed SWE-bench instance with all metadata needed for empirical evaluation."""
    instance_id: str        # e.g. "psf__requests-1921"
    repo: str               # e.g. "psf/requests"
    base_commit: str        # commit hash of the buggy version
    problem_statement: str  # GitHub issue description
    patch: str              # the gold fix patch (unified diff)
    test_patch: str = ""    # patch containing ground-truth reference test(s)
    fail_to_pass: List[str] = field(default_factory=list) # tests that should FAIL on buggy, PASS on fixed
    pass_to_pass: List[str] = field(default_factory=list) # tests that should PASS on both versions
    version: str = ""

    # Derived fields
    patched_files: List[PatchedFile] = field(default_factory=list)
    target_functions: List[str] = field(default_factory=list)

    @property
    def repo_owner(self) -> str:
        return self.repo.split("/")[0]

    @property
    def repo_name(self) -> str:
        return self.repo.split("/")[1]

    @property
    def repo_key(self) -> str:
        return self.repo.replace("/", "__")


# ---------- Parsing Functions ----------

def parse_patch(patch_text: str) -> List[PatchedFile]:
    """Parse a unified diff into structured PatchedFile objects."""
    files = []
    current_file = None

    for line in patch_text.split("\n"):
        if line.startswith("diff --git"):
            match = re.search(r"b/(.+)$", line)
            if match:
                current_file = PatchedFile(filepath=match.group(1))
                files.append(current_file)
        elif line.startswith("@@") and current_file:
            hunk_match = re.search(
                r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)",
                line,
            )
            if hunk_match:
                current_file.hunks.append({
                    "old_start": int(hunk_match.group(1)),
                    "old_count": int(hunk_match.group(2) or 1),
                    "new_start": int(hunk_match.group(3)),
                    "new_count": int(hunk_match.group(4) or 1),
                    "context": hunk_match.group(5).strip(),
                })
        elif current_file:
            if line.startswith("+") and not line.startswith("+++"):
                current_file.added_lines.append(line[1:])
            elif line.startswith("-") and not line.startswith("---"):
                current_file.removed_lines.append(line[1:])

    return files


def extract_target_functions(patch_text: str) -> List[str]:
    """Extract function/class names from patch hunk headers."""
    functions = []
    for line in patch_text.split("\n"):
        if line.startswith("@@"):
            match = re.search(r"@@.*@@\s*(def |class )(\w+)", line)
            if match:
                functions.append(match.group(2))
    return list(set(functions))


def load_swebench_instances(
    dataset_name: str = "princeton-nlp/SWE-bench_Verified",
    split: str = "test",
    instance_ids: Optional[List[str]] = None,
    repos: Optional[List[str]] = None,
) -> List[SWEBenchInstance]:
    """Load SWE-bench instances from HuggingFace dataset."""
    from datasets import load_dataset

    print(f"Loading {dataset_name} ({split} split)...")
    os.environ.setdefault("NO_PROXY", "*")

    ds = load_dataset(dataset_name, split=split)
    print(f"  Total instances in split: {len(ds)}")

    instances = []
    for item in ds:
        iid = item["instance_id"]
        repo = item["repo"]

        if instance_ids and iid not in instance_ids:
            continue
        if repos and repo not in repos:
            continue

        fail_to_pass = json.loads(item.get("FAIL_TO_PASS", "[]"))
        pass_to_pass = json.loads(item.get("PASS_TO_PASS", "[]"))
        patch = item.get("patch", "")
        test_patch = item.get("test_patch", "")

        instance = SWEBenchInstance(
            instance_id=iid,
            repo=repo,
            base_commit=item.get("base_commit", ""),
            problem_statement=item.get("problem_statement", ""),
            patch=patch,
            test_patch=test_patch,
            fail_to_pass=fail_to_pass,
            pass_to_pass=pass_to_pass,
            version=item.get("version", ""),
            patched_files=parse_patch(patch),
            target_functions=extract_target_functions(patch),
        )
        instances.append(instance)

    print(f"  Loaded {len(instances)} matching instances")
    return instances


# ---------- Shared Repository & Isolation Management ----------

def verify_repo_cleanliness(repo_dir: Path) -> Tuple[bool, str, str]:
    """
    Verify that the shared repository is clean (no modified or untracked files).
    Returns (is_clean, head_commit, status_output).
    """
    if not repo_dir.exists():
        return False, "", "Repository directory does not exist"

    try:
        head_res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=10, check=True
        )
        head_commit = head_res.stdout.strip()
    except Exception as e:
        return False, "", f"Failed to get HEAD commit: {e}"

    try:
        status_res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=10, check=True
        )
        status_out = status_res.stdout.strip()
        is_clean = len(status_out) == 0
        return is_clean, head_commit, status_out
    except Exception as e:
        return False, head_commit, f"Failed to check git status: {e}"


class IsolatedWorktree:
    """
    Context manager that creates an isolated Git worktree from a shared repo
    at a specific commit, ensuring the shared repo is never modified.
    Automatically cleans up the worktree on exit.
    """

    def __init__(self, repo_dir: Path, commit: str, base_temp_dir: Optional[Path] = None):
        self.repo_dir = repo_dir
        self.commit = commit
        self.base_temp_dir = base_temp_dir
        self.worktree_dir: Optional[Path] = None

    def __enter__(self) -> Path:
        if not self.repo_dir.exists():
            raise EnvironmentIsolationError(f"Shared repository not found: {self.repo_dir}")

        # Create temporary directory for the worktree
        temp_dir = tempfile.mkdtemp(prefix="swebench_wt_", dir=str(self.base_temp_dir) if self.base_temp_dir else None)
        self.worktree_dir = Path(temp_dir)

        # Remove the directory itself because git worktree add expects to create it
        try:
            self.worktree_dir.rmdir()
        except OSError:
            pass

        cmd = [
            "git", "worktree", "add", "--detach",
            str(self.worktree_dir),
            self.commit
        ]
        res = subprocess.run(
            cmd, cwd=str(self.repo_dir), capture_output=True, text=True, timeout=60
        )
        if res.returncode != 0:
            shutil.rmtree(self.worktree_dir, ignore_errors=True)
            raise EnvironmentIsolationError(
                f"Failed to create git worktree at {self.commit} from {self.repo_dir}:\n"
                f"STDOUT: {res.stdout}\nSTDERR: {res.stderr}"
            )

        return self.worktree_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.worktree_dir and self.worktree_dir.exists():
            # Force remove worktree from git registry
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(self.worktree_dir)],
                cwd=str(self.repo_dir), capture_output=True, text=True, timeout=30
            )
            # Prune any stale worktree entries
            subprocess.run(
                ["git", "worktree", "prune"],
                cwd=str(self.repo_dir), capture_output=True, text=True, timeout=30
            )
            # Ensure folder is wiped
            shutil.rmtree(self.worktree_dir, ignore_errors=True)


@contextmanager
def isolated_instance_environment(
    repo_dir: Path,
    instance: SWEBenchInstance,
    version: str = "buggy",
    apply_test_patch: bool = False,
    base_temp_dir: Optional[Path] = None,
) -> Generator[Path, None, None]:
    """
    Creates an isolated environment for an instance.
    - version="buggy": Checks out base_commit in an isolated worktree.
    - version="fixed": Checks out base_commit in worktree and applies instance.patch.
      If patch application fails, raises PatchApplicationError explicitly (NO SILENT FALLBACK).
    - apply_test_patch=True: Also applies instance.test_patch (official ground-truth reference test).
      If test_patch application fails, raises PatchApplicationError explicitly.
    """
    if version not in ("buggy", "fixed"):
        raise ValueError(f"version must be 'buggy' or 'fixed', got '{version}'")

    with IsolatedWorktree(repo_dir=repo_dir, commit=instance.base_commit, base_temp_dir=base_temp_dir) as wt_path:
        # Apply official test patch if requested (e.g. for ground-truth reference evaluation)
        if apply_test_patch and instance.test_patch:
            apply_test_res = subprocess.run(
                ["git", "apply", "--ignore-whitespace", "--ignore-space-change"],
                input=instance.test_patch,
                cwd=str(wt_path),
                capture_output=True, text=True, timeout=30,
            )
            if apply_test_res.returncode != 0:
                raise PatchApplicationError(
                    f"Failed to apply test_patch for instance {instance.instance_id} in isolated worktree:\n"
                    f"STDOUT: {apply_test_res.stdout}\nSTDERR: {apply_test_res.stderr}\n"
                    f"Test Patch (first 200 chars): {instance.test_patch[:200]}"
                )

        if version == "fixed":
            # Apply the gold patch
            apply_res = subprocess.run(
                ["git", "apply", "--ignore-whitespace", "--ignore-space-change"],
                input=instance.patch,
                cwd=str(wt_path),
                capture_output=True, text=True, timeout=30,
            )
            if apply_res.returncode != 0:
                raise PatchApplicationError(
                    f"Failed to apply patch for instance {instance.instance_id} in isolated worktree:\n"
                    f"STDOUT: {apply_res.stdout}\nSTDERR: {apply_res.stderr}\n"
                    f"Patch (first 200 chars): {instance.patch[:200]}"
                )

        yield wt_path


def extract_source_at_commits(
    repo_dir: Path,
    instance: SWEBenchInstance,
    output_dir: Path,
) -> dict:
    """
    Extract source files at both fixed and buggy versions using isolated worktrees.
    Shared repository is completely untouched.
    """
    result = {"fixed_dir": None, "buggy_dir": None, "files": []}

    fixed_dir = output_dir / "fixed"
    buggy_dir = output_dir / "buggy"
    fixed_dir.mkdir(parents=True, exist_ok=True)
    buggy_dir.mkdir(parents=True, exist_ok=True)

    # 1. Extract Buggy Version from isolated worktree
    with isolated_instance_environment(repo_dir=repo_dir, instance=instance, version="buggy") as buggy_wt:
        for pf in instance.patched_files:
            fname = pf.filepath.split("/")[-1].lower()
            if fname.startswith("test_") or fname.endswith("_test.py") or fname.startswith("conftest"):
                continue

            src_path = buggy_wt / pf.filepath
            if not src_path.exists():
                continue

            target_file = buggy_dir / pf.filepath
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(src_path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
            result["files"].append(pf.filepath)

    # 2. Extract Fixed Version from isolated worktree
    with isolated_instance_environment(repo_dir=repo_dir, instance=instance, version="fixed") as fixed_wt:
        for pf in instance.patched_files:
            fname = pf.filepath.split("/")[-1].lower()
            if fname.startswith("test_") or fname.endswith("_test.py") or fname.startswith("conftest"):
                continue

            src_path = fixed_wt / pf.filepath
            if not src_path.exists():
                continue

            target_file = fixed_dir / pf.filepath
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(src_path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

    result["fixed_dir"] = str(fixed_dir)
    result["buggy_dir"] = str(buggy_dir)
    return result


def run_official_reference_tests(
    instance: SWEBenchInstance,
    isolated_repo_dir: Path,
    python_paths: Optional[List[str]] = None,
    pass_to_pass_tests: Optional[List[str]] = None,
    timeout: int = 60,
) -> dict:
    """
    Execute SWE-bench official ground-truth reference tests (fail_to_pass and pass_to_pass)
    in the isolated repository environment.
    Strictly distinguishes genuine ASSERTION_FAILED from COLLECTION_ERROR, IMPORT_ERROR,
    TIMEOUT, and SKIPPED.
    """
    from src.execution.structured_executor import execute_suite, ExecutionMode

    paths = list(python_paths or [])
    paths.insert(0, str(isolated_repo_dir))

    results = {
        "fail_to_pass": {},
        "pass_to_pass": {},
        "pass_to_pass_scope": {
            "total_in_instance": len(instance.pass_to_pass),
            "evaluated_in_run": len(pass_to_pass_tests) if pass_to_pass_tests is not None else len(instance.pass_to_pass),
            "is_full_set": pass_to_pass_tests is None or len(pass_to_pass_tests) == len(instance.pass_to_pass),
        }
    }

    # 1. Run fail_to_pass tests
    for t_spec in instance.fail_to_pass:
        res = execute_suite(
            test_target=t_spec,
            cwd=isolated_repo_dir,
            python_paths=paths,
            mode=ExecutionMode.SINGLE_TEST_ISOLATED,
            timeout_per_test=timeout,
        )
        t_obj = next(iter(res.tests.values())) if res.tests else None
        if t_obj:
            outcome = t_obj.outcome
            err_msg = t_obj.error_message
        elif res.collection_errors:
            outcome = res.collection_errors[0].get("outcome", "COLLECTION_ERROR")
            err_msg = res.collection_errors[0].get("error_message")
        else:
            outcome = "UNKNOWN_ERROR"
            err_msg = "No test results recorded"

        results["fail_to_pass"][t_spec] = {
            "nodeid": t_spec,
            "outcome": outcome,
            "is_passed": outcome == "PASSED",
            "is_assertion_failure": outcome == "ASSERTION_FAILED",
            "is_infrastructure_failure": outcome in ("COLLECTION_ERROR", "IMPORT_ERROR", "TIMEOUT", "SKIPPED"),
            "duration_seconds": res.duration_seconds,
            "error_message": err_msg,
        }

    # 2. Run pass_to_pass tests (default to full list, or caller-specified protocol subset)
    ptp_target_list = pass_to_pass_tests if pass_to_pass_tests is not None else instance.pass_to_pass
    for t_spec in ptp_target_list:
        res = execute_suite(
            test_target=t_spec,
            cwd=isolated_repo_dir,
            python_paths=paths,
            mode=ExecutionMode.SINGLE_TEST_ISOLATED,
            timeout_per_test=timeout,
        )
        t_obj = next(iter(res.tests.values())) if res.tests else None
        if t_obj:
            outcome = t_obj.outcome
            err_msg = t_obj.error_message
        elif res.collection_errors:
            outcome = res.collection_errors[0].get("outcome", "COLLECTION_ERROR")
            err_msg = res.collection_errors[0].get("error_message")
        else:
            outcome = "UNKNOWN_ERROR"
            err_msg = "No test results recorded"

        results["pass_to_pass"][t_spec] = {
            "nodeid": t_spec,
            "outcome": outcome,
            "is_passed": outcome == "PASSED",
            "is_assertion_failure": outcome == "ASSERTION_FAILED",
            "is_infrastructure_failure": outcome in ("COLLECTION_ERROR", "IMPORT_ERROR", "TIMEOUT", "SKIPPED"),
            "duration_seconds": res.duration_seconds,
            "error_message": err_msg,
        }

    return results


def verify_instance_reproducibility(
    repo_dir: Path,
    instance: SWEBenchInstance,
    conftest_shim: Optional[str] = None,
    pass_to_pass_tests: Optional[List[str]] = None,
    timeout: int = 60,
) -> dict:
    """
    End-to-end ground truth validation under strict scientific criteria:
    1. Buggy environment:
       - FAIL_TO_PASS tests MUST produce ASSERTION_FAILED (collection errors or timeouts do NOT count).
       - PASS_TO_PASS tests MUST produce PASSED (regression baseline check).
    2. Fixed environment:
       - FAIL_TO_PASS tests MUST produce PASSED.
       - PASS_TO_PASS tests MUST produce PASSED.
    3. Conftest shims and patch hashes are recorded for full auditability.
    4. Shared repository in repo_dir remains completely untouched.
    """
    import hashlib

    shim_hash = hashlib.sha256(conftest_shim.encode("utf-8")).hexdigest() if conftest_shim else None
    patch_hash = hashlib.sha256(instance.patch.encode("utf-8")).hexdigest() if instance.patch else None
    test_patch_hash = hashlib.sha256(instance.test_patch.encode("utf-8")).hexdigest() if instance.test_patch else None

    report = {
        "instance_id": instance.instance_id,
        "base_commit": instance.base_commit,
        "patch_sha256": patch_hash,
        "test_patch_sha256": test_patch_hash,
        "conftest_shim_sha256": shim_hash,
        "buggy_verified": False,
        "fixed_verified": False,
        "reproduced": False,
        "verdict_reasons": [],
        "buggy_details": {},
        "fixed_details": {},
    }

    # ----------------------------------------------------
    # Phase 1: Buggy Environment (base_commit + test_patch)
    # ----------------------------------------------------
    with isolated_instance_environment(repo_dir=repo_dir, instance=instance, version="buggy", apply_test_patch=True) as buggy_wt:
        if conftest_shim:
            (buggy_wt / "conftest.py").write_text(conftest_shim, encoding="utf-8")
        buggy_res = run_official_reference_tests(
            instance, buggy_wt, pass_to_pass_tests=pass_to_pass_tests, timeout=timeout
        )
        report["buggy_details"] = buggy_res

    # Strict buggy verification check:
    buggy_ftps = buggy_res["fail_to_pass"]
    buggy_ptps = buggy_res["pass_to_pass"]

    buggy_assertion_fails = [k for k, v in buggy_ftps.items() if v["outcome"] == "ASSERTION_FAILED"]
    buggy_infra_errors = [k for k, v in buggy_ftps.items() if v["is_infrastructure_failure"]]
    buggy_passed_ftps = [k for k, v in buggy_ftps.items() if v["is_passed"]]
    buggy_failed_ptps = [k for k, v in buggy_ptps.items() if not v["is_passed"]]

    if not buggy_assertion_fails:
        report["verdict_reasons"].append(
            f"Buggy run FAILED: 0 of {len(buggy_ftps)} FAIL_TO_PASS tests produced ASSERTION_FAILED "
            f"(Passed: {len(buggy_passed_ftps)}, Infra errors: {len(buggy_infra_errors)})."
        )
    if buggy_infra_errors:
        report["verdict_reasons"].append(
            f"Buggy run encountered infrastructure/collection errors on FAIL_TO_PASS: {buggy_infra_errors}."
        )
    if buggy_failed_ptps:
        report["verdict_reasons"].append(
            f"Buggy run FAILED baseline check: {len(buggy_failed_ptps)} PASS_TO_PASS tests failed: {buggy_failed_ptps}."
        )

    buggy_verified = (
        len(buggy_assertion_fails) > 0 and
        len(buggy_infra_errors) == 0 and
        len(buggy_failed_ptps) == 0
    )
    report["buggy_verified"] = buggy_verified

    # ----------------------------------------------------
    # Phase 2: Fixed Environment (base_commit + test_patch + patch)
    # ----------------------------------------------------
    with isolated_instance_environment(repo_dir=repo_dir, instance=instance, version="fixed", apply_test_patch=True) as fixed_wt:
        if conftest_shim:
            (fixed_wt / "conftest.py").write_text(conftest_shim, encoding="utf-8")
        fixed_res = run_official_reference_tests(
            instance, fixed_wt, pass_to_pass_tests=pass_to_pass_tests, timeout=timeout
        )
        report["fixed_details"] = fixed_res

    # Strict fixed verification check:
    fixed_ftps = fixed_res["fail_to_pass"]
    fixed_ptps = fixed_res["pass_to_pass"]

    fixed_unpassed_ftps = [k for k, v in fixed_ftps.items() if not v["is_passed"]]
    fixed_unpassed_ptps = [k for k, v in fixed_ptps.items() if not v["is_passed"]]

    if fixed_unpassed_ftps:
        report["verdict_reasons"].append(
            f"Fixed run FAILED: {len(fixed_unpassed_ftps)} FAIL_TO_PASS tests did not pass on fixed code: {fixed_unpassed_ftps}."
        )
    if fixed_unpassed_ptps:
        report["verdict_reasons"].append(
            f"Fixed run FAILED: {len(fixed_unpassed_ptps)} PASS_TO_PASS tests failed on fixed code: {fixed_unpassed_ptps}."
        )

    fixed_verified = (len(fixed_unpassed_ftps) == 0 and len(fixed_unpassed_ptps) == 0)
    report["fixed_verified"] = fixed_verified

    report["reproduced"] = buggy_verified and fixed_verified
    if report["reproduced"]:
        report["verdict_reasons"].append("Ground-truth defect reproduction confirmed: FAIL_TO_PASS failed via assertion on buggy and passed on fixed; PASS_TO_PASS clean on both.")

    return report


def print_instance_summary(instance: SWEBenchInstance):
    """Print a human-readable summary of an instance."""
    print(f"\n{'='*60}")
    print(f"Instance: {instance.instance_id}")
    print(f"  Repo: {instance.repo} (v{instance.version})")
    print(f"  Commit: {instance.base_commit[:12]}")
    print(f"  FAIL_TO_PASS tests: {len(instance.fail_to_pass)}")
    print(f"  PASS_TO_PASS tests: {len(instance.pass_to_pass)}")
    print(f"  Patched files: {len(instance.patched_files)}")
    for pf in instance.patched_files:
        print(f"    - {pf.filepath} (+{len(pf.added_lines)}/-{len(pf.removed_lines)})")
    print(f"  Target functions: {instance.target_functions}")
    print(f"  Problem: {instance.problem_statement[:200]}...")
    print(f"{'='*60}")
