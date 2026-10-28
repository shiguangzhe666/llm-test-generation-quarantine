"""
Cold-Start / Zero-History Risk-Aware Test Triage Framework.

Provides unsupervised triage for newly generated LLM test suites without
requiring historical CI execution logs or labeled mutation datasets.

Methodology & Design Decisions:
1. Feature Extraction:
   - Intra-test Assertion Predicate Diversity (H_semantic heuristic):
     Clusters normalized assertion predicates within a test to quantify semantic breadth.
     (Note: Cross-generation semantic entropy across LLM completion distributions
     is an experimental module subject to empirical calibration in Phase III).
   - Assertion Specificity Index: Quantifies verification rigor (equality vs weak presence/truthiness).
   - Environmental Fragility Index: AST scan for non-deterministic primitives (time, threading, random, unseeded io).
   - Observed Flakiness Rate (when available from repeated execution):
     Explicitly distinguished from static risk. If no execution data exists (total runs = 0),
     flakiness is explicitly flagged as None / "Undefined", NOT assumed to be 0.0.
2. Unsupervised Triage Classification:
   - Balances Defect-Detection Potential against Flakiness Risk.
   - Categorizes tests into:
     * TIER_1_SAFE_KEEP: High defect value, deterministic -> KEEP.
     * TIER_2_DUAL_PURPOSE: High defect value, unstable -> QUARANTINE_INSPECT.
       (Note: Quarantined for manual review or future repair module. Automated test
       repair is not yet implemented; no claim of automated repair is made).
     * TIER_3_SAFE_LOW: Low defect value, deterministic -> OPTIONAL.
     * TIER_4_SPURIOUS: Low defect value, high instability -> DISCARD.
3. Denominator Transparency:
   - When denominators are 0 (e.g. 0 tests, 0 bug-detecting tests, 0 execution runs),
     rates are reported as None / "Undefined", preventing misleading 0% or 100% metrics.
"""

import ast
import json
import math
import os
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from src.execution.nodeid_matching import canonical_nodeid, find_test_in_report_data


# ---------- Non-Deterministic API Catalog ----------

FRAGILE_MODULES = {
    "random", "time", "datetime", "uuid", "threading", "multiprocessing",
    "socket", "subprocess", "tempfile", "shutil"
}

FRAGILE_FUNCTIONS = {
    "sleep", "now", "utcnow", "random", "randint", "choice", "uuid4",
    "time", "monotonic", "perf_counter"
}


# ---------- Static Feature Extractor ----------

@dataclass
class TestStaticFeatures:
    """Static features extracted from an individual test function AST."""
    __test__ = False
    test_name: str
    num_assertions: int = 0
    equality_assertions: int = 0
    presence_assertions: int = 0
    boolean_assertions: int = 0
    specificity_score: float = 0.0
    fragility_score: float = 0.0
    fragile_calls: List[str] = field(default_factory=list)
    ast_node_count: int = 0
    ast_depth: int = 0
    assertions_text: List[str] = field(default_factory=list)


