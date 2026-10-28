"""
Regression tests for risk-aware triage framework:
1. Verifies that TIER_2_DUAL_PURPOSE action is QUARANTINE_INSPECT (no unearned REPAIR claim).
2. Verifies that missing flakiness data is reported as "Undefined" rather than 0.0.
3. Verifies that zero-test or zero-bug-detector conditions report "Undefined" rates.
"""

from pathlib import Path
import pytest
import tempfile

from src.triage.risk_triage import triage_suite, triage_test, TestStaticFeatures


def test_triage_action_no_unearned_repair():
    """Verify action names do not claim auto-repair."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        test_file = tdp / "test_fragile.py"
        test_file.write_text("""
import time

def test_time_sensitive_logic():
    t0 = time.time()
    assert 10 + 20 == 30
    assert 5 * 5 == 25
""", encoding="utf-8")

        report = triage_suite(test_file)
        assert report.total_tests == 1
        decision = report.decisions[0]
        assert "REPAIR" not in decision.action
        assert decision.action in ("KEEP", "QUARANTINE_INSPECT", "OPTIONAL", "DISCARD")


def test_triage_undefined_metrics_handling():
    """Verify rates report None / Undefined when denominators are zero."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        empty_file = tdp / "test_zero.py"
        empty_file.write_text("", encoding="utf-8")

        report = triage_suite(empty_file)
        assert report.total_tests == 0
        assert report.retention_rate is None
        assert "Undefined" in report.retention_rate_str
        assert report.defect_retention_rate is None
        assert "Undefined" in report.defect_retention_rate_str


def test_cold_start_flakiness_reporting():
    """Verify cold start tests without execution logs report flakiness as Undefined."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        test_file = tdp / "test_cold.py"
        test_file.write_text("""
def test_simple_assertion():
    assert 1 == 1
""", encoding="utf-8")

        report = triage_suite(test_file, flakiness_records=None)
        assert report.total_tests == 1
        decision = report.decisions[0]
        assert decision.flakiness_rate is None
        assert "Undefined" in decision.flakiness_observed_str


def test_nodeid_routing_canonical_and_collision():
    """Verify canonical nodeid preference, collision detection, and matched_observation_key."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        test_file = tdp / "test_routing.py"
        test_file.write_text("""
class TestA:
    def test_run(self):
        assert 1 == 1

class TestB:
    def test_run(self):
        assert 2 == 2
""", encoding="utf-8")

        # 1. Provide exact canonical records
        canonical_records = {
            "test_routing.py::TestA::test_run": {"flakiness_rate": 0.05},
            "test_routing.py::TestB::test_run": {"flakiness_rate": 0.25},
        }
        rep1 = triage_suite(test_file, flakiness_records=canonical_records)
        assert rep1.total_tests == 2
        d_map = {d.test_name: d for d in rep1.decisions}
        assert d_map["TestA::test_run"].matched_observation_key == "test_routing.py::TestA::test_run"
        assert d_map["TestA::test_run"].flakiness_rate == 0.05
        assert d_map["TestB::test_run"].matched_observation_key == "test_routing.py::TestB::test_run"
        assert d_map["TestB::test_run"].flakiness_rate == 0.25

        # 2. Provide ambiguous records with collision
        colliding_records = {
            "other_module.py::TestX::test_run": {"flakiness_rate": 0.10},
            "yet_another.py::TestY::test_run": {"flakiness_rate": 0.30},
        }
        rep2 = triage_suite(test_file, flakiness_records=colliding_records)
        for d in rep2.decisions:
            assert d.matched_observation_key == "COLLISION"
            assert d.flakiness_rate is None
            assert "collision" in d.flakiness_observed_str.lower()
            assert any("COLLISION" in r for r in d.reasons)

        # 3. Provide flakiness records with no matching observations
        unmatched_records = {
            "test_routing.py::TestC::test_unrelated": {"flakiness_rate": 0.10}
        }
        rep3 = triage_suite(test_file, flakiness_records=unmatched_records)
        for d in rep3.decisions:
            assert d.matched_observation_key is None
            assert d.flakiness_rate is None
            assert "no matching observation" in d.flakiness_observed_str.lower()


def test_observed_flakiness_routes_to_quarantine_or_discard():
    """Verify that any test with observed flakiness_rate > 0 is NEVER categorized as TIER_1_SAFE_KEEP."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        test_file = tdp / "test_flaky_triage.py"
        test_file.write_text("""
def test_high_defect_flaky():
    assert 1 == 1
    assert 2 == 2
    assert 3 == 3

def test_low_defect_flaky():
    x = 1
""", encoding="utf-8")

        flakiness_records = {
            "test_flaky_triage.py::test_high_defect_flaky": {"flakiness_rate": 0.0556},
            "test_flaky_triage.py::test_low_defect_flaky": {"flakiness_rate": 0.0526},
        }

        report = triage_suite(test_file, flakiness_records=flakiness_records)
        assert report.total_tests == 2
        d_map = {d.test_name: d for d in report.decisions}

        # High defect potential + flakiness -> TIER_2_DUAL_PURPOSE (QUARANTINE_INSPECT)
        d_high = d_map["test_high_defect_flaky"]
        assert d_high.category == "TIER_2_DUAL_PURPOSE"
        assert d_high.action == "QUARANTINE_INSPECT"
        assert d_high.flakiness_risk_score > 0.3
        assert "deterministic" not in " ".join(d_high.reasons)

        # Low defect potential + flakiness -> TIER_4_SPURIOUS (DISCARD)
        d_low = d_map["test_low_defect_flaky"]
        assert d_low.category == "TIER_4_SPURIOUS"
        assert d_low.action == "DISCARD"
        assert d_low.flakiness_risk_score > 0.3


def test_exception_and_method_assertion_detection():
    """Verify that with pytest.raises and self.assert* are recognized as assertions with high specificity."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        test_file = tdp / "test_exceptions.py"
        test_file.write_text("""
import pytest

def test_pytest_raises_assertion():
    with pytest.raises(ValueError):
        int("invalid")

def test_unittest_method_assertion():
    self.assertEqual(1 + 1, 2)
    self.assertTrue(True)

def test_no_assertions_at_all():
    x = 10 + 20
""", encoding="utf-8")

        report = triage_suite(test_file)
        assert report.total_tests == 3
        d_map = {d.test_name: d for d in report.decisions}

        # pytest.raises should be recognized and categorized as TIER_1_SAFE_KEEP
        d_raises = d_map["test_pytest_raises_assertion"]
        assert d_raises.defect_potential_score >= 0.5
        assert d_raises.category == "TIER_1_SAFE_KEEP"
        assert d_raises.action == "KEEP"

        # unittest assertEqual should be recognized
        d_unit = d_map["test_unittest_method_assertion"]
        assert d_unit.defect_potential_score >= 0.5
        assert d_unit.category == "TIER_1_SAFE_KEEP"

        # no assertions -> low defect score -> TIER_3_SAFE_LOW
        d_none = d_map["test_no_assertions_at_all"]
        assert d_none.defect_potential_score < 0.5
        assert d_none.category == "TIER_3_SAFE_LOW"


def test_external_url_fragility_detection():
    """Verify that unmocked external URLs are flagged with environmental fragility."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        test_file = tdp / "test_urls.py"
        test_file.write_text("""
def test_external_endpoint():
    url = "https://example.com/api/v1"
    assert url is not None
""", encoding="utf-8")

        report = triage_suite(test_file)
        assert report.total_tests == 1
        dec = report.decisions[0]
        assert dec.flakiness_risk_score > 0.0


