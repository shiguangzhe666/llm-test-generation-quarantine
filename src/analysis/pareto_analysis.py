"""
Pareto Analysis, Clustered Standard Errors, and Non-Parametric Statistics.

Implements rigorous empirical software engineering metrics for TSE/EMSE:
1. Vargha-Delaney A12 effect size with standard magnitude interpretations.
2. Wilcoxon Signed-Rank Test (paired) with exact / normal approximation.
3. Cluster-Robust Standard Errors (Clustered SE) grouped by project/instance.
4. Wilson Score 95% Confidence Interval for proportions with zero-denominator handling.
5. Pareto Frontier identification across CI Determinism vs Defect Retention trade-off.
6. Baseline Strategy Evaluation (Keep-All vs Discard-All-Flaky vs Random vs Static vs Triage).
"""

import math
import random
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any


def compute_vargha_delaney_a12(sample_a: List[float], sample_b: List[float]) -> Tuple[float, str]:
    """
    Computes Vargha-Delaney A12 effect size for two independent samples.
    
    A12 = (R1 / (m * n)) - (m + 1) / (2 * n)
    where R1 is the sum of ranks of sample_a in the combined ranked array.
    
    Returns:
        (a12_value, magnitude)
        magnitude in ['negligible', 'small', 'medium', 'large']
    """
    m = len(sample_a)
    n = len(sample_b)
    if m == 0 or n == 0:
        return float('nan'), "undefined"
    
    # Tag and combine
    combined = [(val, 'A') for val in sample_a] + [(val, 'B') for val in sample_b]
    combined.sort(key=lambda x: x[0])
    
    # Assign average ranks for ties
    ranks = [0.0] * len(combined)
    i = 0
    N = len(combined)
    while i < N:
        j = i
        while j < N and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
        
    r1 = sum(ranks[idx] for idx in range(N) if combined[idx][1] == 'A')
    a12 = (r1 / (m * n)) - (m + 1.0) / (2.0 * n)
    
    # Magnitude interpretation according to Vargha & Delaney (2000)
    diff = abs(a12 - 0.5)
    if diff < 0.06:
        magnitude = "negligible"
    elif diff < 0.14:
        magnitude = "small"
    elif diff < 0.21:
        magnitude = "medium"
    else:
        magnitude = "large"
        
    return round(a12, 4), magnitude


class WilcoxonResult(tuple):
    """
    Tuple subclass (statistic, p_value) with audit attributes.
    Supports backward-compatible unpacking: w, p = compute_wilcoxon_signed_rank(a, b).
    """
    statistic: Optional[float]
    p_value: Optional[float]
    n_pairs: int
    n_non_zero: int
    n_zero: int

    def __new__(cls, statistic: Optional[float], p_value: Optional[float], n_pairs: int = 0, n_non_zero: int = 0, n_zero: int = 0):
        obj = super().__new__(cls, (statistic, p_value))
        obj.statistic = statistic
        obj.p_value = p_value
        obj.n_pairs = n_pairs
        obj.n_non_zero = n_non_zero
        obj.n_zero = n_zero
        return obj


def compute_paired_effect_size(sample_a: List[float], sample_b: List[float]) -> Tuple[Optional[float], str]:
    """
    Computes paired probability of superiority / paired A12 effect size:
    P(A > B) + 0.5 * P(A == B) calculated across matched pairs (sample_a[i], sample_b[i]).
    
    Returns:
        (paired_a12, magnitude)
    """
    if len(sample_a) != len(sample_b):
        raise ValueError("sample_a and sample_b must have the same length for paired effect size")
    N = len(sample_a)
    if N == 0:
        return None, "undefined"

    wins = sum(1 for a, b in zip(sample_a, sample_b) if a - b > 1e-9)
    ties = sum(1 for a, b in zip(sample_a, sample_b) if abs(a - b) <= 1e-9)
    paired_a12 = (wins + 0.5 * ties) / float(N)

    diff = abs(paired_a12 - 0.5)
    if diff < 0.06:
        magnitude = "negligible"
    elif diff < 0.14:
        magnitude = "small"
    elif diff < 0.21:
        magnitude = "medium"
    else:
        magnitude = "large"

    return round(paired_a12, 4), magnitude


