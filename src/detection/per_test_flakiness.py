"""
Per-test flakiness detection: run each test function individually N times.
This gives much more granular data than whole-file execution.
"""
import subprocess
import json
import sys
import re
import time
from pathlib import Path
from datetime import datetime


def discover_tests(test_file, project_dir):
    """Discover all test function names in a test file."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "--collect-only", "-q"],
        capture_output=True, text=True, timeout=30, cwd=project_dir,
    )
    tests = []
    for line in result.stdout.split("\n"):
        line = line.strip()
        if "::" in line and not line.startswith("="):
            tests.append(line)
    return tests


def run_single_test(test_id, project_dir, seed=None, timeout=30):
    """Run a single test function and return pass/fail."""
    cmd = [sys.executable, "-m", "pytest", test_id, "-x", "--tb=line", "-q"]
    env = None
    if seed is not None:
        import os
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = str(seed)

    start = time.perf_counter()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                          timeout=timeout, cwd=project_dir, env=env)
        elapsed = time.perf_counter() - start
        # Extract error info
        error = None
        if r.returncode != 0:
            for line in (r.stdout + r.stderr).split("\n"):
                if "FAILED" in line or "Error" in line or "assert" in line.lower():
                    error = line.strip()[:150]
                    break
        return {
            "passed": r.returncode == 0,
            "duration": round(elapsed, 4),
            "error": error,
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "duration": timeout, "error": "TIMEOUT"}


def analyze_per_test(test_file, project_dir, num_runs=15):
    """Run each test N times and classify flakiness."""
    print("Discovering tests in {}...".format(test_file))
    tests = discover_tests(test_file, project_dir)
    print("Found {} test functions".format(len(tests)))

    results = {}
    for test_id in tests:
        short_name = test_id.split("::")[-1]
        print("\n  Testing: {} ({} runs)".format(short_name, num_runs), end="", flush=True)

        runs = []
        for i in range(num_runs):
            seed = i * 7919 + 42
            r = run_single_test(test_id, project_dir, seed=seed)
            runs.append(r)
            print("." if r["passed"] else "X", end="", flush=True)

        passes = sum(1 for r in runs if r["passed"])
        fails = num_runs - passes
        is_flaky = 0 < passes < num_runs

        category = "stable_pass" if passes == num_runs else \
                   "stable_fail" if fails == num_runs else \
                   "flaky"
        
        flakiness_rate = min(passes, fails) / num_runs if num_runs > 0 else 0

        results[short_name] = {
            "test_id": test_id,
            "passes": passes,
            "fails": fails,
            "is_flaky": is_flaky,
            "category": category,
            "flakiness_rate": round(flakiness_rate, 3),
            "errors": list(set(r["error"] for r in runs if r["error"])),
            "mean_duration": round(sum(r["duration"] for r in runs) / num_runs, 4),
        }
        print(" -> {}".format(category))

    # Summary
    stable_pass = sum(1 for v in results.values() if v["category"] == "stable_pass")
    stable_fail = sum(1 for v in results.values() if v["category"] == "stable_fail")
    flaky = sum(1 for v in results.values() if v["category"] == "flaky")

    print("\n" + "=" * 60)
    print("PER-TEST FLAKINESS SUMMARY")
    print("=" * 60)
    print("  Total tests: {}".format(len(results)))
    print("  Stable pass: {}".format(stable_pass))
    print("  Stable fail: {}".format(stable_fail))
    print("  Flaky:       {}".format(flaky))
    if flaky > 0:
        print("\n  Flaky tests:")
        for name, data in results.items():
            if data["is_flaky"]:
                print("    {} (pass:{}/fail:{}, rate:{:.1%})".format(
                    name, data["passes"], data["fails"], data["flakiness_rate"]))

    return {
        "test_file": test_file,
        "project_dir": project_dir,
        "num_runs": num_runs,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(results),
            "stable_pass": stable_pass,
            "stable_fail": stable_fail,
            "flaky": flaky,
        },
        "tests": results,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-file", required=True)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--runs", type=int, default=15)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    report = analyze_per_test(args.test_file, args.project_dir, args.runs)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print("\nReport saved: {}".format(args.output))
