import ast
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.triage.risk_triage import extract_static_features_from_file, triage_test
from scripts.run_phase4_rerun import INSTANCE_CONFIGS

results_file = PROJECT_ROOT / "results" / "runs" / "run_phase4_rerun_20260926_090500" / "phase4_full_study_results.json"
with open(results_file, 'r', encoding='utf-8') as f:
    study_data = json.load(f)

print("=" * 60)
print("ANALYSIS OF TIER 2 (QUARANTINE) TESTS ACROSS ALL INSTANCES")
print("=" * 60)

quarantine_by_inst = {}
quarantine_reasons_counter = {}

for inst_data in study_data['instance_results']:
    inst_id = inst_data['instance_id']
    cfg = INSTANCE_CONFIGS.get(inst_id)
    if not cfg:
        continue
    test_dir = cfg['test_dir']
    if not test_dir.exists():
        continue
    
    inst_quar_tests = []
    for test_file in test_dir.glob("test_gen_*.py"):
        feats = extract_static_features_from_file(test_file)
        for tname, feat in feats.items():
            # In Phase 4, observed flakiness was 0.0 for deterministic suites
            # So triage was driven by static AST features
            dec = triage_test(tname, str(test_file), feat, flakiness_rate=0.0)
            if dec.category == "TIER_2_DUAL_PURPOSE":
                fragile_types = []
                for call in feat.fragile_calls:
                    if call.startswith("external_url"):
                        fragile_types.append("UNMOCKED_NETWORK_URL")
                    else:
                        fragile_types.append(f"FRAGILE_CALL:{call}")
                if feat.fragility_score >= 1.0 and not fragile_types:
                    fragile_types.append("HIGH_FRAGILITY_SCORE")
                
                inst_quar_tests.append({
                    "test_name": tname,
                    "file": test_file.name,
                    "defect_score": dec.defect_potential_score,
                    "risk_score": dec.flakiness_risk_score,
                    "fragility_score": feat.fragility_score,
                    "fragile_types": fragile_types,
                    "assertions": feat.assertions_text[:3]
                })
                for ft in fragile_types:
                    quarantine_reasons_counter[ft] = quarantine_reasons_counter.get(ft, 0) + 1
                    
    quarantine_by_inst[inst_id] = inst_quar_tests

print(f"\nTotal Instances with Quarantine Tests: {len([k for k, v in quarantine_by_inst.items() if v])}")
for inst_id, q_tests in quarantine_by_inst.items():
    if q_tests:
        print(f"\n[{inst_id}] - Total Quarantined: {len(q_tests)}")
        # Print breakdown of reasons
        r_counts = {}
        for qt in q_tests:
            for ft in qt['fragile_types']:
                r_counts[ft] = r_counts.get(ft, 0) + 1
        print(f"  Fragility signatures: {r_counts}")
        print(f"  Example test: {q_tests[0]['test_name']} in {q_tests[0]['file']}")
        print(f"    Defect potential: {q_tests[0]['defect_score']}, Risk score: {q_tests[0]['risk_score']}")
        print(f"    Sample assertions: {q_tests[0]['assertions']}")

print("\n" + "=" * 60)
print("OVERALL QUARANTINE ROOT-CAUSE DISTRIBUTION")
print("=" * 60)
for reason, count in sorted(quarantine_reasons_counter.items(), key=lambda x: x[1], reverse=True):
    print(f"  {reason:<30}: {count} occurrences")