class TestFunctionVisitor(ast.NodeVisitor):
    """Inspects an individual test function to extract structural and assertion metrics."""
    __test__ = False

    def __init__(self, func_name: str):
        self.func_name = func_name
        self.found = False
        self.features = TestStaticFeatures(test_name=func_name)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name == self.func_name:
            self.found = True
            self.features.ast_node_count = sum(1 for _ in ast.walk(node))
            self._analyze_body(node)
        self.generic_visit(node)

    def _analyze_body(self, func_node: ast.FunctionDef):
        for node in ast.walk(func_node):
            # 1. Assert statements: assert ...
            if isinstance(node, ast.Assert):
                self.features.num_assertions += 1
                try:
                    assert_text = ast.unparse(node.test)
                    self.features.assertions_text.append(assert_text)
                except Exception:
                    pass
                self._classify_assertion(node.test)

            # 2. Context manager assertions: with pytest.raises(...), with self.assertRaises(...)
            elif isinstance(node, ast.With):
                for item in node.items:
                    ce = item.context_expr
                    if isinstance(ce, ast.Call):
                        name = ""
                        if isinstance(ce.func, ast.Name):
                            name = ce.func.id
                        elif isinstance(ce.func, ast.Attribute):
                            name = ce.func.attr
                        low_name = name.lower()
                        if "raises" in low_name or "warns" in low_name:
                            self.features.num_assertions += 1
                            self.features.equality_assertions += 1  # Specific exception type check is exact
                            try:
                                self.features.assertions_text.append(ast.unparse(ce))
                            except Exception:
                                pass

            # 3. Method call assertions: self.assertEqual(...), and fragile function calls
            elif isinstance(node, ast.Call):
                name = ""
                if isinstance(node.func, ast.Name):
                    name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    name = node.func.attr

                # Unittest-style assertion methods
                if isinstance(node.func, ast.Attribute) and name.startswith("assert"):
                    self.features.num_assertions += 1
                    try:
                        self.features.assertions_text.append(ast.unparse(node))
                    except Exception:
                        pass
                    low_name = name.lower()
                    if "equal" in low_name or "raises" in low_name:
                        self.features.equality_assertions += 1
                    elif "in" in low_name or "is" in low_name:
                        self.features.presence_assertions += 1
                    else:
                        self.features.boolean_assertions += 1

                # Fragile function calls
                if name in FRAGILE_FUNCTIONS:
                    self.features.fragility_score += 1.0
                    self.features.fragile_calls.append(name)

            # 4. Fragile external string literals (e.g. unmocked external URLs)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value.startswith(("http://", "https://")):
                    self.features.fragility_score += 1.5  # Severe environmental fragility (unmocked network I/O)
                    self.features.fragile_calls.append("external_url:" + node.value[:30])

        # Compute specificity score
        total_asserts = max(self.features.num_assertions, 1)
        # Weighted: equality=1.0, presence=0.4, boolean=0.2
        raw_spec = (
            self.features.equality_assertions * 1.0 +
            self.features.presence_assertions * 0.4 +
            self.features.boolean_assertions * 0.2
        ) / total_asserts
        self.features.specificity_score = round(min(raw_spec, 1.0), 4)

    def _classify_assertion(self, test_node: ast.AST):
        if isinstance(test_node, ast.Compare):
            has_eq = any(isinstance(op, (ast.Eq, ast.NotEq)) for op in test_node.ops)
            has_in = any(isinstance(op, (ast.In, ast.NotIn)) for op in test_node.ops)
            has_is = any(isinstance(op, (ast.Is, ast.IsNot)) for op in test_node.ops)

            if has_eq:
                self.features.equality_assertions += 1
            elif has_in or has_is:
                self.features.presence_assertions += 1
            else:
                self.features.equality_assertions += 1
        else:
            self.features.boolean_assertions += 1


def extract_static_features_from_file(file_path: Path) -> Dict[str, TestStaticFeatures]:
    """Extract static features for all test functions in a test file."""
    source = file_path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}

    features_map = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            visitor = TestFunctionVisitor(node.name)
            visitor.visit(node)
            features_map[node.name] = visitor.features
        elif isinstance(node, ast.ClassDef) and (node.name.startswith("Test") or node.name.endswith("Test")):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                    qualified_name = f"{node.name}::{item.name}"
                    visitor = TestFunctionVisitor(item.name)
                    visitor.visit(item)
                    visitor.features.test_name = qualified_name
                    features_map[qualified_name] = visitor.features

    return features_map


# ---------- Assertion Semantic Diversity Heuristic ----------

def compute_assertion_semantic_entropy(assertions: List[str]) -> float:
    """
    Computes Shannon semantic entropy across normalized assertion predicates.
    Identical or whitespace-normalized assertion predicates fall into the same cluster.
    """
    if not assertions:
        return 0.0

    clusters = {}
    for a in assertions:
        norm = re.sub(r"\s+", " ", a.strip())
        clusters[norm] = clusters.get(norm, 0) + 1

    total = len(assertions)
    entropy = 0.0
    for count in clusters.values():
        p = count / total
        entropy -= p * math.log2(p)

    return round(entropy, 4)


# ---------- Unsupervised Triage Decision Engine ----------