def adjust_p_values_holm(p_values: List[Tuple[str, Optional[float]]]) -> Dict[str, Optional[float]]:
    """
    Applies Holm-Bonferroni step-down correction to multiple hypothesis test p-values.
    
    Args:
        p_values: list of (hypothesis_key, raw_p_value) pairs.
        
    Returns:
        Dict mapping hypothesis_key to adjusted_p_value.
    """
    valid = [(k, p) for k, p in p_values if p is not None and not math.isnan(p)]
    result: Dict[str, Optional[float]] = {k: None for k, p in p_values if p is None or math.isnan(p)}

    if not valid:
        return result

    # Sort valid by p-value ascending
    sorted_p = sorted(valid, key=lambda x: x[1])
    m = len(sorted_p)
    adj_values = []
    running_max = 0.0

    for i, (k, p) in enumerate(sorted_p):
        multiplier = m - i
        adj = min(1.0, p * multiplier)
        running_max = max(running_max, adj)
        adj_values.append((k, round(running_max, 6)))

    for k, adj in adj_values:
        result[k] = adj

    return result


def compute_wilcoxon_signed_rank(sample_a: List[float], sample_b: List[float]) -> WilcoxonResult:
    """
    Computes paired Wilcoxon Signed-Rank Test between sample_a and sample_b.
    
    Returns:
        WilcoxonResult(W_statistic, p_value, n_pairs, n_non_zero, n_zero)
        Unpacks as (w, p).
    """
    if len(sample_a) != len(sample_b):
        raise ValueError("sample_a and sample_b must have the same length for paired test")

    n_pairs = len(sample_a)
    if n_pairs == 0:
        return WilcoxonResult(None, None, n_pairs=0, n_non_zero=0, n_zero=0)

    diffs = [a - b for a, b in zip(sample_a, sample_b)]
    non_zero_diffs = [d for d in diffs if abs(d) > 1e-9]
    Nr = len(non_zero_diffs)
    n_zero = n_pairs - Nr

    if Nr == 0:
        return WilcoxonResult(0.0, 1.0, n_pairs=n_pairs, n_non_zero=0, n_zero=n_zero)

    # Sort absolute differences
    abs_diffs = [(abs(d), d > 0) for d in non_zero_diffs]
    abs_diffs.sort(key=lambda x: x[0])

    # Compute average ranks for ties
    ranks = [0.0] * Nr
    i = 0
    tie_corrections = 0.0
    while i < Nr:
        j = i
        while j < Nr and abs(abs_diffs[j][0] - abs_diffs[i][0]) < 1e-9:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        tie_size = j - i
        if tie_size > 1:
            tie_corrections += (tie_size ** 3 - tie_size) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j

    w_pos = sum(ranks[idx] for idx in range(Nr) if abs_diffs[idx][1])
    w_neg = sum(ranks[idx] for idx in range(Nr) if not abs_diffs[idx][1])
    w = min(w_pos, w_neg)

    # Normal approximation with continuity correction
    mean_w = Nr * (Nr + 1.0) / 4.0
    var_w = (Nr * (Nr + 1.0) * (2.0 * Nr + 1.0) - tie_corrections) / 24.0

    if var_w <= 0.0:
        return WilcoxonResult(w, 1.0, n_pairs=n_pairs, n_non_zero=Nr, n_zero=n_zero)

    std_w = math.sqrt(var_w)
    # Continuity correction
    z = (abs(w - mean_w) - 0.5) / std_w
    # Two-tailed p-value via complementary error function
    p_value = math.erfc(z / math.sqrt(2.0))
    p_value = max(0.0, min(1.0, p_value))

    return WilcoxonResult(round(w, 4), round(p_value, 6), n_pairs=n_pairs, n_non_zero=Nr, n_zero=n_zero)


