"""
Rigorous Shared Repositories State Auditor.

Audits git repositories in data/repos to ensure they remain untouched read-only mirrors.
Strictly checks subprocess return codes — a failed git command NEVER evaluates as clean!
"""

import datetime
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

REPOS_DIR = Path(r"F:\论文\llm-test-stability\data\repos")
REPOS = ["psf__requests", "pallets__flask", "pytest-dev__pytest", "sympy__sympy", "pydata__xarray"]


def audit_single_repo(repo_path: Path) -> Dict[str, Any]:
    """Audit a single git repository with strict returncode verification."""
    if not repo_path.exists():
        return {"exists": False, "is_clean": False, "error": "Directory does not exist"}

    res = {
        "exists": True,
        "path": str(repo_path),
        "is_clean": False,
        "git_success": False,
        "head_sha": None,
        "branch_name": None,
        "status_porcelain": None,
        "diff_stat": None,
        "diff_cached_stat": None,
        "untracked_files": [],
        "errors": [],
    }

    # 1. HEAD commit and Tree hash
    p_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_path), capture_output=True, text=True)
    if p_head.returncode != 0:
        res["errors"].append(f"git rev-parse HEAD failed ({p_head.returncode}): {p_head.stderr.strip()}")
        return res
    res["head_sha"] = p_head.stdout.strip()

    p_tree = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=str(repo_path), capture_output=True, text=True)
    res["tree_sha"] = p_tree.stdout.strip() if p_tree.returncode == 0 else "UNKNOWN"

    # 2. Branch name and detached status
    p_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(repo_path), capture_output=True, text=True)
    if p_branch.returncode == 0:
        bname = p_branch.stdout.strip()
        res["branch_name"] = bname
        res["is_detached"] = (bname == "HEAD")
    else:
        res["errors"].append(f"git rev-parse --abbrev-ref HEAD failed: {p_branch.stderr.strip()}")

    # 3. Status porcelain v1 with untracked-files=all
    p_status = subprocess.run(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=str(repo_path), capture_output=True, text=True)
    if p_status.returncode != 0:
        res["errors"].append(f"git status --porcelain=v1 failed ({p_status.returncode}): {p_status.stderr.strip()}")
        return res
    res["status_porcelain"] = p_status.stdout.strip()

    # 4. Working tree diff
    p_diff = subprocess.run(["git", "diff", "--stat"], cwd=str(repo_path), capture_output=True, text=True)
    if p_diff.returncode != 0:
        res["errors"].append(f"git diff failed: {p_diff.stderr.strip()}")
    res["diff_stat"] = p_diff.stdout.strip()

    # 5. Cached diff
    p_diff_c = subprocess.run(["git", "diff", "--cached", "--stat"], cwd=str(repo_path), capture_output=True, text=True)
    if p_diff_c.returncode != 0:
        res["errors"].append(f"git diff --cached failed: {p_diff_c.stderr.strip()}")
    res["diff_cached_stat"] = p_diff_c.stdout.strip()

    # 6. Untracked files
    p_untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=str(repo_path), capture_output=True, text=True)
    if p_untracked.returncode == 0:
        res["untracked_files"] = [f for f in p_untracked.stdout.strip().splitlines() if f]
    else:
        res["errors"].append(f"git ls-files --others failed: {p_untracked.stderr.strip()}")

    # 7. Tracked files count
    p_tracked = subprocess.run(["git", "ls-files"], cwd=str(repo_path), capture_output=True, text=True)
    res["tracked_files_count"] = len(p_tracked.stdout.strip().splitlines()) if p_tracked.returncode == 0 else 0

    # 8. Ignored files check
    p_ignored = subprocess.run(["git", "status", "--porcelain=v1", "--ignored"], cwd=str(repo_path), capture_output=True, text=True)
    ignored_lines = [line[3:] for line in p_ignored.stdout.splitlines() if line.startswith("!! ")] if p_ignored.returncode == 0 else []
    res["ignored_files_count"] = len(ignored_lines)
    res["ignored_files_sample"] = ignored_lines[:10]

    # Determine cleanliness: command must succeed AND porcelain status must be empty AND untracked empty
    res["git_success"] = len(res["errors"]) == 0
    res["is_clean"] = (
        res["git_success"] and
        len(res["status_porcelain"]) == 0 and
        len(res["untracked_files"]) == 0 and
        len(res["diff_stat"]) == 0 and
        len(res["diff_cached_stat"]) == 0
    )

    return res


def run_audit(output_path: Path = Path(r"F:\论文\llm-test-stability\data\repos_state_audit.json")) -> Dict[str, Any]:
    audit_data = {
        "audit_timestamp": datetime.datetime.now().isoformat(),
        "all_repos_clean": True,
        "repos": {}
    }

    for r in REPOS:
        p = REPOS_DIR / r
        repo_res = audit_single_repo(p)
        audit_data["repos"][r] = repo_res
        if not repo_res.get("is_clean", False):
            audit_data["all_repos_clean"] = False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(audit_data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Audit completed (All Clean: {audit_data['all_repos_clean']}): {output_path}")
    for r, info in audit_data["repos"].items():
        head = (info.get("head_sha") or "")[:10]
        clean = info.get("is_clean")
        branch = info.get("branch_name")
        errs = info.get("errors", [])
        print(f"  {r:22s} HEAD: {head} | Clean: {clean} | Branch: {branch}")
        if errs:
            print(f"    ERRORS: {errs}")

    return audit_data


audit_all_repos = run_audit


if __name__ == "__main__":
    run_audit()
