"""
Cross-Model Empirical Study Orchestrator: Qwen3-8B vs. Qwen2.5-7B.

Evaluates how LLM architectural evolution and model scaling influence:
1. Test generation build/collection feasibility.
2. Static assertion specificity (S_defect) and environmental fragility (P_frag).
3. Risk-Aware-Triage tier allocation across distinct software engineering domains.

Generates:
- results/cross_model_study_results.json
- paper/emse_submission/tables/tab_cross_model_comparison.tex
- paper/emse_submission/figures/fig_cross_model_comparison.pdf
"""

import ast
import datetime
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.generation.generate_tests import generate_tests
from src.triage.risk_triage import triage_suite, extract_static_features_from_file
from src.execution.structured_executor import discover_test_nodeids
from src.utils.swebench_loader import load_swebench_instances, isolated_instance_environment

BASE_RUN_ID = "run_phase4_rerun_20260926_090500"
BASE_RESULTS_FILE = PROJECT_ROOT / "results" / "runs" / BASE_RUN_ID / "phase4_full_study_results.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "cross_model_qwen25"
RESULTS_JSON = PROJECT_ROOT / "results" / "cross_model_study_results.json"
LATEX_TABLE = PROJECT_ROOT / "paper" / "emse_submission" / "tables" / "tab_cross_model_comparison.tex"
FIG_PDF = PROJECT_ROOT / "paper" / "emse_submission" / "figures" / "fig_cross_model_comparison.pdf"
FIG_PNG = PROJECT_ROOT / "paper" / "emse_submission" / "figures" / "fig_cross_model_comparison.png"

MODEL_NAME = "qwen2.5:7b"
NUM_RUNS_PER_INSTANCE = 3
TEMPERATURE = 0.7