@dataclass
class TriageDecision:
    """Triage verdict and scores for an individual test."""
    test_name: str
    suite_file: str
    defect_potential_score: float
    flakiness_risk_score: float
    category: str  # TIER_1_SAFE_KEEP, TIER_2_DUAL_PURPOSE, TIER_3_SAFE_LOW, TIER_4_SPURIOUS
    action: str    # "KEEP", "QUARANTINE_INSPECT", "OPTIONAL", "DISCARD"
    flakiness_rate: Optional[float]
    flakiness_observed_str: str
    static_fragility_score: float = 0.0
    matched_observation_key: Optional[str] = None
    reasons: List[str] = field(default_factory=list)


@dataclass
class TriageSuiteReport:
    """Aggregated triage report for a test suite with explicit separation between executable retention and quarantine."""
    suite_file: str
    total_tests: int
    tier_1_count: int
    tier_2_count: int
    tier_3_count: int
    tier_4_count: int
    # Strict separation: executable retained vs quarantined
    executable_retention_count: int = 0
    quarantined_count: int = 0
    optional_count: int = 0
    discarded_count: int = 0
    executable_retention_rate: Optional[float] = None
    executable_retention_rate_str: str = "Undefined"
    quarantine_rate: Optional[float] = None
    quarantine_rate_str: str = "Undefined"
    # Legacy broad pool metrics (kept for compatibility, explicitly documented)
    retention_rate: Optional[float] = None          # (tier_1 + tier_2) / total_tests
    retention_rate_str: str = "Undefined"
    # Ground-truth defect metrics
    gt_total_count: Optional[int] = None
    gt_retained_executable_count: int = 0
    gt_quarantined_count: int = 0
    gt_discarded_count: int = 0
    defect_retention_rate_executable: Optional[float] = None
    defect_retention_rate_executable_str: str = "Undefined"
    defect_quarantine_rate: Optional[float] = None
    defect_quarantine_rate_str: str = "Undefined"
    defect_retention_rate: Optional[float] = None   # (retained + quarantined) / total_gt
    defect_retention_rate_str: str = "Undefined"
    decisions: List[TriageDecision] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def triage_test(
    test_name: str,
    suite_file: str,
    static_feats: TestStaticFeatures,
    flakiness_rate: Optional[float] = None,
    entropy: float = 0.0,
    matched_observation_key: Optional[str] = None,
    custom_flakiness_str: Optional[str] = None,
) -> TriageDecision:
    """
    Score and triage a test based on cold-start signals.
    Handles flakiness_rate=None as 'Undefined' rather than assuming 0.0 deterministic.
    """
    reasons = []

    # 1. Defect Potential Score (0.0 to 1.0)
    assert_factor = min(static_feats.num_assertions / 3.0, 1.0) * 0.4
    spec_factor = static_feats.specificity_score * 0.4
    entropy_penalty = min(entropy / 2.0, 1.0) * 0.2
    defect_score = round(max(0.0, min(1.0, assert_factor + spec_factor - entropy_penalty + 0.2)), 4)

    # 2. Flakiness Risk Score (0.0 to 1.0)
    fragility_penalty = min(static_feats.fragility_score * 0.3, 0.6)
    
    if flakiness_rate is not None:
        if flakiness_rate > 0.0:
            # Any observed flakiness violates determinism; baseline penalty 0.35 ensures risk_score > 0.3
            flaky_obs_penalty = 0.35 + flakiness_rate * 0.65
            reasons.append(f"Empirical flakiness observed ({flakiness_rate:.1%}); classified as unstable execution risk.")
        else:
            flaky_obs_penalty = 0.0
        risk_score = round(min(1.0, fragility_penalty + flaky_obs_penalty), 4)
        flakiness_str = f"{flakiness_rate:.1%}"
    else:
        # Cold start without execution logs: risk relies on static fragility
        risk_score = round(min(1.0, fragility_penalty), 4)
        flakiness_str = custom_flakiness_str or "Undefined (no execution data)"
        reasons.append(f"Cold start: Flakiness rate is {flakiness_str}; risk assessed solely on static AST fragility.")

    # 3. Categorization
    if defect_score >= 0.5:
        if risk_score <= 0.3:
            cat = "TIER_1_SAFE_KEEP"
            action = "KEEP"
            reasons.append("High defect-detection potential with deterministic execution profile.")
        else:
            cat = "TIER_2_DUAL_PURPOSE"
            action = "QUARANTINE_INSPECT"
            reasons.append(
                "High defect-detection potential BUT exhibits instability risk; "
                "quarantine for inspection (auto-repair is not yet implemented)."
            )
    else:
        if risk_score <= 0.3:
            cat = "TIER_3_SAFE_LOW"
            action = "OPTIONAL"
            reasons.append("Low defect detection potential with low instability risk.")
        else:
            cat = "TIER_4_SPURIOUS"
            action = "DISCARD"
            reasons.append("Low defect detection potential accompanied by high instability risk; discard.")

    return TriageDecision(
        test_name=test_name,
        suite_file=suite_file,
        defect_potential_score=defect_score,
        flakiness_risk_score=risk_score,
        category=cat,
        action=action,
        flakiness_rate=flakiness_rate,
        flakiness_observed_str=flakiness_str,
        static_fragility_score=static_feats.fragility_score,
        matched_observation_key=matched_observation_key,
        reasons=reasons,
    )


