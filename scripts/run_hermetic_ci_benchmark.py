"""
Hermetic CI Empirical Benchmark Orchestrator.

Measures the empirical resilience and build breakage rates of test selection strategies
under modern production Hermetic CI conditions (strict air-gapped / socket-blocked environment).

Contrasts:
1. Keep-All (unconditional CI admission)
2. Discard-All-Flaky (dynamic-only flakiness filter)
3. Static-Only (static specificity filter)
4. Random-Filtering (budget-matched random sampling)
5. Risk-Aware-Triage (Ours: 4-tier risk-aware admission gatekeeper)

Outputs:
- results/hermetic_ci_benchmark_results.json
- paper/emse_submission/tables/tab_hermetic_ci_benchmark.tex
"""

import datetime
import json
import os
import shutil
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.execution.structured_executor import _run_pytest_with_plugin
from src.utils.swebench_loader import load_swebench_instances, isolated_instance_environment

RUN_ID = "run_phase4_rerun_20260926_090500"
POOLS_ROOT = PROJECT_ROOT / "results" / "runs" / RUN_ID / "strategy_pools"
RESULTS_FILE = PROJECT_ROOT / "results" / "hermetic_ci_benchmark_results.json"
LATEX_TABLE = PROJECT_ROOT / "paper" / "emse_submission" / "tables" / "tab_hermetic_ci_benchmark.tex"

# All 13 valid instances from formal rerun
VALID_INSTANCES = [
    {"instance_id": "psf__requests-1724", "repo": "psf/requests", "repo_dir": "psf__requests", "domain": "HTTP / Networking"},
    {"instance_id": "psf__requests-1766", "repo": "psf/requests", "repo_dir": "psf__requests", "domain": "HTTP / Networking"},
    {"instance_id": "psf__requests-1921", "repo": "psf/requests", "repo_dir": "psf__requests", "domain": "HTTP / Networking"},
    {"instance_id": "psf__requests-2317", "repo": "psf/requests", "repo_dir": "psf__requests", "domain": "HTTP / Networking"},
    {"instance_id": "psf__requests-6028", "repo": "psf/requests", "repo_dir": "psf__requests", "domain": "HTTP / Networking"},
    {"instance_id": "pallets__flask-5014", "repo": "pallets/flask", "repo_dir": "pallets__flask", "domain": "Web Framework"},
    {"instance_id": "sympy__sympy-15809", "repo": "sympy/sympy", "repo_dir": "sympy__sympy", "domain": "Symbolic Mathematics"},
    {"instance_id": "sympy__sympy-17630", "repo": "sympy/sympy", "repo_dir": "sympy__sympy", "domain": "Symbolic Mathematics"},
    {"instance_id": "sympy__sympy-21930", "repo": "sympy/sympy", "repo_dir": "sympy__sympy", "domain": "Symbolic Mathematics"},
    {"instance_id": "pydata__xarray-4075", "repo": "pydata/xarray", "repo_dir": "pydata__xarray", "domain": "Scientific Computing"},
    {"instance_id": "pydata__xarray-4356", "repo": "pydata/xarray", "repo_dir": "pydata__xarray", "domain": "Scientific Computing"},
    {"instance_id": "pydata__xarray-4966", "repo": "pydata/xarray", "repo_dir": "pydata__xarray", "domain": "Scientific Computing"},
    {"instance_id": "pydata__xarray-6744", "repo": "pydata/xarray", "repo_dir": "pydata__xarray", "domain": "Scientific Computing"},
]

CONFTEST_REQUESTS = """# Backward compatibility shim for Python 3.11+
import collections, collections.abc
for name in ['Mapping', 'MutableMapping', 'Sequence', 'Callable', 'Iterable', 'Iterator']:
    if not hasattr(collections, name) and hasattr(collections.abc, name):
        setattr(collections, name, getattr(collections.abc, name))
"""

CONFTEST_XARRAY = """# Backward compatibility shim for Python 3.11+ and NumPy 2.0+
import numpy as np
if not hasattr(np, 'unicode_'):
    np.unicode_ = np.str_
import collections, collections.abc
for name in ['Mapping', 'MutableMapping', 'Sequence', 'Callable', 'Iterable', 'Iterator']:
    if not hasattr(collections, name) and hasattr(collections.abc, name):
        setattr(collections, name, getattr(collections.abc, name))
"""


