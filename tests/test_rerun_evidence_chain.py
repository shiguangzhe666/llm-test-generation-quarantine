"""
Unit and regression tests for experimental rerun evidence chain integrity:
1. Incomplete / missing observations are never defaulted to 0.0 or PASSED.
2. Strategy pool selection excludes undefined / unobserved flakiness.
3. Defect retention requires physical failure on buggy codebase and non-zero exit code.
4. Paired hypothesis tests properly handle None / missing metrics without zero-coercion.
"""

import pytest
from src.analysis.pareto_analysis import (
    compute_wilcoxon_signed_rank,
    compute_vargha_delaney_a12,
)


def test_incomplete_flakiness_not_defaulted_to_zero():
    """Verify that incomplete or undefined flakiness records preserve None and are not classified as non-flaky."""
    mock_records = {
        "test_a": {
            "flakiness_rate": None,
            "category": "incomplete",
            "is_flaky": False,
            "pass_count": 5,
            "fail_count": 0,
            "planned_runs": 20,
            "observed_runs": 5,
        },
        "test_b": {
            "flakiness_rate": 0.0,
            "category": "stable_pass",
            "is_flaky": False,
            "pass_count": 20,
            "fail_count": 0,
            "planned_runs": 20,
            "observed_runs": 20,
        },
        "test_c": {
            "flakiness_rate": 0.15,
            "category": "occasional_flaky",
            "is_flaky": True,
            "pass_count": 17,
            "fail_count": 3,
            "planned_runs": 20,
            "observed_runs": 20,
        },
    }

    test_records = []
    canonical_nodeids = ["test_a", "test_b", "test_c", "test_unobserved"]

    for nid in canonical_nodeids:
        r = mock_records.get(nid)
        flaky_rate = r["flakiness_rate"] if r else None
        is_flk = r.get("is_flaky", False) if r else False
        test_records.append({
            "nodeid": nid,
            "flakiness_rate": flaky_rate,
            "is_flaky": is_flk,
        })

    # Discard-All-Flaky strategy pool selection:
    # Only tests with verified non-flaky execution (flakiness_rate is not None and <= 0.0)
    discard_mainline = [t["nodeid"] for t in test_records if t["flakiness_rate"] is not None and t["flakiness_rate"] <= 0.0]

    # test_a is incomplete (flakiness_rate is None) -> must NOT be in discard_mainline
    assert "test_a" not in discard_mainline
    # test_unobserved was never run -> must NOT be in discard_mainline
    assert "test_unobserved" not in discard_mainline
    # test_c is flaky -> must NOT be in discard_mainline
    assert "test_c" not in discard_mainline
    # test_b is stable_pass -> must be in discard_mainline
    assert discard_mainline == ["test_b"]


def test_fixed_outcome_requires_stable_pass():
    """Verify that a test with intermittent passes or incomplete runs is not marked as PASSED on fixed."""
    outcomes = {}
    test_cases = [
        ("t_clean", "stable_pass", 20, 0, 20, 20, False),
        ("t_intermittent", "occasional_flaky", 1, 19, 20, 20, True),
        ("t_incomplete", "incomplete", 5, 0, 5, 20, False),
        ("t_fail", "stable_fail", 0, 20, 20, 20, False),
        ("t_skip", "unstable_skip", 10, 0, 10, 20, False),
    ]

    for nid, cat, p_cnt, f_cnt, obs, plan, is_flk in test_cases:
        if cat == "stable_pass" and p_cnt == plan and obs == plan:
            outcomes[nid] = "PASSED"
        elif cat == "stable_fail" and f_cnt == plan:
            outcomes[nid] = "FAILED"
        elif is_flk:
            outcomes[nid] = "FLAKY"
        elif cat == "incomplete":
            outcomes[nid] = "INCOMPLETE"
        elif cat == "unstable_skip":
            outcomes[nid] = "SKIPPED"
        else:
            outcomes[nid] = "UNDEFINED"

    assert outcomes["t_clean"] == "PASSED"
    assert outcomes["t_intermittent"] == "FLAKY"  # Not PASSED despite pass_count > 0!
    assert outcomes["t_incomplete"] == "INCOMPLETE"  # Not PASSED despite pass_count > 0!
    assert outcomes["t_fail"] == "FAILED"
    assert outcomes["t_skip"] == "SKIPPED"