def triage_suite(
    test_file: Path,
    flakiness_records: Optional[dict] = None,
    ground_truth_bug_detectors: Optional[Set[str]] = None,
) -> TriageSuiteReport:
    """
    Triage all tests in a test file and produce an aggregated report with
    strict zero-denominator handling.
    """
    test_path = Path(test_file)
    static_map = extract_static_features_from_file(test_path)
    flakiness = flakiness_records or {}

    decisions: List[TriageDecision] = []
    for tname, feats in static_map.items():
        # Strict Canonical NodeID Routing with Ambiguity / Collision Check:
        matched_key = None
        collision_detected = False
        frate = None
        custom_str = None

        if flakiness:
            cand_p = tname if (".py" in tname or tname.startswith(f"{test_path.name}::")) else f"{test_path.name}::{tname}"
            matched_k, t_val, status = find_test_in_report_data(cand_p, flakiness)
            if status == "AMBIGUOUS":
                collision_detected = True
                matched_key = "COLLISION"
            elif status in ("EXACT", "CANONICAL"):
                matched_key = matched_k
            else:
                short_target = tname.split("::")[-1]
                short_cands = [k for k in flakiness if k.split("::")[-1] == short_target]
                if len(short_cands) > 1:
                    collision_detected = True
                    matched_key = "COLLISION"
                else:
                    matched_key = None

            if collision_detected:
                frate = None
                custom_str = f"Undefined (collision: multiple observations match '{tname}')"
            elif matched_key is not None:
                t_data = flakiness[matched_key]
                if isinstance(t_data, dict):
                    frate = t_data.get("flakiness_rate")
                elif hasattr(t_data, "flakiness_rate"):
                    frate = t_data.flakiness_rate
                elif isinstance(t_data, (int, float)):
                    frate = float(t_data)
            else:
                frate = None
                custom_str = f"Undefined (no matching observation for '{tname}')"

        # Compute intra-test assertion semantic entropy
        ent = compute_assertion_semantic_entropy(feats.assertions_text)

        dec = triage_test(
            test_name=tname,
            suite_file=test_path.name,
            static_feats=feats,
            flakiness_rate=frate,
            entropy=ent,
            matched_observation_key=matched_key,
            custom_flakiness_str=custom_str,
        )
        if collision_detected:
            dec.reasons.append(f"COLLISION: Multiple observations match short test name '{tname}'; ambiguous routing.")
        elif matched_key is None and flakiness:
            dec.reasons.append(f"No matching observation found in execution records for '{tname}'.")

        decisions.append(dec)

    total_tests = len(decisions)
    t1 = sum(1 for d in decisions if d.category == "TIER_1_SAFE_KEEP")
    t2 = sum(1 for d in decisions if d.category == "TIER_2_DUAL_PURPOSE")
    t3 = sum(1 for d in decisions if d.category == "TIER_3_SAFE_LOW")
    t4 = sum(1 for d in decisions if d.category == "TIER_4_SPURIOUS")

    # Executable retention rate (Tier 1 safe keep ONLY, no quarantine mixed in)
    if total_tests > 0:
        exec_ret_rate = round(t1 / total_tests, 4)
        exec_ret_rate_str = f"{exec_ret_rate * 100:.1f}% ({t1}/{total_tests})"
        quar_rate = round(t2 / total_tests, 4)
        quar_rate_str = f"{quar_rate * 100:.1f}% ({t2}/{total_tests})"
        legacy_ret_rate = round((t1 + t2) / total_tests, 4)
        legacy_ret_rate_str = f"{legacy_ret_rate * 100:.1f}%"
    else:
        exec_ret_rate = None
        exec_ret_rate_str = "Undefined (0 total tests)"
        quar_rate = None
        quar_rate_str = "Undefined (0 total tests)"
        legacy_ret_rate = None
        legacy_ret_rate_str = "Undefined (0 total tests)"

    # Ground-truth defect detection separation
    gt_total = None
    gt_retained_exec = 0
    gt_quar = 0
    gt_disc = 0
    gt_exec_rate = None
    gt_exec_rate_str = "Undefined (no ground-truth detectors specified)"
    gt_quar_rate = None
    gt_quar_rate_str = "Undefined (no ground-truth detectors specified)"
    legacy_gt_rate = None
    legacy_gt_rate_str = "Undefined (no ground-truth detectors specified)"

    if ground_truth_bug_detectors:
        gt_total = len(ground_truth_bug_detectors)
        gt_dict = {g: True for g in ground_truth_bug_detectors}
        for d in decisions:
            # Canonical match first
            is_gt = False
            p_cand = d.test_name if (".py" in d.test_name or d.test_name.startswith(f"{d.suite_file}::")) else f"{d.suite_file}::{d.test_name}"
            m_k, _, status = find_test_in_report_data(p_cand, gt_dict)
            if status in ("EXACT", "CANONICAL"):
                is_gt = True
            elif status != "AMBIGUOUS":
                m_k2, _, status2 = find_test_in_report_data(d.test_name, gt_dict)
                if status2 in ("EXACT", "CANONICAL"):
                    is_gt = True
            if is_gt:
                if d.action == "KEEP":
                    gt_retained_exec += 1
                elif d.action == "QUARANTINE_INSPECT":
                    gt_quar += 1
                else:
                    gt_disc += 1

        if gt_total > 0:
            gt_exec_rate = round(gt_retained_exec / gt_total, 4)
            gt_exec_rate_str = f"{gt_exec_rate * 100:.1f}% ({gt_retained_exec}/{gt_total})"
            gt_quar_rate = round(gt_quar / gt_total, 4)
            gt_quar_rate_str = f"{gt_quar_rate * 100:.1f}% ({gt_quar}/{gt_total})"
            legacy_gt_rate = round((gt_retained_exec + gt_quar) / gt_total, 4)
            legacy_gt_rate_str = f"{legacy_gt_rate * 100:.1f}% ({gt_retained_exec + gt_quar}/{gt_total})"
        else:
            gt_exec_rate_str = "Undefined (0 ground-truth bug detectors)"
            gt_quar_rate_str = "Undefined (0 ground-truth bug detectors)"
            legacy_gt_rate_str = "Undefined (0 ground-truth bug detectors)"

    return TriageSuiteReport(
        suite_file=test_path.name,
        total_tests=total_tests,
        tier_1_count=t1,
        tier_2_count=t2,
        tier_3_count=t3,
        tier_4_count=t4,
        executable_retention_count=t1,
        quarantined_count=t2,
        optional_count=t3,
        discarded_count=t4,
        executable_retention_rate=exec_ret_rate,
        executable_retention_rate_str=exec_ret_rate_str,
        quarantine_rate=quar_rate,
        quarantine_rate_str=quar_rate_str,
        retention_rate=legacy_ret_rate,
        retention_rate_str=legacy_ret_rate_str,
        gt_total_count=gt_total,
        gt_retained_executable_count=gt_retained_exec,
        gt_quarantined_count=gt_quar,
        gt_discarded_count=gt_disc,
        defect_retention_rate_executable=gt_exec_rate,
        defect_retention_rate_executable_str=gt_exec_rate_str,
        defect_quarantine_rate=gt_quar_rate,
        defect_quarantine_rate_str=gt_quar_rate_str,
        defect_retention_rate=legacy_gt_rate,
        defect_retention_rate_str=legacy_gt_rate_str,
        decisions=decisions,
    )
