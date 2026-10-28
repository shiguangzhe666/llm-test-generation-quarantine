import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import audit_final_evidence as audit_module


def test_audit_has_expected_record_shape():
    audit = audit_module.build_audit()
    assert audit["run_id"] == audit_module.RUN_ID
    assert len(audit["records"]) == 135
    assert audit["defect_denominator"]["defect_instances"] == 3
    assert audit["defect_denominator"]["defect_tests"] == 14
    assert all("strategy_pool" in record for record in audit["records"])


def test_unavailable_fields_are_explicit():
    audit = audit_module.build_audit()
    for record in audit["records"]:
        assert record["planned_nodeids"] == audit_module.UNAVAILABLE
        assert record["match_mode"] == audit_module.NOT_AUDITABLE
        assert record["stdout"] == audit_module.UNAVAILABLE
        assert record["stderr"] == audit_module.UNAVAILABLE


def test_observed_nodeids_come_from_strategy_pool():
    audit = audit_module.build_audit()
    first = audit["records"][0]
    pool_path = PROJECT_ROOT / first["strategy_pool"]["path"]
    pool = json.loads(pool_path.read_text(encoding="utf-8"))
    expected = pool["runtime_order"]
    assert first["observed_nodeids"] == expected
    assert first["observed_count"] == len(expected)


def test_no_short_name_fallback_is_claimed():
    audit = audit_module.build_audit()
    assert all(
        record["match_mode"] == audit_module.NOT_AUDITABLE
        for record in audit["records"]
    )
    assert not any(
        record["match_mode"].lower() == "fallback"
        for record in audit["records"]
    )


def test_generated_collected_mismatch_is_reported(monkeypatch):
    original = audit_module.load_json

    def fake_load_json(path):
        value = original(path)
        if path == audit_module.RESULTS_PATH:
            value["instance_results"][0]["total_tests"] = "not-an-int"
        return value

    monkeypatch.setattr(audit_module, "load_json", fake_load_json)
    audit = audit_module.build_audit()
    assert not audit["audit_checks"]["generated_count_equals_collected_count"]
