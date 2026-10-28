"""Verify that manuscript artifacts use the frozen evidence scope and numbers."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUN_ID = "run_phase4_rerun_20260926_090500"
RUN_DIR = PROJECT_ROOT / "results" / "runs" / RUN_ID
RESULTS_FILE = RUN_DIR / "phase4_full_study_results.json"
CROSS_MODEL_FILE = PROJECT_ROOT / "results" / "cross_model_study_results.json"

MANUSCRIPT_FILES = [
    PROJECT_ROOT / "paper" / "emse_submission" / "main.tex",
    PROJECT_ROOT / "paper" / "manuscript_en.md",
    PROJECT_ROOT / "paper" / "manuscript.md",
    PROJECT_ROOT / "paper" / "REPLICATION.md",
    PROJECT_ROOT / "paper" / "rebuttal_defense_guide.md",
    PROJECT_ROOT / "paper" / "emse_submission" / "cover_letter.md",
    PROJECT_ROOT / "paper" / "emse_submission" / "cover_letter.tex",
]

TABLE_FILES = [
    PROJECT_ROOT / "paper" / "tab_strategy_comparison.tex",
    PROJECT_ROOT / "paper" / "emse_submission" / "tables" / "tab_strategy_comparison.tex",
    PROJECT_ROOT / "paper" / "tab_hypothesis_tests.tex",
    PROJECT_ROOT / "paper" / "emse_submission" / "tables" / "tab_hypothesis_tests.tex",
]

REQUIRED_TEXT = [
    "N=20",
    "13",
    "308",
    "14/14",
    "62/308",
    "231/308",
    "CodeLlama",
    "executable-suite proportions",
    "current benchmark subset",
]

FORBIDDEN_TEXT = [
    "Without Observed Defect Loss",
    "eliminates network-induced CI breaks",
    "eliminates network-induced suite crashes",
    "generalizes across model architectures",
    "universal pathology",
    "automated mock remediation",
    "Cross-Model Invariance",
    "TODO",
    "TODO@invalid.example",
    "17 instances spanning",
    "18.1%--24.8% of the four",
]


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def close(value: float, expected: float, tolerance: float = 1e-4) -> bool:
    return abs(value - expected) <= tolerance


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    try:
        results = load_json(RESULTS_FILE)
        cross_model = load_json(CROSS_MODEL_FILE)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"ERROR: unable to load authoritative results: {exc}")
        return 1

    if results.get("run_id") != RUN_ID:
        fail(errors, f"phase4 run_id is {results.get('run_id')!r}, expected {RUN_ID!r}")

    instances = results.get("instance_results", [])
    excluded = results.get("excluded_instances", [])
    if len(instances) != 13:
        fail(errors, f"valid instance count is {len(instances)}, expected 13")
    if len(excluded) != 4:
        fail(errors, f"excluded instance count is {len(excluded)}, expected 4")

    generated_tests = sum(int(item.get("total_tests", 0) or 0) for item in instances)
    defect_instances = sum(
        int(item.get("defect_detecting_tests", 0) or 0) > 0 for item in instances
    )
    defect_tests = sum(int(item.get("defect_detecting_tests", 0) or 0) for item in instances)
    if generated_tests != 308:
        fail(errors, f"generated test count is {generated_tests}, expected 308")
    if defect_instances != 3 or defect_tests != 14:
        fail(
            errors,
            f"defect denominator is {defect_instances} instances/{defect_tests} tests, "
            "expected 3 instances/14 tests",
        )

    triage = results["strategy_aggregates"]["Risk-Aware-Triage"]
    expected_metrics = {
        "exec_retention": 0.7754,
        "quarantine_rate": 0.1952,
        "ci_determinism": 1.0,
        "defect_tests_retention": 1.0,
    }
    for name, expected in expected_metrics.items():
        actual = float(triage[name])
        if not close(actual, expected):
            fail(errors, f"Triage {name} is {actual}, expected {expected}")

    if results.get("settings", {}).get("num_runs") != 20:
        fail(errors, "authoritative run does not declare dynamic profiling N=20")

    expected_models = {
        "qwen3_8b": (308, 308, 20.1, 62),
        "qwen25_7b": (282, 201, 18.1, 61),
        "deepseek_coder_67b": (230, 189, 24.8, 59),
        "codellama_7b": (103, 77, 3.9, 4),
    }
    summary = cross_model.get("summary", {})
    for model, expected in expected_models.items():
        item = summary.get(model)
        if item is None:
            fail(errors, f"cross-model summary is missing {model}")
            continue
        actual = (
            item.get("total_generated"),
            item.get("total_collected"),
            item.get("tier_2_rate_pct"),
            item.get("unmocked_urls"),
        )
        if actual != expected:
            fail(errors, f"{model} summary is {actual}, expected {expected}")
    if sum(item[0] for item in expected_models.values()) != 923:
        fail(errors, "cross-model generated total invariant is incorrect")
    if sum(item[1] for item in expected_models.values()) != 775:
        fail(errors, "cross-model collected total invariant is incorrect")

    print(f"Authoritative run: {RUN_ID}")
    print(
        f"Scope: {len(instances)} valid instances, {generated_tests} generated tests, "
        f"{defect_instances} defect instances/{defect_tests} defect tests"
    )
    print(
        "Triage: 19.5% instance-mean quarantine, 20.1% test-weighted quarantine, "
        "77.5% instance-mean non-quarantine retention, 231/308 test-weighted"
    )
    print("Cross-model: 923 generated, 775 collected; CodeLlama is a low-fragility counterexample")

    for path in MANUSCRIPT_FILES + TABLE_FILES:
        if not path.exists():
            fail(errors, f"missing artifact: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(PROJECT_ROOT)
        for phrase in FORBIDDEN_TEXT:
            if phrase in text:
                fail(errors, f"{relative}: forbidden legacy phrase {phrase!r}")
        if path in MANUSCRIPT_FILES:
            for phrase in REQUIRED_TEXT:
                if phrase not in text:
                    fail(errors, f"{relative}: missing required evidence phrase {phrase!r}")
        if "77.9" in text or "99.7%" in text:
            fail(errors, f"{relative}: obsolete final-run value remains")
        print(f"  [checked] {relative}")

    if errors:
        print("\nSYNC ERRORS:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nSYNC CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
