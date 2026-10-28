import json
from pathlib import Path
import sys
from dataclasses import asdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.triage.risk_triage import triage_suite
from src.execution.nodeid_matching import canonical_nodeid
from scripts.run_phase4_rerun import INSTANCE_CONFIGS

study_dir = PROJECT_ROOT / "results" / "runs" / "run_phase4_rerun_20260926_090500"
pools_dir = study_dir / "strategy_pools"

all_308_scored = []

for inst in sorted([p.name for p in pools_dir.iterdir() if p.is_dir()]):
    cfg = INSTANCE_CONFIGS.get(inst)
    if not cfg:
        continue
    test_dir = cfg["test_dir"]
    
    keep_file = pools_dir / inst / "Keep-All_main_fixed.json"
    if not keep_file.exists():
        continue
    with open(keep_file, "r", encoding="utf-8") as f:
        kd = json.load(f)
        canonical_nodeids = kd["runtime_order"]
    
    all_decisions = []
    for tf in sorted(test_dir.glob("test_gen_*.py")):
        trep = triage_suite(test_file=tf)
        for dec in trep.decisions:
            all_decisions.append(asdict(dec))
            
    for nid in canonical_nodeids:
        matching_dec = None
        for d in all_decisions:
            d_nid = f"{d['suite_file']}::{d['test_name']}"
            if d_nid == nid or canonical_nodeid(d_nid) == canonical_nodeid(nid):
                matching_dec = d
                break
        if matching_dec:
            all_308_scored.append({
                "inst": inst,
                "nid": nid,
                "s_defect": matching_dec["defect_potential_score"],
                "risk": matching_dec["flakiness_risk_score"]
            })
        else:
            print("Unmatched test:", inst, nid)

print(f"Total matched evaluated tests: {len(all_308_scored)}")

# Parameter Sweep on Defect Threshold S_defect in [0.2, 0.8]
print("\n" + "=" * 75)
print("THRESHOLD SENSITIVITY ANALYSIS: Defect Threshold Sweep (Risk Threshold = 0.30)")
print("=" * 75)
print(f"{'S_defect':<10} | {'Tier 1 (Keep)':<14} | {'Tier 2 (Quar)':<14} | {'Tier 3 (Low)':<14} | {'Tier 4 (Disc)':<14} | {'Total':<6}")
print("-" * 75)

for th_defect in [0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]:
    c_t1 = c_t2 = c_t3 = c_t4 = 0
    for t in all_308_scored:
        s = t["s_defect"]
        r = t["risk"]
        if s >= th_defect:
            if r <= 0.30:
                c_t1 += 1
            else:
                c_t2 += 1
        else:
            if r <= 0.30:
                c_t3 += 1
            else:
                c_t4 += 1
    pct_t1 = c_t1 / len(all_308_scored) * 100
    pct_t2 = c_t2 / len(all_308_scored) * 100
    pct_t3 = c_t3 / len(all_308_scored) * 100
    pct_t4 = c_t4 / len(all_308_scored) * 100
    default_mark = " (Default)" if abs(th_defect - 0.50) < 1e-4 else ""
    print(f"{th_defect:<10.2f}{default_mark:<10} | {c_t1:<3} ({pct_t1:4.1f}%)     | {c_t2:<3} ({pct_t2:4.1f}%)     | {c_t3:<3} ({pct_t3:4.1f}%)    | {c_t4:<3} ({pct_t4:4.1f}%)    | {c_t1+c_t2+c_t3+c_t4:<6d}")

print("\n" + "=" * 75)
print("THRESHOLD SENSITIVITY ANALYSIS: Risk Threshold Sweep (Defect Threshold = 0.50)")
print("=" * 75)
print(f"{'Risk_th':<10} | {'Tier 1 (Keep)':<14} | {'Tier 2 (Quar)':<14} | {'Tier 3 (Low)':<14} | {'Tier 4 (Disc)':<14} | {'Total':<6}")
print("-" * 75)

for th_risk in [0.10, 0.20, 0.30, 0.40, 0.50]:
    c_t1 = c_t2 = c_t3 = c_t4 = 0
    for t in all_308_scored:
        s = t["s_defect"]
        r = t["risk"]
        if s >= 0.50:
            if r <= th_risk:
                c_t1 += 1
            else:
                c_t2 += 1
        else:
            if r <= th_risk:
                c_t3 += 1
            else:
                c_t4 += 1
    pct_t1 = c_t1 / len(all_308_scored) * 100
    pct_t2 = c_t2 / len(all_308_scored) * 100
    pct_t3 = c_t3 / len(all_308_scored) * 100
    pct_t4 = c_t4 / len(all_308_scored) * 100
    default_mark = " (Default)" if abs(th_risk - 0.30) < 1e-4 else ""
    print(f"{th_risk:<10.2f}{default_mark:<10} | {c_t1:<3} ({pct_t1:4.1f}%)     | {c_t2:<3} ({pct_t2:4.1f}%)     | {c_t3:<3} ({pct_t3:4.1f}%)    | {c_t4:<3} ({pct_t4:4.1f}%)    | {c_t1+c_t2+c_t3+c_t4:<6d}")

