"""
Tests for Pareto Analysis, Clustered Standard Errors, and Non-Parametric Statistics.
"""

import math
import pytest
from src.analysis.pareto_analysis import (
    compute_vargha_delaney_a12,
    compute_wilcoxon_signed_rank,
    compute_clustered_standard_error,
    compute_wilson_confidence_interval,
    compute_pareto_frontier,
    evaluate_strategies_on_suite,
    generate_latex_table,
)


def test_vargha_delaney_a12_known_properties():
    # Identical samples should give A12 = 0.5 (negligible)
    a12, mag = compute_vargha_delaney_a12([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
    assert a12 == 0.5
    assert mag == "negligible"
    
    # Strictly superior sample should give A12 = 1.0 (large)
    a12, mag = compute_vargha_delaney_a12([10.0, 20.0, 30.0], [1.0, 2.0, 3.0])
    assert a12 == 1.0
    assert mag == "large"
    
    # Strictly inferior sample should give A12 = 0.0 (large)
    a12, mag = compute_vargha_delaney_a12([1.0, 2.0, 3.0], [10.0, 20.0, 30.0])
    assert a12 == 0.0
    assert mag == "large"
    
    # Empty sample returns undefined
    a12, mag = compute_vargha_delaney_a12([], [1.0])
    assert math.isnan(a12)
    assert mag == "undefined"


def test_wilcoxon_signed_rank():
    # Identical pairs give p-value 1.0
    s1 = [1.0, 2.0, 3.0, 4.0, 5.0]
    s2 = [1.0, 2.0, 3.0, 4.0, 5.0]
    w, p = compute_wilcoxon_signed_rank(s1, s2)
    assert w == 0.0
    assert p == 1.0
    
    # Asymmetric pairs
    a = [5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0]
    b = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    w, p = compute_wilcoxon_signed_rank(a, b)
    assert w == 0.0
    assert p < 0.01  # Highly significant difference


def test_clustered_standard_error():
    # Two clusters with constant values
    cluster_ids = ["proj_a", "proj_a", "proj_b", "proj_b"]
    vals = [10.0, 10.0, 20.0, 20.0]
    mean_val, se = compute_clustered_standard_error(cluster_ids, vals)
    assert mean_val == 15.0
    assert se > 0.0
    
    # Empty input
    m, se = compute_clustered_standard_error([], [])
    assert math.isnan(m)
    assert math.isnan(se)
    
    # Single element
    m, se = compute_clustered_standard_error(["a"], [5.0])
    assert m == 5.0
    assert se == 0.0


def test_wilson_confidence_interval():
    # Normal case: 10 successes out of 20
    p, lower, upper = compute_wilson_confidence_interval(10, 20)
    assert p == 0.5
    assert 0.25 < lower < 0.5
    assert 0.5 < upper < 0.75
    
    # Zero denominator
    p, lower, upper = compute_wilson_confidence_interval(0, 0)
    assert p is None
    assert lower is None
    assert upper is None


def test_pareto_frontier_logic():
    # Points with (ci_flakiness, bug_retention)
    # We minimize ci_flakiness and maximize bug_retention
    points = [
        {"name": "Keep-All", "flaky": 0.20, "retention": 1.0},
        {"name": "Discard-All-Flaky", "flaky": 0.0, "retention": 0.5},
        {"name": "Dominated-Strategy", "flaky": 0.30, "retention": 0.4},  # Dominated by both
        {"name": "Our-Triage", "flaky": 0.0, "retention": 1.0},  # Dominates Discard-All-Flaky
    ]
    pareto = compute_pareto_frontier(points, minimize_x="flaky", maximize_y="retention")
    names = [p["name"] for p in pareto]
    assert "Our-Triage" in names
    assert "Dominated-Strategy" not in names
    # Discard-All-Flaky is strictly dominated by Our-Triage (same flaky 0.0, lower retention 0.5 vs 1.0)
    assert "Discard-All-Flaky" not in names


def test_evaluate_strategies_on_suite():
    # Synthetic suite with 3 tests:
    # Test 1: Stable pass, detects bug (Tier 1 KEEP)
    # Test 2: Flaky (flakiness=0.1), detects bug (Tier 2 QUARANTINE_INSPECT)
    # Test 3: Stable pass, no bug (Tier 1 KEEP)
    test_records = [
        {"test_name": "t1", "flakiness_rate": 0.0, "is_bug_detecting": True, "fragility_score": 0.1, "mutation_score": 0.8},
        {"test_name": "t2", "flakiness_rate": 0.1, "is_bug_detecting": True, "fragility_score": 0.2, "mutation_score": 0.6},
        {"test_name": "t3", "flakiness_rate": 0.0, "is_bug_detecting": False, "fragility_score": 0.1, "mutation_score": 0.4},
    ]
    triage_decisions = [
        {"test_name": "t1", "action": "KEEP"},
        {"test_name": "t2", "action": "QUARANTINE_INSPECT"},
        {"test_name": "t3", "action": "KEEP"},
    ]
    
    results = evaluate_strategies_on_suite(test_records, real_bugs_total=1, triage_decisions=triage_decisions)
    
    # Check Keep-All: preserves all 2 bug-detecting tests, but has flakiness = 1/3 = 0.3333
    keep = results["Keep-All"]
    assert keep.real_bugs_retained == 1
    assert keep.defect_tests_retained == 2
    assert keep.ci_flakiness_rate > 0.0
    
    # Check Discard-All-Flaky: drops t2! Retains t1 and t3.
    # Bug is still detected via t1, but only 1 defect test retained!
    discard = results["Discard-All-Flaky"]
    assert discard.ci_flakiness_rate == 0.0
    assert discard.defect_tests_retained == 1
    
    # Check Risk-Aware Triage: t1 and t3 executable (ci flakiness = 0.0), t2 quarantined.
    # Total defect tests preserved across executable + quarantine = 2!
    triage = results["Risk-Aware-Triage"]
    assert triage.ci_flakiness_rate == 0.0
    assert triage.executable_tests == 2
    assert triage.quarantined_tests == 1
    assert triage.defect_tests_retained == 2
    assert triage.real_bugs_retained == 1


def test_generate_latex_table():
    metrics = {
        "Keep-All": {
            "exec_retention": 1.0,
            "quarantine_rate": 0.0,
            "ci_determinism": 0.85,
            "bug_retention": 1.0,
            "defect_tests_retention": 1.0,
            "mutation_score": 0.72
        }
    }
    table = generate_latex_table(metrics)
    assert r"\begin{table*}" in table
    assert "Keep-All" in table
    assert r"\bottomrule" in table
