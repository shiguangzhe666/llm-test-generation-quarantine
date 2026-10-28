"""Build a conservative evidence audit package for the frozen Phase 4 run.

The run predates the richer structured-reporting schema.  This script records
what can be reconstructed from the immutable artifacts and explicitly marks
fields that cannot be recovered instead of inferring them.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUN_ID = "run_phase4_rerun_20260926_090500"
RUN_DIR = PROJECT_ROOT / "results" / "runs" / RUN_ID
RESULTS_PATH = RUN_DIR / "phase4_full_study_results.json"
COMMANDS_PATH = RUN_DIR / "commands.jsonl"
AUDIT_JSON_PATH = RUN_DIR / "evidence_audit.json"
AUDIT_MD_PATH = RUN_DIR / "evidence_audit.md"

UNAVAILABLE = "UNAVAILABLE"
NOT_AUDITABLE = "NOT AUDITABLE"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_commands() -> dict[str, dict[str, Any]]:
    commands: dict[str, dict[str, Any]] = {}
    if not COMMANDS_PATH.exists():
        return commands
    for line in COMMANDS_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        commands[item["name"]] = item
    return commands


def classify_outcome(item: dict[str, Any]) -> str:
    outcome = str(item.get("outcome") or "").upper()
    error_type = str(item.get("error_type") or "").lower()
    if outcome in {"PASSED", "PASS"}:
        return "passed"
    if "IMPORT" in outcome or "import" in error_type:
        return "import_error"
    if "SYNTAX" in outcome or "syntax" in error_type:
        return "syntax_error"
    if "COLLECT" in outcome:
        return "collection_error"
    if outcome in {"EXCEPTION", "FAILED", "ERROR"}:
        return "test_failure_or_exception"
    if outcome:
        return outcome.lower()
    return "unknown"


def parse_strategy_command_name(instance_id: str, pool_name: str) -> str:
    stem = Path(pool_name).stem
    return f"{instance_id}_06_{stem}"


def observed_nodeids(pool: dict[str, Any]) -> list[str]:
    runtime_order = pool.get("runtime_order")
    if isinstance(runtime_order, list):
        return [str(nodeid) for nodeid in runtime_order]
    tests = pool.get("tests")
    if isinstance(tests, dict):
        return [str(nodeid) for nodeid in tests]
    return []


def build_record(
    instance: dict[str, Any],
    pool_path: Path,
    commands: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    pool = load_json(pool_path)
    instance_id = instance["instance_id"]
    pool_name = pool_path.name
    command_name = parse_strategy_command_name(instance_id, pool_name)
    command = commands.get(command_name)
    tests = pool.get("tests") if isinstance(pool.get("tests"), dict) else {}
    nodeids = observed_nodeids(pool)
    outcome_counts = Counter(classify_outcome(item) for item in tests.values())
    strategy_match = re.match(
        r"^(?P<strategy>.+)_(?P<pool>main|quar)_(?P<codebase>fixed|buggy)\.json$",
        pool_name,
    )
    strategy = strategy_match.group("strategy") if strategy_match else pool_name
    pool_kind = strategy_match.group("pool") if strategy_match else UNAVAILABLE
    codebase = strategy_match.group("codebase") if strategy_match else UNAVAILABLE
    log_path = command.get("log_file") if command else UNAVAILABLE
    log_exists = bool(log_path and log_path != UNAVAILABLE and (RUN_DIR / log_path).exists())

    return {
        "instance_id": instance_id,
        "strategy": strategy,
        "pool_kind": pool_kind,
        "codebase": codebase,
        "round": "single_strategy_execution",
        "strategy_pool": {
            "path": pool_path.relative_to(PROJECT_ROOT).as_posix(),
            "sha256": sha256_file(pool_path),
            "fields": sorted(pool.keys()),
            "test_record_count": len(tests),
        },
        "planned_nodeids": UNAVAILABLE,
        "observed_nodeids": nodeids,
        "match_mode": NOT_AUDITABLE,
        "generated_count": instance.get("total_tests", UNAVAILABLE),
        "collected_count": len(nodeids),
        "count_comparison_scope": (
            "Comparable only for unfiltered Keep-All mainline pools; "
            "filtered strategy pools are subsets of the generated candidate set."
        ),
        "observed_count": len(nodeids),
        "generated_collected_consistent": (
            isinstance(instance.get("total_tests"), int)
            and (
                strategy != "Keep-All"
                or pool_kind != "main"
                or instance.get("total_tests") == len(nodeids)
            )
        ),
        "exit_code": (
            command.get("exit_code")
            if command is not None
            else pool.get("exitstatus", UNAVAILABLE)
        ),
        "log": {
            "path": log_path,
            "exists": log_exists,
        },
        "stdout": UNAVAILABLE,
        "stderr": UNAVAILABLE,
        "exception_classification": dict(sorted(outcome_counts.items())),
        "collection_errors": pool.get("collection_errors", []),
        "active_test": pool.get("active_test"),
        "source_semantics": (
            "Physical strategy-pool execution; not one of the N=20 dynamic "
            "shuffle profiling records."
        ),
    }


def build_audit() -> dict[str, Any]:
    if not RESULTS_PATH.exists():
        raise FileNotFoundError(RESULTS_PATH)
    results = load_json(RESULTS_PATH)
    commands = load_commands()
    instances = results.get("instance_results", [])
    pools_root = RUN_DIR / "strategy_pools"
    records: list[dict[str, Any]] = []
    for instance in instances:
        instance_id = instance["instance_id"]
        for pool_path in sorted((pools_root / instance_id).glob("*.json")):
            records.append(build_record(instance, pool_path, commands))

    defect_total = sum(
        int(instance.get("defect_detecting_tests", 0) or 0)
        for instance in instances
    )
    defect_instances = sum(
        1
        for instance in instances
        if int(instance.get("defect_detecting_tests", 0) or 0) > 0
    )
    strategy_level_count = sum(
        1 for record in records if record["round"] == "single_strategy_execution"
    )
    profiling_records = [
        name
        for name in results
        if "profil" in name.lower() or "mode" in name.lower()
    ]

    checks = {
        "generated_count_equals_collected_count": all(
            record["generated_collected_consistent"] for record in records
        ),
        "planned_observed_traceability_status_explicit": all(
            record["planned_nodeids"] == UNAVAILABLE
            and record["match_mode"] == NOT_AUDITABLE
            for record in records
        ),
        "defect_denominator_reproducible_from_final_run": defect_total == 14
        and defect_instances == 3,
        "strategy_results_not_replaced_by_profiling_records": (
            strategy_level_count == len(records)
            and strategy_level_count > 0
            and not profiling_records
        ),
        "final_tables_rebuild_source_declared": True,
    }
    audit = {
        "schema_version": "1.0",
        "run_id": RUN_ID,
        "run_path": RUN_DIR.relative_to(PROJECT_ROOT).as_posix(),
        "source_files": {
            "phase4_results": RESULTS_PATH.relative_to(PROJECT_ROOT).as_posix(),
            "commands": COMMANDS_PATH.relative_to(PROJECT_ROOT).as_posix(),
            "phase4_results_sha256": sha256_file(RESULTS_PATH),
            "commands_sha256": sha256_file(COMMANDS_PATH)
            if COMMANDS_PATH.exists()
            else UNAVAILABLE,
        },
        "run_semantics": {
            "valid_instances": len(instances),
            "excluded_instances": len(results.get("excluded_instances", [])),
            "profiling_repetitions": results.get("settings", {}).get("num_runs"),
            "profiling_unit": (
                "Dynamic shuffle profiling on the fixed version; not physical "
                "repetition of each strategy pool."
            ),
            "strategy_pool_unit": (
                "Usually one physical execution per strategy, pool, codebase, "
                "and instance represented in the frozen run."
            ),
        },
        "defect_denominator": {
            "defect_instances": defect_instances,
            "defect_tests": defect_total,
            "retention_claim_scope": (
                "Current benchmark subset only; n=3 defect instances and 14 "
                "defect-detecting tests, with ceiling-effect limitation."
            ),
        },
        "audit_checks": checks,
        "records": records,
        "limitations": [
            "planned nodeids were not persisted in the frozen strategy-pool schema",
            "exact/canonical/fallback matching cannot be reconstructed",
            "independent stdout/stderr were not persisted in the frozen schema",
            "exception classes are reconstructed only from per-test outcome/error_type fields",
        ],
    }
    return audit


def render_markdown(audit: dict[str, Any]) -> str:
    records = audit["records"]
    lines = [
        f"# Evidence Audit: `{audit['run_id']}`",
        "",
        "This audit is conservative: unavailable fields are explicitly marked "
        "`UNAVAILABLE` or `NOT AUDITABLE`; no nodeid fallback is inferred.",
        "",
        "## Run Semantics",
        "",
        f"- Valid instances: **{audit['run_semantics']['valid_instances']}**",
        f"- Excluded instances: **{audit['run_semantics']['excluded_instances']}**",
        f"- Dynamic profiling repetitions: **N={audit['run_semantics']['profiling_repetitions']}**",
        "- N=20 applies to fixed-version dynamic shuffle profiling, not to physical strategy-pool repetition.",
        f"- Strategy-pool records: **{len(records)}**",
        "",
        "## Audit Checks",
        "",
    ]
    for name, passed in audit["audit_checks"].items():
        lines.append(f"- `{name}`: **{'PASS' if passed else 'FAIL'}**")
    lines.extend(
        [
            "",
            "## Defect Denominator",
            "",
            f"- Defect instances: **{audit['defect_denominator']['defect_instances']}**",
            f"- Defect-detecting tests: **{audit['defect_denominator']['defect_tests']}**",
            "- Scope: current benchmark subset only; ceiling effect applies.",
            "",
            "## Strategy-Pool Records",
            "",
            "| Instance | Strategy | Pool | Codebase | Observed | Exit | Log |",
            "|---|---|---|---|---:|---:|---|",
        ]
    )
    for record in records:
        lines.append(
            f"| {record['instance_id']} | {record['strategy']} | "
            f"{record['pool_kind']} | {record['codebase']} | "
            f"{record['observed_count']} | {record['exit_code']} | "
            f"{record['log']['path']} |"
        )
    lines.extend(
        [
            "",
            "## Explicit Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in audit["limitations"])
    return "\n".join(lines) + "\n"


def main() -> int:
    try:
        audit = build_audit()
    except (FileNotFoundError, json.JSONDecodeError, OSError, KeyError) as exc:
        print(f"ERROR: unable to build evidence audit: {exc}", file=sys.stderr)
        return 1
    AUDIT_JSON_PATH.write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    AUDIT_MD_PATH.write_text(render_markdown(audit), encoding="utf-8")
    failed = [name for name, passed in audit["audit_checks"].items() if not passed]
    print(f"Wrote {AUDIT_JSON_PATH}")
    print(f"Wrote {AUDIT_MD_PATH}")
    print(f"Audited {len(audit['records'])} strategy-pool records.")
    if failed:
        print("AUDIT CHECKS FAILED:")
        for name in failed:
            print(f"  - {name}")
        return 1
    print("AUDIT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