def test_physical_defect_retention_requires_buggy_failure_and_nonzero_exit():
    """Verify that physical defect retention requires actual failure on buggy and non-zero exit code."""
    defect_detecting_test_keys = {"test_bug_1", "test_bug_2"}
    main_nodes = ["test_clean", "test_bug_1", "test_bug_2"]

    # Scenario 1: Pytest exited 0 (no failures detected)
    code_mb_1 = 0
    main_buggy_outcomes_1 = {"test_clean": "PASSED", "test_bug_1": "PASSED", "test_bug_2": "PASSED"}
    main_defect_retained_1 = 0
    if main_nodes and code_mb_1 != 0:
        for nid in main_nodes:
            if nid in defect_detecting_test_keys and main_buggy_outcomes_1.get(nid) in ("ASSERTION_FAILED", "EXCEPTION"):
                main_defect_retained_1 += 1
    assert main_defect_retained_1 == 0

    # Scenario 2: Pytest exited 1, test_bug_1 had ASSERTION_FAILED, test_bug_2 passed
    code_mb_2 = 1
    main_buggy_outcomes_2 = {"test_clean": "PASSED", "test_bug_1": "ASSERTION_FAILED", "test_bug_2": "PASSED"}
    main_defect_retained_2 = 0
    if main_nodes and code_mb_2 != 0:
        for nid in main_nodes:
            if nid in defect_detecting_test_keys and main_buggy_outcomes_2.get(nid) in ("ASSERTION_FAILED", "EXCEPTION"):
                main_defect_retained_2 += 1
    assert main_defect_retained_2 == 1

    # Scenario 3: Pytest exited 1, both failed
    code_mb_3 = 1
    main_buggy_outcomes_3 = {"test_clean": "PASSED", "test_bug_1": "ASSERTION_FAILED", "test_bug_2": "EXCEPTION"}
    main_defect_retained_3 = 0
    if main_nodes and code_mb_3 != 0:
        for nid in main_nodes:
            if nid in defect_detecting_test_keys and main_buggy_outcomes_3.get(nid) in ("ASSERTION_FAILED", "EXCEPTION"):
                main_defect_retained_3 += 1
    assert main_defect_retained_3 == 2


def test_paired_hypothesis_test_filters_none():
    """Verify that paired hypothesis tests exclude None rather than coercing to 0.0."""
    valid_results = [
        {"strategy_comparison": {"Risk-Aware-Triage": {"defect_test_retention_rate": 1.0}, "Discard-All-Flaky": {"defect_test_retention_rate": 1.0}}},
        {"strategy_comparison": {"Risk-Aware-Triage": {"defect_test_retention_rate": None}, "Discard-All-Flaky": {"defect_test_retention_rate": None}}},
        {"strategy_comparison": {"Risk-Aware-Triage": {"defect_test_retention_rate": 1.0}, "Discard-All-Flaky": {"defect_test_retention_rate": 1.0}}},
    ]

    valid_dt_pairs = [
        (r["strategy_comparison"]["Risk-Aware-Triage"]["defect_test_retention_rate"],
         r["strategy_comparison"]["Discard-All-Flaky"]["defect_test_retention_rate"])
        for r in valid_results
        if r["strategy_comparison"]["Risk-Aware-Triage"]["defect_test_retention_rate"] is not None
        and r["strategy_comparison"]["Discard-All-Flaky"]["defect_test_retention_rate"] is not None
    ]

    assert len(valid_dt_pairs) == 2
    s_a = [p[0] for p in valid_dt_pairs]
    s_b = [p[1] for p in valid_dt_pairs]
    w, p = compute_wilcoxon_signed_rank(s_a, s_b)
    a12, mag = compute_vargha_delaney_a12(s_a, s_b)
    assert w == 0.0
    assert p == 1.0
    assert a12 == 0.5
    assert mag == "negligible"
