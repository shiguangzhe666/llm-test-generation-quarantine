import json

with open('results/runs/run_phase4_rerun_20260926_090500/phase4_full_study_results.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("=== ALL 13 INSTANCES TIERS ===")
tot_t1 = tot_t2 = tot_t3 = tot_t4 = 0
for inst in d['instance_results']:
    t_sum = inst.get('triage_summary', {})
    t1 = t_sum.get('tier_1_safe_keep', 0)
    t2 = t_sum.get('tier_2_dual_purpose', 0)
    t3 = t_sum.get('tier_3_safe_low', 0)
    t4 = t_sum.get('tier_4_spurious', 0)
    tot_t1 += t1
    tot_t2 += t2
    tot_t3 += t3
    tot_t4 += t4
    print(f"{inst['instance_id']:<22} | Total: {inst['total_tests']:2d} | T1: {t1:2d} | T2: {t2:2d} | T3: {t3:2d} | T4: {t4:2d} | Defects: {inst['defect_detecting_tests']}")

print(f"\nTOTAL ACROSS ALL: T1={tot_t1}, T2={tot_t2}, T3={tot_t3}, T4={tot_t4}, SUM={tot_t1+tot_t2+tot_t3+tot_t4}")
