"""
SWE-bench Dataset Explorer.

Downloads and analyzes SWE-bench Verified metadata to select
suitable bug instances for our feasibility pilot study.

Usage:
    pip install datasets
    python explore_swebench.py
"""

import json
import sys
from collections import Counter
from pathlib import Path


def load_dataset():
    """Load SWE-bench Verified from HuggingFace."""
    try:
        from datasets import load_dataset
        print("Loading SWE-bench Verified from HuggingFace...")
        ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
        print(f"Loaded {len(ds)} task instances")
        return ds
    except ImportError:
        print("ERROR: 'datasets' package not installed.")
        print("Run: pip install datasets")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR loading dataset: {e}")
        sys.exit(1)


def analyze_dataset(ds):
    """Analyze dataset composition and select pilot candidates."""
    
    # Count instances per repo
    repo_counts = Counter()
    repo_instances = {}
    
    for item in ds:
        repo = item["repo"]
        repo_counts[repo] += 1
        if repo not in repo_instances:
            repo_instances[repo] = []
        
        # Extract useful metadata
        patch_lines = len(item.get("patch", "").split("\n"))
        fail_to_pass = json.loads(item.get("FAIL_TO_PASS", "[]")) if isinstance(item.get("FAIL_TO_PASS"), str) else item.get("FAIL_TO_PASS", [])
        pass_to_pass = json.loads(item.get("PASS_TO_PASS", "[]")) if isinstance(item.get("PASS_TO_PASS"), str) else item.get("PASS_TO_PASS", [])
        
        instance_info = {
            "instance_id": item["instance_id"],
            "base_commit": item.get("base_commit", ""),
            "patch_lines": patch_lines,
            "fail_to_pass_count": len(fail_to_pass),
            "pass_to_pass_count": len(pass_to_pass),
            "problem_statement_length": len(item.get("problem_statement", "")),
        }
        repo_instances[repo].append(instance_info)
    
    return repo_counts, repo_instances


def select_pilot_instances(repo_instances, target_repos=None, max_per_repo=5):
    """Select suitable instances for pilot study."""
    
    if target_repos is None:
        target_repos = [
            "psf/requests",
            "pallets/flask",
            "pytest-dev/pytest",
            "sympy/sympy",
            "pydata/xarray",
        ]
    
    selected = {}
    for repo in target_repos:
        if repo not in repo_instances:
            print(f"WARNING: {repo} not found in dataset")
            continue
        
        instances = repo_instances[repo]
        
        # Prefer instances with:
        # - Small to medium patches (easier to understand)
        # - Multiple fail-to-pass tests (richer evaluation)
        # - Reasonable problem statement (not too short)
        scored = []
        for inst in instances:
            score = 0
            # Prefer moderate patch size
            if 5 <= inst["patch_lines"] <= 50:
                score += 3
            elif inst["patch_lines"] < 5:
                score += 1
            
            # Prefer instances with fail-to-pass tests
            score += min(inst["fail_to_pass_count"], 5)
            
            # Prefer clear problem statements
            if inst["problem_statement_length"] > 100:
                score += 2
            
            scored.append((score, inst))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        selected[repo] = [s[1] for s in scored[:max_per_repo]]
    
    return selected


def print_report(repo_counts, selected):
    """Print analysis report."""
    
    print("\n" + "=" * 70)
    print("SWE-bench Verified Dataset Analysis")
    print("=" * 70)
    
    print("\nInstances per Repository:")
    print("-" * 50)
    for repo, count in repo_counts.most_common():
        marker = " <-- PILOT" if any(repo in r for r in selected.keys()) else ""
        print(f"  {repo:40s} {count:4d}{marker}")
    print(f"  {'TOTAL':40s} {sum(repo_counts.values()):4d}")
    
    print("\n" + "=" * 70)
    print("Selected Pilot Instances")
    print("=" * 70)
    
    total_selected = 0
    for repo, instances in selected.items():
        print(f"\n  {repo} ({len(instances)} instances):")
        for inst in instances:
            print(f"    - {inst['instance_id']}")
            print(f"      patch: {inst['patch_lines']} lines, "
                  f"fail_to_pass: {inst['fail_to_pass_count']}, "
                  f"pass_to_pass: {inst['pass_to_pass_count']}")
            total_selected += 1
    
    print(f"\n  Total selected: {total_selected} instances across {len(selected)} repos")
    return total_selected


def save_pilot_selection(selected, output_path):
    """Save selected instances to JSON for downstream use."""
    output = {
        "description": "Pilot study instance selection from SWE-bench Verified",
        "selection_criteria": {
            "patch_size": "prefer 5-50 lines",
            "fail_to_pass": "prefer multiple test cases",
            "problem_statement": "prefer clear descriptions >100 chars",
        },
        "repos": {}
    }
    
    for repo, instances in selected.items():
        output["repos"][repo] = {
            "count": len(instances),
            "instances": instances,
        }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nSaved selection to: {output_path}")


def main():
    output_dir = Path(__file__).parent.parent / "data" / "benchmarks"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ds = load_dataset()
    repo_counts, repo_instances = analyze_dataset(ds)
    selected = select_pilot_instances(repo_instances)
    total = print_report(repo_counts, selected)
    
    if total > 0:
        save_pilot_selection(selected, output_dir / "pilot_selection.json")
    
    print("\nNext steps:")
    print("  1. Review selected instances")
    print("  2. Pull Docker images for selected repos")
    print("  3. Test LLM generation on 2-3 instances")
    print("  4. Run repeated execution for flakiness detection")


if __name__ == "__main__":
    main()
