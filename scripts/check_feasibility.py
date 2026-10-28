"""
Feasibility Check Script: Evaluate BugsInPy project reproducibility.

This script checks which BugsInPy projects can be set up and run
in the current environment. It does NOT run full experiments —
only validates that projects are usable for our study.

Usage:
    python check_bugsinpy_feasibility.py --bugsinpy-dir <path>
"""

import subprocess
import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime


def check_project_info(bugsinpy_dir: Path) -> list[dict]:
    """Scan BugsInPy directory for project metadata."""
    projects = []
    projects_dir = bugsinpy_dir / "projects"
    
    if not projects_dir.exists():
        print(f"ERROR: {projects_dir} not found")
        return projects
    
    for proj_dir in sorted(projects_dir.iterdir()):
        if not proj_dir.is_dir():
            continue
        
        proj_info = {
            "name": proj_dir.name,
            "path": str(proj_dir),
            "bug_count": 0,
            "bugs": [],
            "python_versions": set(),
            "test_frameworks": set(),
        }
        
        bugs_dir = proj_dir / "bugs"
        if bugs_dir.exists():
            for bug_dir in sorted(bugs_dir.iterdir()):
                if not bug_dir.is_dir():
                    continue
                
                bug_info_file = bug_dir / "bug.info"
                if bug_info_file.exists():
                    bug_data = parse_bug_info(bug_info_file)
                    bug_data["bug_id"] = bug_dir.name
                    proj_info["bugs"].append(bug_data)
                    
                    if "python_version" in bug_data:
                        proj_info["python_versions"].add(bug_data["python_version"])
                    if "test_framework" in bug_data:
                        proj_info["test_frameworks"].add(bug_data["test_framework"])
            
            proj_info["bug_count"] = len(proj_info["bugs"])
        
        # Convert sets to lists for JSON serialization
        proj_info["python_versions"] = sorted(proj_info["python_versions"])
        proj_info["test_frameworks"] = sorted(proj_info["test_frameworks"])
        
        projects.append(proj_info)
    
    return projects


def parse_bug_info(filepath: Path) -> dict:
    """Parse a BugsInPy bug.info file."""
    info = {}
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip().strip('"')
                    value = value.strip().strip('"')
                    info[key] = value
    except Exception as e:
        info["parse_error"] = str(e)
    return info


def check_docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def generate_report(projects: list[dict], docker_ok: bool) -> dict:
    """Generate a feasibility summary report."""
    
    # Known reproducibility status from literature
    KNOWN_STABLE = {"cookiecutter", "httpie", "thefuck", "sanic", "fastapi"}
    KNOWN_DEGRADED = {"pandas", "matplotlib", "scikit-learn", "spacy", "keras"}
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "docker_available": docker_ok,
        "total_projects": len(projects),
        "total_bugs": sum(p["bug_count"] for p in projects),
        "projects_summary": [],
        "recommended_for_pilot": [],
        "warnings": [],
    }
    
    for proj in projects:
        status = "unknown"
        if proj["name"] in KNOWN_STABLE:
            status = "likely_reproducible"
        elif proj["name"] in KNOWN_DEGRADED:
            status = "likely_degraded"
        
        summary = {
            "name": proj["name"],
            "bug_count": proj["bug_count"],
            "python_versions": proj["python_versions"],
            "test_frameworks": proj["test_frameworks"],
            "reproducibility_status": status,
        }
        report["projects_summary"].append(summary)
        
        # Recommend projects for pilot study
        if status == "likely_reproducible" and proj["bug_count"] >= 5:
            report["recommended_for_pilot"].append(proj["name"])
    
    if not docker_ok:
        report["warnings"].append(
            "Docker is not running. BugsInPy reproducibility requires Docker containers."
        )
    
    if not report["recommended_for_pilot"]:
        report["warnings"].append(
            "No projects meet pilot criteria. Consider using SWE-bench instead."
        )
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Check BugsInPy feasibility for LLM test stability study"
    )
    parser.add_argument(
        "--bugsinpy-dir", type=str, default=None,
        help="Path to cloned BugsInPy repository"
    )
    parser.add_argument(
        "--output", type=str, default="feasibility_report.json",
        help="Output report file path"
    )
    parser.add_argument(
        "--check-only", action="store_true",
        help="Only check environment, don't scan BugsInPy"
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("LLM Test Stability Study - Feasibility Check")
    print("=" * 60)
    
    # Check Docker
    docker_ok = check_docker_available()
    print(f"\n[Docker] Available: {docker_ok}")
    
    # Check Python
    print(f"[Python] Version: {sys.version}")
    
    # Check key tools
    tools = {
        "pytest": "pytest --version",
        "coverage": "coverage --version",
        "mutmut": "mutmut --version",
        "git": "git --version",
    }
    for name, cmd in tools.items():
        try:
            result = subprocess.run(
                cmd.split(), capture_output=True, text=True, timeout=5
            )
            status = "OK" if result.returncode == 0 else "MISSING"
            version = result.stdout.strip().split("\n")[0] if result.returncode == 0 else "not found"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            status = "MISSING"
            version = "not installed"
        print(f"[{name}] {status} {version}")
    
    if args.check_only:
        print("\n--check-only mode: skipping BugsInPy scan")
        return
    
    # Scan BugsInPy if available
    projects = []
    if args.bugsinpy_dir:
        bugsinpy_path = Path(args.bugsinpy_dir)
        if bugsinpy_path.exists():
            print(f"\n[BugsInPy] Scanning: {bugsinpy_path}")
            projects = check_project_info(bugsinpy_path)
            print(f"[BugsInPy] Found {len(projects)} projects, "
                  f"{sum(p['bug_count'] for p in projects)} total bugs")
        else:
            print(f"\n[BugsInPy] Directory not found: {bugsinpy_path}")
    else:
        print("\n[BugsInPy] No directory specified. Use --bugsinpy-dir to scan.")
        print("  To clone: git clone https://github.com/soarsmu/BugsInPy.git")
    
    # Generate report
    report = generate_report(projects, docker_ok)
    
    # Save report
    output_path = Path(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n[Report] Saved to: {output_path}")
    
    # Print recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    if report["recommended_for_pilot"]:
        print(f"Recommended pilot projects: {', '.join(report['recommended_for_pilot'])}")
    for w in report["warnings"]:
        print(f"WARNING: {w}")
    
    print("\nBased on literature, recommended pilot projects:")
    print("  1. cookiecutter - template engine, simple deps")
    print("  2. httpie - CLI HTTP client, moderate complexity")  
    print("  3. thefuck - command correction, simple deps")
    print("  4. fastapi - web framework, modern Python")
    print("  5. sanic - async web framework")
    print("\nAlternative: Use SWE-bench Verified (Docker containers available)")


if __name__ == "__main__":
    main()