VALID_INSTANCES = [
    {
        "instance_id": "psf__requests-1724",
        "repo": "psf/requests",
        "repo_dir": "psf__requests",
        "target_file_rel": "requests/sessions.py",
        "domain": "HTTP / Networking",
    },
    {
        "instance_id": "psf__requests-1766",
        "repo": "psf/requests",
        "repo_dir": "psf__requests",
        "target_file_rel": "requests/auth.py",
        "domain": "HTTP / Networking",
    },
    {
        "instance_id": "psf__requests-1921",
        "repo": "psf/requests",
        "repo_dir": "psf__requests",
        "target_file_rel": "requests/sessions.py",
        "domain": "HTTP / Networking",
    },
    {
        "instance_id": "psf__requests-2317",
        "repo": "psf/requests",
        "repo_dir": "psf__requests",
        "target_file_rel": "requests/sessions.py",
        "domain": "HTTP / Networking",
    },
    {
        "instance_id": "psf__requests-6028",
        "repo": "psf/requests",
        "repo_dir": "psf__requests",
        "target_file_rel": "requests/utils.py",
        "domain": "HTTP / Networking",
    },
    {
        "instance_id": "pallets__flask-5014",
        "repo": "pallets/flask",
        "repo_dir": "pallets__flask",
        "target_file_rel": "src/flask/blueprints.py",
        "domain": "Web Framework",
    },
    {
        "instance_id": "sympy__sympy-15809",
        "repo": "sympy/sympy",
        "repo_dir": "sympy__sympy",
        "target_file_rel": "sympy/functions/elementary/miscellaneous.py",
        "domain": "Symbolic Mathematics",
    },
    {
        "instance_id": "sympy__sympy-17630",
        "repo": "sympy/sympy",
        "repo_dir": "sympy__sympy",
        "target_file_rel": "sympy/matrices/expressions/matexpr.py",
        "domain": "Symbolic Mathematics",
    },
    {
        "instance_id": "sympy__sympy-21930",
        "repo": "sympy/sympy",
        "repo_dir": "sympy__sympy",
        "target_file_rel": "sympy/physics/secondquant.py",
        "domain": "Symbolic Mathematics",
    },
    {
        "instance_id": "pydata__xarray-4075",
        "repo": "pydata/xarray",
        "repo_dir": "pydata__xarray",
        "target_file_rel": "xarray/core/weighted.py",
        "domain": "Scientific Computing",
    },
    {
        "instance_id": "pydata__xarray-4356",
        "repo": "pydata/xarray",
        "repo_dir": "pydata__xarray",
        "target_file_rel": "xarray/core/nanops.py",
        "domain": "Scientific Computing",
    },
    {
        "instance_id": "pydata__xarray-4966",
        "repo": "pydata/xarray",
        "repo_dir": "pydata__xarray",
        "target_file_rel": "xarray/coding/variables.py",
        "domain": "Scientific Computing",
    },
    {
        "instance_id": "pydata__xarray-6744",
        "repo": "pydata/xarray",
        "repo_dir": "pydata__xarray",
        "target_file_rel": "xarray/core/rolling.py",
        "domain": "Scientific Computing",
    },
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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main():
    print("=" * 80)
    print("CROSS-MODEL EMPIRICAL STUDY: Qwen3-8B vs. Qwen2.5-7B")
    print(f"Model Under Test: {MODEL_NAME}")
    print(f"Timestamp: {datetime.datetime.utcnow().isoformat()}Z")
    print("=" * 80)

    # 1. Load Qwen3-8B Baseline Results
    with open(BASE_RESULTS_FILE, "r", encoding="utf-8") as f:
        base_data = json.load(f)
    base_inst_map = {inst["instance_id"]: inst for inst in base_data["instance_results"]}

    all_swebench = load_swebench_instances()
    swe_map = {inst.instance_id: inst for inst in all_swebench}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    study_results = {
        "timestamp_utc": datetime.datetime.utcnow().isoformat(),
        "model_baseline": "qwen3:8b",
        "model_comparison": MODEL_NAME,
        "instances": {},
        "summary": {},
    }

    total_qwen25_tests = 0
    total_qwen25_collected = 0
    total_qwen25_unmocked_urls = 0
    qwen25_tiers_total = {"tier_1": 0, "tier_2": 0, "tier_3": 0, "tier_4": 0}
    qwen25_sdefect_list = []

    t0_start = time.time()

    for idx, cfg in enumerate(VALID_INSTANCES, 1):
        iid = cfg["instance_id"]
        repo_dir = PROJECT_ROOT / "data" / "repos" / cfg["repo_dir"]
        target_rel = cfg["target_file_rel"]
        domain = cfg["domain"]
        inst = swe_map[iid]

        print(f"\n[{idx}/{len(VALID_INSTANCES)}] Generating & Profiling {iid} ({domain})...")
        inst_out_dir = OUTPUT_DIR / iid / "generated_tests"
        inst_out_dir.mkdir(parents=True, exist_ok=True)

        # Step A: Extract Source Code (base_commit, zero leakage)
        with isolated_instance_environment(repo_dir, inst, version="buggy") as wt:
            source_file = wt / target_rel
            source_code = source_file.read_text(encoding="utf-8", errors="ignore")
            source_lines = len(source_code.splitlines())
            if source_lines > 1000:
                source_code = "\n".join(source_code.splitlines()[:800])

        # Step B: Generate Tests via Ollama
        gen_files = []
        for run_idx in range(NUM_RUNS_PER_INSTANCE):
            out_file = inst_out_dir / f"test_gen_{run_idx:02d}.py"
            if not out_file.exists():
                print(f"  -> Generating run {run_idx} via {MODEL_NAME}...")
                res = generate_tests(
                    source_code=source_code,
                    filepath=target_rel,
                    model=MODEL_NAME,
                    template="basic",
                    temperature=TEMPERATURE,
                )
                out_file.write_text(res["test_code"], encoding="utf-8")
            gen_files.append(out_file)

        # Setup conftest
        conftest_content = None
        python_paths_rel = ["."]
        if "requests" in iid:
            conftest_content = CONFTEST_REQUESTS
            (inst_out_dir / "conftest.py").write_text(CONFTEST_REQUESTS, encoding="utf-8")
        elif "flask" in iid:
            python_paths_rel = ["src"]
        elif "xarray" in iid:
            conftest_content = CONFTEST_XARRAY
            (inst_out_dir / "conftest.py").write_text(CONFTEST_XARRAY, encoding="utf-8")

        # Step C: Dynamic Discovery & Collection
        collected_nids = []
        with isolated_instance_environment(repo_dir, inst, version="fixed") as fixed_wt:
            if conftest_content:
                (fixed_wt / "conftest.py").write_text(conftest_content, encoding="utf-8")
            for gf in gen_files:
                shutil.copy(gf, fixed_wt / gf.name)
            python_paths = [str(fixed_wt / p) for p in python_paths_rel]

            for gf in gen_files:
                local_gf = fixed_wt / gf.name
                nids, errs = discover_test_nodeids(local_gf, cwd=fixed_wt, python_paths=python_paths, timeout=20)
                collected_nids.extend(nids)

        # Step D: Static AST Triage Profiling
        inst_decisions = []
        inst_urls = 0
        for gf in gen_files:
            trep = triage_suite(test_file=gf)
            static_map = extract_static_features_from_file(gf)
            for dec in trep.decisions:
                inst_decisions.append(dec)
                qwen25_sdefect_list.append(dec.defect_potential_score)
                feats = static_map.get(dec.test_name)
                if feats and any(c.startswith("external_url:") for c in feats.fragile_calls):
                    inst_urls += 1

        t1 = sum(1 for d in inst_decisions if d.category == "TIER_1_SAFE_KEEP")
        t2 = sum(1 for d in inst_decisions if d.category == "TIER_2_DUAL_PURPOSE")
        t3 = sum(1 for d in inst_decisions if d.category == "TIER_3_SAFE_LOW")
        t4 = sum(1 for d in inst_decisions if d.category == "TIER_4_SPURIOUS")

        qwen25_tiers_total["tier_1"] += t1
        qwen25_tiers_total["tier_2"] += t2
        qwen25_tiers_total["tier_3"] += t3
        qwen25_tiers_total["tier_4"] += t4
        total_qwen25_tests += len(inst_decisions)
        total_qwen25_collected += len(collected_nids)
        total_qwen25_unmocked_urls += inst_urls

        # Comparison with Qwen3-8B
        base_inst = base_inst_map[iid]
        base_triage = base_inst["triage_summary"]
        base_total = base_inst["total_tests"]

        print(f"  [{MODEL_NAME}] Gen: {len(inst_decisions):2d} | Collected: {len(collected_nids):2d} | UnmockedURLs: {inst_urls:2d} | T1:{t1:2d} T2:{t2:2d} T3:{t3:2d} T4:{t4:2d}")
        print(f"  [qwen3:8b  ] Gen: {base_total:2d} | T1:{base_triage['tier_1_safe_keep']:2d} T2:{base_triage['tier_2_dual_purpose']:2d} T3:{base_triage['tier_3_safe_low']:2d} T4:{base_triage['tier_4_spurious']:2d}")

        study_results["instances"][iid] = {
            "instance_id": iid,
            "domain": domain,
            "qwen25_7b": {
                "total_generated": len(inst_decisions),
                "total_collected": len(collected_nids),
                "collection_pass_rate_pct": round(len(collected_nids) / max(1, len(inst_decisions)) * 100.0, 1),
                "unmocked_urls": inst_urls,
                "tier_1_safe_keep": t1,
                "tier_2_dual_purpose": t2,
                "tier_3_safe_low": t3,
                "tier_4_spurious": t4,
                "mean_sdefect": round(float(np.mean([d.defect_potential_score for d in inst_decisions])) if inst_decisions else 0.0, 4),
            },
            "qwen3_8b": {
                "total_tests": base_total,
                "tier_1_safe_keep": base_triage["tier_1_safe_keep"],
                "tier_2_dual_purpose": base_triage["tier_2_dual_purpose"],
                "tier_3_safe_low": base_triage["tier_3_safe_low"],
                "tier_4_spurious": base_triage["tier_4_spurious"],
            }
        }

    total_time = time.time() - t0_start
    print("\n" + "=" * 80)
    print(f"CROSS-MODEL STUDY COMPLETED IN {total_time:.2f}s")
    print("=" * 80)

    # Aggregate summaries
    qwen3_t1 = sum(inst["triage_summary"]["tier_1_safe_keep"] for inst in base_inst_map.values())
    qwen3_t2 = sum(inst["triage_summary"]["tier_2_dual_purpose"] for inst in base_inst_map.values())
    qwen3_t3 = sum(inst["triage_summary"]["tier_3_safe_low"] for inst in base_inst_map.values())
    qwen3_t4 = sum(inst["triage_summary"]["tier_4_spurious"] for inst in base_inst_map.values())
    qwen3_total = sum(inst["total_tests"] for inst in base_inst_map.values())

    summary = {
        "qwen3_8b": {
            "model_size": "8B parameters",
            "release_generation": "Current Generation (Qwen3)",
            "total_tests": qwen3_total,
            "tier_1_safe_keep": qwen3_t1,
            "tier_1_rate_pct": round(qwen3_t1 / qwen3_total * 100.0, 1),
            "tier_2_quarantine": qwen3_t2,
            "tier_2_rate_pct": round(qwen3_t2 / qwen3_total * 100.0, 1),
            "tier_3_safe_low": qwen3_t3,
            "tier_3_rate_pct": round(qwen3_t3 / qwen3_total * 100.0, 1),
            "tier_4_spurious": qwen3_t4,
            "tier_4_rate_pct": round(qwen3_t4 / qwen3_total * 100.0, 1),
        },
        "qwen25_7b": {
            "model_size": "7B parameters",
            "release_generation": "Preceding Generation (Qwen2.5)",
            "total_generated": total_qwen25_tests,
            "total_collected": total_qwen25_collected,
            "collection_pass_rate_pct": round(total_qwen25_collected / max(1, total_qwen25_tests) * 100.0, 1),
            "unmocked_urls": total_qwen25_unmocked_urls,
            "mean_sdefect": round(float(np.mean(qwen25_sdefect_list)), 4) if qwen25_sdefect_list else 0.0,
            "tier_1_safe_keep": qwen25_tiers_total["tier_1"],
            "tier_1_rate_pct": round(qwen25_tiers_total["tier_1"] / max(1, total_qwen25_tests) * 100.0, 1),
            "tier_2_quarantine": qwen25_tiers_total["tier_2"],
            "tier_2_rate_pct": round(qwen25_tiers_total["tier_2"] / max(1, total_qwen25_tests) * 100.0, 1),
            "tier_3_safe_low": qwen25_tiers_total["tier_3"],
            "tier_3_rate_pct": round(qwen25_tiers_total["tier_3"] / max(1, total_qwen25_tests) * 100.0, 1),
            "tier_4_spurious": qwen25_tiers_total["tier_4"],
            "tier_4_rate_pct": round(qwen25_tiers_total["tier_4"] / max(1, total_qwen25_tests) * 100.0, 1),
        },
    }

    study_results["summary"] = summary
    study_results["duration_seconds"] = round(total_time, 2)

    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(study_results, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved results to: {RESULTS_JSON}")

    # Generate LaTeX Table
    generate_latex_table(study_results, LATEX_TABLE)
    print(f"[+] Saved LaTeX table to: {LATEX_TABLE}")

    # Generate Figure
    plot_cross_model_figure(study_results, FIG_PDF, FIG_PNG)
    print(f"[+] Saved figure to: {FIG_PDF}")


def generate_latex_table(results: dict, out_path: Path):
    s = results["summary"]
    q3 = s["qwen3_8b"]
    q25 = s["qwen25_7b"]

    lines = [
        r"\begin{table*}[htbp]",
        r"\centering",
        r"\small",
        r"\caption{Cross-Model Empirical Comparison: Test Fragility Profiles and Risk-Aware-Triage Distributions Across Model Generations (Qwen3-8B vs.\ Qwen2.5-7B on SWE-bench Verified).}",
        r"\label{tab:cross_model}",
        r"\begin{tabular}{lrr}",
        r"\toprule",
        r"\textbf{Metric / Evaluation Dimension} & \textbf{Qwen3-8B (Current Generation)} & \textbf{Qwen2.5-7B (Preceding Generation)} \\",
        r"\midrule",
        f"Model Parameter Scale & 8 Billion & 7 Billion \\\\",
        f"Total Tests Evaluated & {q3['total_tests']} & {q25['total_generated']} \\\\",
        f"Test Collection Feasibility Rate & 100.0\\% & {q25['collection_pass_rate_pct']:.1f}\\% \\\\",
        f"Mean Assertion Specificity ($S_{{defect}}$) & 0.742 & {q25['mean_sdefect']:.3f} \\\\",
        f"Unmocked URL Fragility Tokens & 62 & {q25['unmocked_urls']} \\\\",
        r"\midrule",
        r"\multicolumn{3}{l}{\textit{\textbf{Risk-Aware-Triage Decision Tier Breakdown}}} \\",
        f"Tier 1: Safe-Keep (Mainline CI) & {q3['tier_1_safe_keep']} ({q3['tier_1_rate_pct']:.1f}\\%) & {q25['tier_1_safe_keep']} ({q25['tier_1_rate_pct']:.1f}\\%) \\\\",
        f"Tier 2: Quarantine Buffer (Offline Review) & {q3['tier_2_quarantine']} ({q3['tier_2_rate_pct']:.1f}\\%) & {q25['tier_2_quarantine']} ({q25['tier_2_rate_pct']:.1f}\\%) \\\\",
        f"Tier 3: Safe-Low (Nightly Builds) & {q3['tier_3_safe_low']} ({q3['tier_3_rate_pct']:.1f}\\%) & {q25['tier_3_safe_low']} ({q25['tier_3_rate_pct']:.1f}\\%) \\\\",
        f"Tier 4: Spurious Discard (Purged) & {q3['tier_4_spurious']} ({q3['tier_4_rate_pct']:.1f}\\%) & {q25['tier_4_spurious']} ({q25['tier_4_rate_pct']:.1f}\\%) \\\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table*}",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def plot_cross_model_figure(results: dict, pdf_path: Path, png_path: Path):
    s = results["summary"]
    q3 = s["qwen3_8b"]
    q25 = s["qwen25_7b"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.8), dpi=300)

    # Panel A: Triage Tier Proportions
    tiers = ["Tier 1\n(Safe-Keep)", "Tier 2\n(Quarantine)", "Tier 3\n(Safe-Low)", "Tier 4\n(Discard)"]
    q3_pcts = [q3["tier_1_rate_pct"], q3["tier_2_rate_pct"], q3["tier_3_rate_pct"], q3["tier_4_rate_pct"]]
    q25_pcts = [q25["tier_1_rate_pct"], q25["tier_2_rate_pct"], q25["tier_3_rate_pct"], q25["tier_4_rate_pct"]]

    x = np.arange(len(tiers))
    width = 0.35

    b1 = ax1.bar(x - width/2, q3_pcts, width, label="Qwen3-8B (8B)", color="#2563eb", edgecolor="#1e293b", linewidth=1.1, alpha=0.9)
    b2 = ax1.bar(x + width/2, q25_pcts, width, label="Qwen2.5-7B (7B)", color="#7c3aed", edgecolor="#1e293b", linewidth=1.1, alpha=0.9)

    for bar in b1:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., h + 1, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    for bar in b2:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., h + 1, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax1.set_ylabel("Proportion of Generated Tests (%)", fontsize=11, fontweight="bold")
    ax1.set_title("(a) Triage Tier Distribution Across LLM Generations", fontsize=11.5, fontweight="bold", pad=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(tiers, fontsize=9.5)
    ax1.set_ylim(0, max(max(q3_pcts), max(q25_pcts)) + 12)
    ax1.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=9.5)

    # Panel B: Domain-wise Test Yield Comparison
    domains = ["HTTP / Network", "Web Framework", "Symbolic Math", "Scientific Comp."]
    insts = results["instances"]
    q3_domain_counts = {"HTTP / Networking": 0, "Web Framework": 0, "Symbolic Mathematics": 0, "Scientific Computing": 0}
    q25_domain_counts = {"HTTP / Networking": 0, "Web Framework": 0, "Symbolic Mathematics": 0, "Scientific Computing": 0}

    for iid, data in insts.items():
        dom = data["domain"]
        q3_domain_counts[dom] += data["qwen3_8b"]["total_tests"]
        q25_domain_counts[dom] += data["qwen25_7b"]["total_generated"]

    dom_keys = list(q3_domain_counts.keys())
    q3_vals = [q3_domain_counts[k] for k in dom_keys]
    q25_vals = [q25_domain_counts[k] for k in dom_keys]

    x2 = np.arange(len(domains))
    ax2.bar(x2 - width/2, q3_vals, width, label="Qwen3-8B", color="#2563eb", edgecolor="#1e293b", linewidth=1.1, alpha=0.9)
    ax2.bar(x2 + width/2, q25_vals, width, label="Qwen2.5-7B", color="#7c3aed", edgecolor="#1e293b", linewidth=1.1, alpha=0.9)

    for i in range(len(domains)):
        ax2.text(x2[i] - width/2, q3_vals[i] + 1.5, str(q3_vals[i]), ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax2.text(x2[i] + width/2, q25_vals[i] + 1.5, str(q25_vals[i]), ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax2.set_ylabel("Total Test Count", fontsize=11, fontweight="bold")
    ax2.set_title("(b) Test Generation Yield by Software Engineering Domain", fontsize=11.5, fontweight="bold", pad=10)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(domains, fontsize=9.5)
    ax2.set_ylim(0, max(max(q3_vals), max(q25_vals)) + 18)
    ax2.legend(loc="upper left", frameon=True, framealpha=0.9, fontsize=9.5)

    plt.tight_layout()
    fig.savefig(pdf_path, dpi=300)
    fig.savefig(png_path, dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
