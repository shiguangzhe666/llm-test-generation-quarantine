"""End-to-end alignment audit for the final paper and submission package."""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUN_ID = "run_phase4_rerun_20260926_090500"
RUN_FILE = PROJECT_ROOT / "results" / "runs" / RUN_ID / "phase4_full_study_results.json"
CROSS_FILE = PROJECT_ROOT / "results" / "cross_model_study_results.json"
PACKAGE = PROJECT_ROOT / "paper" / "emse_submission_package.zip"

DOCS = [
    PROJECT_ROOT / "paper" / "emse_submission" / "main.tex",
    PROJECT_ROOT / "paper" / "manuscript_en.md",
    PROJECT_ROOT / "paper" / "manuscript.md",
    PROJECT_ROOT / "paper" / "emse_submission" / "cover_letter.tex",
    PROJECT_ROOT / "paper" / "emse_submission" / "cover_letter.md",
    PROJECT_ROOT / "paper" / "rebuttal_defense_guide.md",
    PROJECT_ROOT / "paper" / "REPLICATION.md",
]

REQUIRED = [
    "run_phase4_rerun_20260926_090500",
    "13",
    "308",
    "14/14",
    "n=3",
    "24",
    "2/13",
    "0/13",
    "12/13",
    "Qwen3",
    "Qwen2.5",
    "DeepSeek-Coder",
    "CodeLlama",
    "executable-suite proportions",
    "preliminary evidence across selected model families",
]

FORBIDDEN = [
    "invariant cross-vendor fragility",
    "universal pathology",
    "generalizes across",
    "eliminates network-induced",
    "automated mock remediation",
    "Without Observed Defect Loss",
    "Cross-Model Invariance",
    "TODO",
    "TODO@invalid.example",
]


def main() -> int:
    errors: list[str] = []
    try:
        run = json.loads(RUN_FILE.read_text(encoding="utf-8"))
        cross = json.loads(CROSS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"ERROR: unable to load final evidence: {exc}")
        return 1

    if run.get("run_id") != RUN_ID:
        errors.append("final run id does not match the frozen authoritative run")
    instances = run.get("instance_results", [])
    if len(instances) != 13:
        errors.append(f"expected 13 valid instances, got {len(instances)}")
    if sum(int(x.get("total_tests", 0) or 0) for x in instances) != 308:
        errors.append("expected 308 generated tests in the primary benchmark")
    defect_instances = sum(
        int(x.get("defect_detecting_tests", 0) or 0) > 0 for x in instances
    )
    defect_tests = sum(int(x.get("defect_detecting_tests", 0) or 0) for x in instances)
    if (defect_instances, defect_tests) != (3, 14):
        errors.append("expected a 3-instance/14-test defect denominator")

    summary = cross.get("summary", {})
    expected = {
        "qwen3_8b": (308, 308, 20.1, 62),
        "qwen25_7b": (282, 201, 18.1, 61),
        "deepseek_coder_67b": (230, 189, 24.8, 59),
        "codellama_7b": (103, 77, 3.9, 4),
    }
    for key, values in expected.items():
        item = summary.get(key, {})
        actual = (
            item.get("total_generated"),
            item.get("total_collected"),
            item.get("tier_2_rate_pct"),
            item.get("unmocked_urls"),
        )
        if actual != values:
            errors.append(f"cross-model values for {key} are {actual}, expected {values}")

    for doc in DOCS:
        if not doc.exists():
            errors.append(f"missing document: {doc}")
            continue
        text = doc.read_text(encoding="utf-8")
        rel = doc.relative_to(PROJECT_ROOT)
        for phrase in REQUIRED:
            if phrase not in text:
                errors.append(f"{rel}: missing required phrase {phrase!r}")
        for phrase in FORBIDDEN:
            if phrase in text:
                errors.append(f"{rel}: forbidden phrase remains {phrase!r}")
        if "18.1%--24.8%" in text and "CodeLlama" not in text:
            errors.append(f"{rel}: cross-model range lacks the CodeLlama counterexample")
        print(f"  [checked] {rel}")

    if not PACKAGE.exists():
        errors.append(f"missing submission package: {PACKAGE}")
    else:
        required_assets = {
            "main.tex",
            "references.bib",
            "sn-jnl.cls",
            "cover_letter.tex",
            "cover_letter.md",
            "tables/tab_cross_model_comparison.tex",
            "tables/tab_hermetic_ci_benchmark.tex",
            "tables/tab_hypothesis_tests.tex",
            "tables/tab_strategy_comparison.tex",
            "figures/fig_cross_model_comparison.pdf",
            "figures/fig_hermetic_ci_comparison.pdf",
        }
        with zipfile.ZipFile(PACKAGE) as archive:
            names = set(archive.namelist())
        missing = sorted(required_assets - names)
        if missing:
            errors.append(f"submission package is missing: {', '.join(missing)}")
        else:
            print(f"  [checked] package contains {len(names)} entries")

    if errors:
        print("\nALIGNMENT AUDIT FAILED:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nALIGNMENT AUDIT PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