def compute_clustered_standard_error(cluster_ids: List[str], values: List[float]) -> Tuple[float, float]:
    """
    Computes cluster-robust standard error for sample mean.
    Accounts for intra-cluster correlation (e.g. multiple tests generated on same project/instance).
    
    Returns:
        (sample_mean, clustered_se)
    """
    if len(cluster_ids) != len(values):
        raise ValueError(f"Length mismatch: cluster_ids ({len(cluster_ids)}) vs values ({len(values)})")
    
    # Pair-filter to strictly prevent index misalignment when filtering missing values
    valid_pairs = [(c, v) for c, v in zip(cluster_ids, values) if v is not None]
    if not valid_pairs:
        return float('nan'), float('nan')
    if len(valid_pairs) == 1:
        return valid_pairs[0][1], 0.0

    cluster_ids = [c for c, v in valid_pairs]
    values = [v for c, v in valid_pairs]
    N = len(values)

    # Group by cluster
    clusters: Dict[str, List[float]] = {}
    for cid, val in zip(cluster_ids, values):
        clusters.setdefault(cid, []).append(val)
        
    G = len(clusters)
    if G <= 1:
        # Fallback to standard SE if only 1 cluster
        mean_val = sum(values) / N
        var = sum((v - mean_val) ** 2 for v in values) / (N - 1)
        return round(mean_val, 4), round(math.sqrt(var / N), 4)
        
    mean_val = sum(values) / N
    
    # Sum of residuals per cluster
    u_g_sum_sq = 0.0
    for cid, cvals in clusters.items():
        u_g = sum(v - mean_val for v in cvals)
        u_g_sum_sq += u_g ** 2
        
    # Finite-sample correction: [G / (G - 1)] * [(N - 1) / N]
    finite_corr = (G / (G - 1.0)) * ((N - 1.0) / N)
    var_cluster = (finite_corr / (N ** 2)) * u_g_sum_sq
    clustered_se = math.sqrt(max(0.0, var_cluster))
    
    return round(mean_val, 4), round(clustered_se, 4)


