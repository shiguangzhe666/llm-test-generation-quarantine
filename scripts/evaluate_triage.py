import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.triage.risk_triage import triage_suite


def run_triage_benchmark(output_dir: Path = None):
    results_file = PROJECT_ROOT / "results" / "gate2" / "gate2_pilot_results.json"
    if not results_file.exists():
        raise FileNotFoundError(f"Pilot calibration results file not found: {results_file}")

    with open(results_file, encoding="utf-8") as f:
        g2 = json.load(f)

    # 1. Identify all ground truth bug-detecting tests
    bug_detecting_keys = set()
    for r in g2.get("results", []):
        for b in r.get("bug_detection_list", []):
            if b.get("is_bug_detecting"):
                bug_detecting_keys.add(f"{r['instance_id']}::{b['key']}")

    print(f"Total Ground-Truth Bug-Detecting Tests: {len(bug_detecting_keys)}")
    for k in sorted(bug_detecting_keys):
        print(f"  ★ {k}")

    # 2. Run Triage across all generated tests with real calibration records
    total_tests = 0
    triage_counts = {"KEEP": 0, "QUARANTINE_INSPECT": 0, "OPTIONAL": 0, "DISCARD": 0}
    executable_kept_bug_detectors = 0
    quarantined_bug_detectors = 0
    discarded_bug_detectors = 0
    decisions = []

    for r in g2.get("results", []):
        iid = r["instance_id"]
        # Build flakiness lookup map from real calibration observations
        flakiness_map = {}
        for item in r.get("flakiness_summary", []):
            key = item.get("key", "")
            flakiness_map[key] = item
            flakiness_map[item.get("test_name", "")] = item

        gen_dir = PROJECT_ROOT / "data" / "pilot_gate2" / iid / "generated_tests"
        if not gen_dir.exists():
            continue

        for tf in sorted(gen_dir.glob("test_gen_*.py")):
            suite_report = triage_suite(tf, flakiness_records=flakiness_map)
            for d in suite_report.decisions:
                total_tests += 1
                full_key = f"{iid}::{tf.name}::{d.test_name}"
                is_bd = full_key in bug_detecting_keys
                triage_counts[d.action] = triage_counts.get(d.action, 0) + 1

                if is_bd:
                    if d.action == "KEEP":
                        executable_kept_bug_detectors += 1
                    elif d.action == "QUARANTINE_INSPECT":
                        quarantined_bug_detectors += 1
                    else:
                        discarded_bug_detectors += 1

                decisions.append({
                    "key": full_key,
                    "action": d.action,
                    "category": d.category,
                    "defect_score": d.defect_potential_score,
                    "risk_score": d.flakiness_risk_score,
                    "flakiness_observed": d.flakiness_observed_str,
                    "is_bug_detecting": is_bd,
                })

    total_gt = len(bug_detecting_keys)
    if total_gt > 0:
        exec_ret_rate = round(executable_kept_bug_detectors / total_gt, 4)
        exec_ret_str = f"{exec_ret_rate:.1%} ({executable_kept_bug_detectors}/{total_gt})"
        quar_ret_rate = round(quarantined_bug_detectors / total_gt, 4)
        quar_ret_str = f"{quar_ret_rate:.1%} ({quarantined_bug_detectors}/{total_gt})"
        combined_rate = round((executable_kept_bug_detectors + quarantined_bug_detectors) / total_gt, 4)
        combined_str = f"{combined_rate:.1%} ({executable_kept_bug_detectors + quarantined_bug_detectors}/{total_gt})"
    else:
        exec_ret_rate = None
        exec_ret_str = "Undefined (0 bug-detecting tests)"
        quar_ret_rate = None
        quar_ret_str = "Undefined (0 bug-detecting tests)"
        combined_rate = None
        combined_str = "Undefined (0 bug-detecting tests)"

    print("\n" + "=" * 60)
    print("UNSUPERVISED TRIAGE BENCHMARK RESULTS")
    print("=" * 60)
    print(f"Total tests evaluated:               {total_tests}")
    print("Triage Actions distribution:")
    for action, cnt in triage_counts.items():
        pct = cnt / total_tests if total_tests else 0
        print(f"  - {action:20s}: {cnt:3d} ({pct:.1%})")
    print("-" * 60)
    print(f"Ground-Truth Bug-Detectors:          {total_gt}")
    print(f"  - Retained for Execution (KEEP):   {executable_kept_bug_detectors} ({exec_ret_str})")
    print(f"  - Quarantined (INSPECT):           {quarantined_bug_detectors} ({quar_ret_str})")
    print(f"  - Discarded (False Negatives):     {discarded_bug_detectors}")
    print(f"Defect Retention (Pure Executable):  {exec_ret_str}")
    print(f"Defect Retention (Broad + Quarantine): {combined_str}")
    print("=" * 60)

    report_payload = {
        "total_tests": total_tests,
        "triage_distribution": triage_counts,
        "ground_truth_bug_detectors": total_gt,
        "executable_retained_bug_detectors": executable_kept_bug_detectors,
        "quarantined_bug_detectors": quarantined_bug_detectors,
        "discarded_bug_detectors": discarded_bug_detectors,
        "executable_defect_retention_rate": exec_ret_rate,
        "executable_defect_retention_rate_str": exec_ret_str,
        "quarantined_defect_rate": quar_ret_rate,
        "quarantined_defect_rate_str": quar_ret_str,
        "combined_defect_retention_rate": combined_rate,
        "combined_defect_retention_rate_str": combined_str,
        "decisions": decisions,
    }

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / "triage_benchmark_results.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report_payload, f, indent=2)
        print(f"\nSaved benchmark results to: {out_path}")

    return report_payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate triage framework against real calibration data.")
    parser.add_argument("--run-id", type=str, default=None, help="Optional run_id to store results under results/runs/<run_id>")
    parser.add_argument("--output-dir", type=str, default=None, help="Explicit output directory")
    args = parser.parse_args()

    target_dir = None
    if args.output_dir:
        target_dir = Path(args.output_dir)
    elif args.run_id:
        target_dir = PROJECT_ROOT / "results" / "runs" / args.run_id

    run_triage_benchmark(output_dir=target_dir)