def is_network_violation(test_result: dict) -> bool:
    """Detect whether a failure was caused by socket connection block in Hermetic CI."""
    err_type = str(test_result.get("error_type", ""))
    err_msg = str(test_result.get("error_message", ""))
    indicators = [
        "Hermetic CI Violation",
        "ConnectionError",
        "NewConnectionError",
        "Max retries exceeded with url",
        "Connection refused",
        "connection blocked",
    ]
    if "OSError" in err_type and ("Hermetic CI" in err_msg or "connectionpool" in err_msg or "urlopen" in err_msg):
        return True
    return any(ind in err_msg or ind in err_type for ind in indicators)


def run_benchmark():
    print("=" * 80)
    print("HERMETIC CI EMPIRICAL BENCHMARK (AIR-GAPPED SOCKET ISOLATION)")
    print(f"Timestamp: {datetime.datetime.utcnow().isoformat()}Z")
    print(f"Target Instances: {len(VALID_INSTANCES)}")
    print("=" * 80)

    all_swebench = load_swebench_instances()
    inst_map = {inst.instance_id: inst for inst in all_swebench}

    strategies = ["Keep-All", "Discard-All-Flaky", "Static-Only", "Random-Filtering", "Risk-Aware-Triage"]
    benchmark_results = {
        "timestamp_utc": datetime.datetime.utcnow().isoformat(),
        "total_instances": len(VALID_INSTANCES),
        "instances": {},
        "summary": {},
    }

    strategy_totals = {
        s: {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "network_violations": 0,
            "broken_builds": 0,
            "clean_builds": 0,
        }
        for s in strategies
    }

    t0_all = time.time()

    for idx, inst_info in enumerate(VALID_INSTANCES, 1):
        iid = inst_info["instance_id"]
        repo_name = inst_info["repo"]
        domain = inst_info["domain"]
        repo_dir = PROJECT_ROOT / "data" / "repos" / inst_info["repo_dir"]
        test_dir = PROJECT_ROOT / "data" / "study_gate3" / iid / "generated_tests"
        pools_dir = POOLS_ROOT / iid

        print(f"\n[{idx}/{len(VALID_INSTANCES)}] Benchmarking {iid} ({domain})...")

        swe_inst = inst_map.get(iid)
        if not swe_inst:
            print(f"  [-] Instance {iid} not found in SWE-bench map!")
            continue

        instance_entry = {
            "instance_id": iid,
            "domain": domain,
            "repo": repo_name,
            "strategies": {},
        }

        # Setup conftest
        conftest_content = None
        python_paths_rel = ["."]
        if "requests" in repo_name:
            conftest_content = CONFTEST_REQUESTS
        elif "flask" in repo_name:
            python_paths_rel = ["src"]
        elif "xarray" in repo_name:
            conftest_content = CONFTEST_XARRAY

        with isolated_instance_environment(repo_dir, swe_inst, version="fixed") as wt:
            if conftest_content:
                (wt / "conftest.py").write_text(conftest_content, encoding="utf-8")
            for tf in test_dir.glob("test_gen_*.py"):
                shutil.copy(tf, wt / tf.name)

            python_paths = [str(wt / p) for p in python_paths_rel]

            for strat in strategies:
                pool_file = pools_dir / f"{strat}_main_fixed.json"
                if not pool_file.exists():
                    print(f"  [-] Missing pool file: {pool_file.name}")
                    continue

                with open(pool_file, "r", encoding="utf-8") as pf:
                    pool_data = json.load(pf)

                nodeids = pool_data.get("runtime_order", [])
                if not nodeids:
                    # Strategy admitted 0 tests
                    instance_entry["strategies"][strat] = {
                        "total_tests": 0,
                        "passed_tests": 0,
                        "failed_tests": 0,
                        "network_violations": 0,
                        "exit_code": 0,
                        "build_status": "CLEAN_EMPTY",
                        "duration_seconds": 0.0,
                    }
                    strategy_totals[strat]["clean_builds"] += 1
                    continue

                rep_file = wt / f"rep_hermetic_{strat}.json"
                t0_exec = time.time()
                exit_code, rep_data, out, err = _run_pytest_with_plugin(
                    nodeids,
                    cwd=wt,
                    report_file=rep_file,
                    python_paths=python_paths,
                    timeout=30,
                    extra_env={"HERMETIC_CI": "1"},
                )
                dur_exec = time.time() - t0_exec

                tests_dict = rep_data.get("tests", {})
                passed = sum(1 for t in tests_dict.values() if t.get("outcome") == "PASSED")
                failed = sum(1 for t in tests_dict.values() if t.get("outcome") != "PASSED")
                net_viol = sum(1 for t in tests_dict.values() if is_network_violation(t))

                is_broken = (net_viol > 0)
                build_status = "BROKEN_BY_NETWORK" if is_broken else ("PASSED" if failed == 0 else "TEST_FAILED_HERMETIC")

                instance_entry["strategies"][strat] = {
                    "total_tests": len(tests_dict),
                    "passed_tests": passed,
                    "failed_tests": failed,
                    "network_violations": net_viol,
                    "exit_code": exit_code,
                    "build_status": build_status,
                    "duration_seconds": round(dur_exec, 3),
                }

                strategy_totals[strat]["total_tests"] += len(tests_dict)
                strategy_totals[strat]["passed_tests"] += passed
                strategy_totals[strat]["failed_tests"] += failed
                strategy_totals[strat]["network_violations"] += net_viol
                if is_broken:
                    strategy_totals[strat]["broken_builds"] += 1
                else:
                    strategy_totals[strat]["clean_builds"] += 1

                print(f"    [{strat:18s}] Tests: {len(tests_dict):2d} | Passed: {passed:2d} | NetViolations: {net_viol:2d} | Status: {build_status}")

        benchmark_results["instances"][iid] = instance_entry

    total_time = time.time() - t0_all
    print("\n" + "=" * 80)
    print("HERMETIC CI BENCHMARK SUMMARY")
    print(f"Total Benchmark Duration: {total_time:.2f}s")
    print("=" * 80)

    summary = {}
    for strat, data in strategy_totals.items():
        total_inst = len(VALID_INSTANCES)
        break_rate = (data["broken_builds"] / total_inst) * 100.0
        feas_rate = ((total_inst - data["broken_builds"]) / total_inst) * 100.0
        summary[strat] = {
            "total_tests_evaluated": data["total_tests"],
            "passed_tests": data["passed_tests"],
            "network_violations": data["network_violations"],
            "broken_instances": data["broken_builds"],
            "clean_instances": data["clean_builds"],
            "spurious_network_break_rate_pct": round(break_rate, 2),
            "hermetic_build_feasibility_rate_pct": round(feas_rate, 2),
        }
        print(f"Strategy: {strat:18s} | Net Violations: {data['network_violations']:2d} | Broken Suites: {data['broken_builds']:2d}/{total_inst} ({break_rate:5.1f}%) | Hermetic Feasibility: {feas_rate:5.1f}%")

    benchmark_results["summary"] = summary
    benchmark_results["duration_seconds"] = round(total_time, 2)

    # Save JSON results
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(benchmark_results, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Saved JSON results to: {RESULTS_FILE}")

    # Generate LaTeX Table
    generate_latex_benchmark_table(benchmark_results, LATEX_TABLE)
    print(f"[+] Saved LaTeX table to: {LATEX_TABLE}")


def generate_latex_benchmark_table(data: dict, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary = data["summary"]

    lines = [
        r"\begin{table*}[htbp]",
        r"\centering",
        r"\small",
        r"\caption{Empirical Resilience of Test Selection Strategies Under Hermetic CI (Air-Gapped Network Socket Isolation). Evaluated across 13 SWE-bench Verified instances. Spurious Network Breakage measures build failures directly triggered by unmocked socket calls. Mainline Hermetic Feasibility measures the proportion of test suites that execute without environmental network failure.}",
        r"\label{tab:hermetic_ci}",
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"\textbf{Strategy} & \textbf{Admitted Tests} & \textbf{Network Violations} & \textbf{Broken Suites} & \textbf{Spurious Break Rate (\%)} & \textbf{Hermetic Feasibility (\%)} \\",
        r"\midrule",
    ]

    for strat, m in summary.items():
        name = strat
        if strat == "Risk-Aware-Triage":
            name = r"\textbf{Risk-Aware-Triage (Ours)}"
        lines.append(
            f"{name} & {m['total_tests_evaluated']} & {m['network_violations']} & "
            f"{m['broken_instances']}/13 & {m['spurious_network_break_rate_pct']:.1f}\\% & "
            f"\\textbf{{{m['hermetic_build_feasibility_rate_pct']:.1f}\\%}} \\\\"
        )

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table*}",
        "",
    ])

    out_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run_benchmark()