def compute_wilson_confidence_interval(k: int, n: int, confidence: float = 0.95) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Computes Wilson score interval for binomial proportions.
    
    Returns:
        (p_hat, ci_lower, ci_upper) or (None, None, None) if n == 0.
    """
    if n <= 0:
        return None, None, None
        
    p_hat = k / n
    # z for 95% is 1.95996
    z = 1.95996 if abs(confidence - 0.95) < 0.01 else 2.57583
    
    denominator = 1.0 + (z ** 2) / n
    center = (p_hat + (z ** 2) / (2.0 * n)) / denominator
    margin = (z / denominator) * math.sqrt((p_hat * (1.0 - p_hat) / n) + ((z ** 2) / (4.0 * (n ** 2))))
    
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    
    return round(p_hat, 4), round(lower, 4), round(upper, 4)


def compute_pareto_frontier(points: List[Dict[str, Any]], minimize_x: str, maximize_y: str) -> List[Dict[str, Any]]:
    """
    Identifies the Pareto frontier (non-dominated points).
    
    We wish to MINIMIZE variable `minimize_x` (e.g. Flakiness / CI failure rate)
    and MAXIMIZE variable `maximize_y` (e.g. Defect Retention Rate / Mutation Score).
    
    Point A dominates Point B if:
      A[minimize_x] <= B[minimize_x] and A[maximize_y] >= B[maximize_y]
      and at least one inequality is strict.
    """
    pareto: List[Dict[str, Any]] = []
    
    for i, p1 in enumerate(points):
        dominated = False
        for j, p2 in enumerate(points):
            if i == j:
                continue
            x1, y1 = p1[minimize_x], p1[maximize_y]
            x2, y2 = p2[minimize_x], p2[maximize_y]
            
            # If p2 dominates p1:
            if (x2 <= x1 and y2 >= y1) and (x2 < x1 or y2 > y1):
                dominated = True
                break
        if not dominated:
            pareto.append(p1)
            
    # Sort Pareto points by minimize_x ascending
    pareto.sort(key=lambda p: (p[minimize_x], -p[maximize_y]))
    return pareto


@dataclass
class StrategyMetrics:
    strategy_name: str
    total_tests: int
    executable_tests: int
    executable_retention_rate: Optional[float]
    quarantined_tests: int
    quarantine_rate: Optional[float]
    ci_flakiness_rate: float
    ci_deterministic_rate: float
    real_bugs_retained: int
    real_bugs_total: int
    real_bug_retention_rate: Optional[float]
    defect_tests_retained: int  # Combined / overall defect tests retained (mainline + quarantine)
    defect_tests_total: int
    defect_test_retention_rate: Optional[float]
    avg_mutation_score: Optional[float]
    # Transparent breakdown metrics distinguishing mainline CI vs quarantine pool
    mainline_defect_tests_retained: int = 0
    quarantine_defect_tests_retained: int = 0
    mainline_defect_test_retention_rate: Optional[float] = None
    quarantine_defect_test_retention_rate: Optional[float] = None
    mainline_real_bugs_retained: int = 0
    quarantine_real_bugs_retained: int = 0
    mainline_real_bug_retention_rate: Optional[float] = None
    quarantine_real_bug_retention_rate: Optional[float] = None
    system_defect_test_retention_rate: Optional[float] = None
    system_real_bug_retention_rate: Optional[float] = None


def evaluate_strategies_on_suite(
    test_records: List[Dict[str, Any]],
    real_bugs_total: int,
    triage_decisions: List[Dict[str, Any]],
    random_seed: int = 42
) -> Dict[str, StrategyMetrics]:
    """
    Evaluates and compares 5 baseline and proposed triage strategies on a single test suite:
    1. Keep-All: Baseline retaining all tests.
    2. Discard-All-Flaky: Industrial baseline (TestGen-LLM) discarding all flaky tests.
    3. Random-Filtering: Budget-matched random filtering matching Tier 1 count.
    4. Static-Only: Filtering using only static AST fragility without dynamic flakiness.
    5. Risk-Aware Triage: Our 4-tier risk-aware framework.
    """
    N = len(test_records)
    if N == 0:
        return {}
        
    total_defect_tests = sum(1 for t in test_records if t.get("is_bug_detecting", False))
    
    # 1. Strategy: Keep-All
    keep_all_exec = test_records
    keep_flaky = sum(1 for t in keep_all_exec if t.get("flakiness_rate", 0.0) > 0.0)
    keep_ci_flaky = keep_flaky / N if N > 0 else 0.0
    keep_bd = sum(1 for t in keep_all_exec if t.get("is_bug_detecting", False))
    keep_bugs = real_bugs_total if keep_bd > 0 else 0
    keep_ms = [t.get("mutation_score", 0.0) for t in keep_all_exec if "mutation_score" in t]
    avg_keep_ms = sum(keep_ms) / len(keep_ms) if keep_ms else None
    
    res_keep_all = StrategyMetrics(
        strategy_name="Keep-All",
        total_tests=N,
        executable_tests=N,
        executable_retention_rate=1.0,
        quarantined_tests=0,
        quarantine_rate=0.0,
        ci_flakiness_rate=round(keep_ci_flaky, 4),
        ci_deterministic_rate=round(1.0 - keep_ci_flaky, 4),
        real_bugs_retained=keep_bugs,
        real_bugs_total=real_bugs_total,
        real_bug_retention_rate=1.0 if real_bugs_total > 0 else None,
        defect_tests_retained=keep_bd,
        defect_tests_total=total_defect_tests,
        defect_test_retention_rate=1.0 if total_defect_tests > 0 else None,
        avg_mutation_score=round(avg_keep_ms, 4) if avg_keep_ms is not None else None,
        mainline_defect_tests_retained=keep_bd,
        quarantine_defect_tests_retained=0,
        mainline_defect_test_retention_rate=1.0 if total_defect_tests > 0 else None,
        quarantine_defect_test_retention_rate=0.0 if total_defect_tests > 0 else None,
        mainline_real_bugs_retained=keep_bugs,
        quarantine_real_bugs_retained=0,
        mainline_real_bug_retention_rate=1.0 if real_bugs_total > 0 else None,
        quarantine_real_bug_retention_rate=0.0 if real_bugs_total > 0 else None,
        system_defect_test_retention_rate=1.0 if total_defect_tests > 0 else None,
        system_real_bug_retention_rate=1.0 if real_bugs_total > 0 else None,
    )
    
    # 2. Strategy: Discard-All-Flaky (Industrial standard: drop any flakiness > 0)
    discard_exec = [t for t in test_records if t.get("flakiness_rate", 0.0) <= 0.0]
    disc_n = len(discard_exec)
    disc_bd = sum(1 for t in discard_exec if t.get("is_bug_detecting", False))
    disc_bugs = real_bugs_total if (disc_bd > 0 and real_bugs_total > 0) else 0
    disc_ms = [t.get("mutation_score", 0.0) for t in discard_exec if "mutation_score" in t]
    avg_disc_ms = sum(disc_ms) / len(disc_ms) if disc_ms else None
    
    res_discard = StrategyMetrics(
        strategy_name="Discard-All-Flaky",
        total_tests=N,
        executable_tests=disc_n,
        executable_retention_rate=round(disc_n / N, 4) if N > 0 else None,
        quarantined_tests=0,
        quarantine_rate=0.0,
        ci_flakiness_rate=0.0,
        ci_deterministic_rate=1.0,
        real_bugs_retained=disc_bugs,
        real_bugs_total=real_bugs_total,
        real_bug_retention_rate=round(disc_bugs / real_bugs_total, 4) if real_bugs_total > 0 else None,
        defect_tests_retained=disc_bd,
        defect_tests_total=total_defect_tests,
        defect_test_retention_rate=round(disc_bd / total_defect_tests, 4) if total_defect_tests > 0 else None,
        avg_mutation_score=round(avg_disc_ms, 4) if avg_disc_ms is not None else None,
        mainline_defect_tests_retained=disc_bd,
        quarantine_defect_tests_retained=0,
        mainline_defect_test_retention_rate=round(disc_bd / total_defect_tests, 4) if total_defect_tests > 0 else None,
        quarantine_defect_test_retention_rate=0.0 if total_defect_tests > 0 else None,
        mainline_real_bugs_retained=disc_bugs,
        quarantine_real_bugs_retained=0,
        mainline_real_bug_retention_rate=round(disc_bugs / real_bugs_total, 4) if real_bugs_total > 0 else None,
        quarantine_real_bug_retention_rate=0.0 if real_bugs_total > 0 else None,
        system_defect_test_retention_rate=round(disc_bd / total_defect_tests, 4) if total_defect_tests > 0 else None,
        system_real_bug_retention_rate=round(disc_bugs / real_bugs_total, 4) if real_bugs_total > 0 else None,
    )
    
    # 5. Strategy: Risk-Aware Triage (Proposed)
    # Tier 1 = KEEP (executable pool)
    # Tier 2 = QUARANTINE_INSPECT (dual purpose / high value quarantine)
    # Tier 3 = FRAGILE_KEEP (monitored executable pool)
    # Tier 4 = DISCARD
    triage_map = {t["test_name"]: t for t in triage_decisions}
    
    tier1_tests = []
    tier2_tests = []
    tier3_tests = []
    tier4_tests = []
    
    for tr in test_records:
        tname = tr["test_name"]
        d_info = triage_map.get(tname, {})
        action = d_info.get("action", "KEEP")
        cat = d_info.get("category", "")
        
        if cat:
            if cat == "TIER_1_SAFE_KEEP":
                tier1_tests.append(tr)
            elif cat == "TIER_2_DUAL_PURPOSE":
                tier2_tests.append(tr)
            elif cat == "TIER_3_SAFE_LOW":
                tier3_tests.append(tr)
            else:
                tier4_tests.append(tr)
        else:
            if action == "KEEP":
                tier1_tests.append(tr)
            elif action in ("QUARANTINE_INSPECT", "QUARANTINE_REPAIR"):
                tier2_tests.append(tr)
            elif action in ("OPTIONAL", "MONITOR_RUN"):
                tier3_tests.append(tr)
            else:
                tier4_tests.append(tr)
            
    triage_exec = tier1_tests + tier3_tests
    n_exec = len(triage_exec)
    n_quarantine = len(tier2_tests)
    
    # In our framework, executable CI tests have 0 flakiness (due to base flakiness penalty)
    triage_ci_flaky = sum(1 for t in triage_exec if t.get("flakiness_rate", 0.0) > 0.0)
    ci_flaky_rate = triage_ci_flaky / n_exec if n_exec > 0 else 0.0
    
    # Transparent separation of mainline defect detection vs quarantine defect detection
    triage_mainline_bd = sum(1 for t in triage_exec if t.get("is_bug_detecting", False))
    triage_quar_bd = sum(1 for t in tier2_tests if t.get("is_bug_detecting", False))
    retained_all = triage_exec + tier2_tests
    triage_bd = sum(1 for t in retained_all if t.get("is_bug_detecting", False))
    triage_bugs = real_bugs_total if (triage_bd > 0 and real_bugs_total > 0) else 0
    triage_mainline_bugs = real_bugs_total if (triage_mainline_bd > 0 and real_bugs_total > 0) else 0
    triage_quar_bugs = real_bugs_total if (triage_quar_bd > 0 and real_bugs_total > 0) else 0
    triage_ms = [t.get("mutation_score", 0.0) for t in retained_all if "mutation_score" in t]
    avg_triage_ms = sum(triage_ms) / len(triage_ms) if triage_ms else None
    
    res_triage = StrategyMetrics(
        strategy_name="Risk-Aware-Triage",
        total_tests=N,
        executable_tests=n_exec,
        executable_retention_rate=round(n_exec / N, 4) if N > 0 else None,
        quarantined_tests=n_quarantine,
        quarantine_rate=round(n_quarantine / N, 4) if N > 0 else None,
        ci_flakiness_rate=round(ci_flaky_rate, 4),
        ci_deterministic_rate=round(1.0 - ci_flaky_rate, 4),
        real_bugs_retained=triage_bugs,
        real_bugs_total=real_bugs_total,
        real_bug_retention_rate=round(triage_bugs / real_bugs_total, 4) if real_bugs_total > 0 else None,
        defect_tests_retained=triage_bd,
        defect_tests_total=total_defect_tests,
        defect_test_retention_rate=round(triage_bd / total_defect_tests, 4) if total_defect_tests > 0 else None,
        avg_mutation_score=round(avg_triage_ms, 4) if avg_triage_ms is not None else None,
        mainline_defect_tests_retained=triage_mainline_bd,
        quarantine_defect_tests_retained=triage_quar_bd,
        mainline_defect_test_retention_rate=round(triage_mainline_bd / total_defect_tests, 4) if total_defect_tests > 0 else None,
        quarantine_defect_test_retention_rate=round(triage_quar_bd / total_defect_tests, 4) if total_defect_tests > 0 else None,
        mainline_real_bugs_retained=triage_mainline_bugs,
        quarantine_real_bugs_retained=triage_quar_bugs,
        mainline_real_bug_retention_rate=round(triage_mainline_bugs / real_bugs_total, 4) if real_bugs_total > 0 else None,
        quarantine_real_bug_retention_rate=round(triage_quar_bugs / real_bugs_total, 4) if real_bugs_total > 0 else None,
        system_defect_test_retention_rate=round(triage_bd / total_defect_tests, 4) if total_defect_tests > 0 else None,
        system_real_bug_retention_rate=round(triage_bugs / real_bugs_total, 4) if real_bugs_total > 0 else None,
    )
    
    # 3. Strategy: Random-Filtering (Budget-matched to Tier 1 size)
    rng = random.Random(random_seed)
    target_k = max(1, min(N, n_exec))
    sampled_indices = sorted(rng.sample(range(N), target_k))
    random_exec = [test_records[i] for i in sampled_indices]
    rand_flaky = sum(1 for t in random_exec if t.get("flakiness_rate", 0.0) > 0.0)
    rand_ci_flaky = rand_flaky / target_k if target_k > 0 else 0.0
    rand_bd = sum(1 for t in random_exec if t.get("is_bug_detecting", False))
    rand_bugs = real_bugs_total if (rand_bd > 0 and real_bugs_total > 0) else 0
    rand_ms = [t.get("mutation_score", 0.0) for t in random_exec if "mutation_score" in t]
    avg_rand_ms = sum(rand_ms) / len(rand_ms) if rand_ms else None
    
    res_random = StrategyMetrics(
        strategy_name="Random-Filtering",
        total_tests=N,
        executable_tests=target_k,
        executable_retention_rate=round(target_k / N, 4) if N > 0 else None,
        quarantined_tests=0,
        quarantine_rate=0.0,
        ci_flakiness_rate=round(rand_ci_flaky, 4),
        ci_deterministic_rate=round(1.0 - rand_ci_flaky, 4),
        real_bugs_retained=rand_bugs,
        real_bugs_total=real_bugs_total,
        real_bug_retention_rate=round(rand_bugs / real_bugs_total, 4) if real_bugs_total > 0 else None,
        defect_tests_retained=rand_bd,
        defect_tests_total=total_defect_tests,
        defect_test_retention_rate=round(rand_bd / total_defect_tests, 4) if total_defect_tests > 0 else None,
        avg_mutation_score=round(avg_rand_ms, 4) if avg_rand_ms is not None else None,
        mainline_defect_tests_retained=rand_bd,
        quarantine_defect_tests_retained=0,
        mainline_defect_test_retention_rate=round(rand_bd / total_defect_tests, 4) if total_defect_tests > 0 else None,
        quarantine_defect_test_retention_rate=0.0 if total_defect_tests > 0 else None,
        mainline_real_bugs_retained=rand_bugs,
        quarantine_real_bugs_retained=0,
        mainline_real_bug_retention_rate=round(rand_bugs / real_bugs_total, 4) if real_bugs_total > 0 else None,
        quarantine_real_bug_retention_rate=0.0 if real_bugs_total > 0 else None,
        system_defect_test_retention_rate=round(rand_bd / total_defect_tests, 4) if total_defect_tests > 0 else None,
        system_real_bug_retention_rate=round(rand_bugs / real_bugs_total, 4) if real_bugs_total > 0 else None,
    )
    
    # 4. Strategy: Static-Only (Filtering using static AST fragility <= 0.3)
    static_exec = [t for t in test_records if t.get("fragility_score", 0.0) <= 0.3]
    static_n = len(static_exec)
    stat_flaky = sum(1 for t in static_exec if t.get("flakiness_rate", 0.0) > 0.0)
    stat_ci_flaky = stat_flaky / static_n if static_n > 0 else 0.0
    stat_bd = sum(1 for t in static_exec if t.get("is_bug_detecting", False))
    stat_bugs = real_bugs_total if (stat_bd > 0 and real_bugs_total > 0) else 0
    stat_ms = [t.get("mutation_score", 0.0) for t in static_exec if "mutation_score" in t]
    avg_stat_ms = sum(stat_ms) / len(stat_ms) if stat_ms else None
    
    res_static = StrategyMetrics(
        strategy_name="Static-Only",
        total_tests=N,
        executable_tests=static_n,
        executable_retention_rate=round(static_n / N, 4) if N > 0 else None,
        quarantined_tests=0,
        quarantine_rate=0.0,
        ci_flakiness_rate=round(stat_ci_flaky, 4),
        ci_deterministic_rate=round(1.0 - stat_ci_flaky, 4),
        real_bugs_retained=stat_bugs,
        real_bugs_total=real_bugs_total,
        real_bug_retention_rate=round(stat_bugs / real_bugs_total, 4) if real_bugs_total > 0 else None,
        defect_tests_retained=stat_bd,
        defect_tests_total=total_defect_tests,
        defect_test_retention_rate=round(stat_bd / total_defect_tests, 4) if total_defect_tests > 0 else None,
        avg_mutation_score=round(avg_stat_ms, 4) if avg_stat_ms is not None else None,
        mainline_defect_tests_retained=stat_bd,
        quarantine_defect_tests_retained=0,
        mainline_defect_test_retention_rate=round(stat_bd / total_defect_tests, 4) if total_defect_tests > 0 else None,
        quarantine_defect_test_retention_rate=0.0 if total_defect_tests > 0 else None,
        mainline_real_bugs_retained=stat_bugs,
        quarantine_real_bugs_retained=0,
        mainline_real_bug_retention_rate=round(stat_bugs / real_bugs_total, 4) if real_bugs_total > 0 else None,
        quarantine_real_bug_retention_rate=0.0 if real_bugs_total > 0 else None,
        system_defect_test_retention_rate=round(stat_bd / total_defect_tests, 4) if total_defect_tests > 0 else None,
        system_real_bug_retention_rate=round(stat_bugs / real_bugs_total, 4) if real_bugs_total > 0 else None,
    )
    
    return {
        "Keep-All": res_keep_all,
        "Discard-All-Flaky": res_discard,
        "Random-Filtering": res_random,
        "Static-Only": res_static,
        "Risk-Aware-Triage": res_triage,
    }


def generate_latex_table(study_metrics: Dict[str, Any]) -> str:
    """
    Generates a publication-ready LaTeX table for EMSE/TSE comparison.
    """
    latex = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Empirical Comparison of Test Selection Strategies Across SWE-bench Verified Instances}",
        r"\label{tab:strategy_comparison}",
        r"\begin{tabular}{lcccccc}",
        r"\toprule",
        r"\textbf{Strategy} & \textbf{Exec. Ret. (\%)} & \textbf{Quarantine (\%)} & \textbf{CI Determ. (\%)} & \textbf{Bug Ret. (\%)} & \textbf{Defect Tests Ret. (\%)} & \textbf{Mut. Score (\%)} \\",
        r"\midrule"
    ]
    
    for strat, m in study_metrics.items():
        exec_ret = f"{m['exec_retention'] * 100:.1f}" if m.get('exec_retention') is not None else "N/A"
        quar = f"{m['quarantine_rate'] * 100:.1f}" if m.get('quarantine_rate') is not None else "0.0"
        determ = f"{m['ci_determinism'] * 100:.1f}" if m.get('ci_determinism') is not None else "N/A"
        bug_ret = f"{m['bug_retention'] * 100:.1f}" if m.get('bug_retention') is not None else "N/A"
        dt_ret = f"{m['defect_tests_retention'] * 100:.1f}" if m.get('defect_tests_retention') is not None else "N/A"
        mut = f"{m['mutation_score'] * 100:.1f}" if m.get('mutation_score') is not None else "N/A"
        
        row = f"{strat} & {exec_ret} & {quar} & {determ} & {bug_ret} & {dt_ret} & {mut} \\\\"
        latex.append(row)
        
    latex.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table*}"
    ])
    return "\n".join(latex)
