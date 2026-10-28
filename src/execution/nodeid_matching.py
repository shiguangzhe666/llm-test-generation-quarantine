"""
Unified NodeID Matching and Canonicalization Module.

Provides robust, transparent NodeID canonicalization and matching between
planned test targets and pytest runtime observation reports.

Guarantees:
1. Path normalization across OS platforms (POSIX style, resolving slashes/relative paths).
2. Strict hierarchical matching (file -> class -> function -> parameterization).
3. Explicit prohibition of silent, cross-file/cross-class short-name fallbacks (no blind split("::")[-1]).
4. Categorization of all test IDs: matched, missing, unknown, duplicate, ambiguous.
5. Parameterized tests aggregated only when strictly belonging to the same canonical test function node.
"""

from dataclasses import dataclass, field
import os
from pathlib import Path, PurePosixPath
import re
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class NodeIDMatchResult:
    """Detailed audit record of matching planned nodeids against observed report nodeids."""
    planned_nodeids: List[str] = field(default_factory=list)
    observed_nodeids: List[str] = field(default_factory=list)
    matched: Dict[str, str] = field(default_factory=dict)       # planned_nid -> observed_nid
    reverse_matched: Dict[str, str] = field(default_factory=dict) # observed_nid -> planned_nid
    missing: List[str] = field(default_factory=list)             # planned but unobserved
    unknown: List[str] = field(default_factory=list)             # observed in report but not planned
    duplicates: List[str] = field(default_factory=list)          # observed more than once
    ambiguous: List[str] = field(default_factory=list)           # conflicts/multiple potential matches

    @property
    def is_complete(self) -> bool:
        """True if every planned test was uniquely matched with zero missing or ambiguous."""
        return len(self.missing) == 0 and len(self.ambiguous) == 0


def normalize_path_part(path_str: str) -> str:
    """Normalize file path component to clean forward-slash representation."""
    clean = path_str.replace("\\", "/").strip()
    # Remove leading ./
    if clean.startswith("./"):
        clean = clean[2:]
    # Normalize path segments (e.g., foo/bar/../baz -> foo/baz)
    try:
        norm = os.path.normpath(clean).replace("\\", "/")
        if norm == ".":
            norm = clean
        return norm
    except Exception:
        return clean


def split_nodeid(nodeid: str) -> Tuple[str, List[str]]:
    """
    Split a pytest nodeid into (normalized_file_path, [scope1, scope2, ...]).
    
    Example:
        'tests\\test_api.py::TestClass::test_get[param]' ->
        ('tests/test_api.py', ['TestClass', 'test_get[param]'])
    """
    if "::" not in nodeid:
        return normalize_path_part(nodeid), []
    parts = nodeid.split("::")
    file_part = normalize_path_part(parts[0])
    code_parts = [p.strip() for p in parts[1:] if p.strip()]
    return file_part, code_parts


def canonical_nodeid(nodeid: str) -> str:
    """
    Return the canonical, normalized string representation of a nodeid.
    
    Guarantees consistent forward slashes in path and clean '::' separators.
    """
    file_part, code_parts = split_nodeid(nodeid)
    if not code_parts:
        return file_part
    return f"{file_part}::{'::'.join(code_parts)}"


def get_base_test_name(func_or_scope: str) -> str:
    """Strip parameter brackets to get the bare function or class name."""
    idx = func_or_scope.find("[")
    if idx != -1:
        return func_or_scope[:idx]
    return func_or_scope


def match_nodeids(
    planned: List[str],
    observed: List[str],
) -> NodeIDMatchResult:
    """
    Match planned test nodeids against observed test nodeids from report.
    
    Strict Matching Policy:
    1. Exact Match: canonical(p) == canonical(o).
    2. Suffix File Match: The file parts match on relative suffix (e.g. 'tests/test_a.py' matches
       'repo/tests/test_a.py' or vice versa) AND all code parts match identically.
    3. Parameterized Sub-node: If planned nodeid matches the base of an observed parameterized test
       or vice versa, strictly within the EXACT SAME file and class hierarchy.
    4. NO Cross-file / Cross-class Fallback: Blind split("::")[-1] matching across different files
       or scopes is strictly rejected.
    """
    result = NodeIDMatchResult(
        planned_nodeids=list(planned),
        observed_nodeids=list(observed),
    )

    # Check observed duplicates
    seen_obs: Set[str] = set()
    for o in observed:
        o_can = canonical_nodeid(o)
        if o_can in seen_obs:
            result.duplicates.append(o)
        seen_obs.add(o_can)

    planned_canonical = [(p, canonical_nodeid(p), split_nodeid(p)) for p in planned]
    observed_canonical = [(o, canonical_nodeid(o), split_nodeid(o)) for o in observed]

    matched_p: Set[str] = set()
    matched_o: Set[str] = set()

    # Pass 1: Exact canonical match
    obs_by_canonical: Dict[str, List[Tuple[str, str, Tuple[str, List[str]]]]] = {}
    for o_tuple in observed_canonical:
        obs_by_canonical.setdefault(o_tuple[1], []).append(o_tuple)

    for p, p_can, p_parts in planned_canonical:
        if p_can in obs_by_canonical:
            candidates = obs_by_canonical[p_can]
            if len(candidates) == 1:
                o_orig = candidates[0][0]
                result.matched[p] = o_orig
                result.reverse_matched[o_orig] = p
                matched_p.add(p)
                matched_o.add(o_orig)

    # Pass 2: Path suffix & relative path match (code parts must be identical)
    for p, p_can, (p_file, p_scopes) in planned_canonical:
        if p in matched_p:
            continue
        candidates = []
        for o, o_can, (o_file, o_scopes) in observed_canonical:
            if o in matched_o:
                continue
            if p_scopes == o_scopes and len(p_scopes) > 0:
                # Compare file paths: one ends with the other as a proper path component
                if (p_file == o_file or
                    p_file.endswith(f"/{o_file}") or
                    o_file.endswith(f"/{p_file}")):
                    candidates.append(o)

        if len(candidates) == 1:
            o_match = candidates[0]
            result.matched[p] = o_match
            result.reverse_matched[o_match] = p
            matched_p.add(p)
            matched_o.add(o_match)
        elif len(candidates) > 1:
            result.ambiguous.append(p)

    # Pass 3: Parameterized variant matching (same file + class scope + same base function)
    for p, p_can, (p_file, p_scopes) in planned_canonical:
        if p in matched_p or p in result.ambiguous:
            continue
        candidates = []
        p_base_scopes = [get_base_test_name(s) for s in p_scopes]
        for o, o_can, (o_file, o_scopes) in observed_canonical:
            if o in matched_o:
                continue
            o_base_scopes = [get_base_test_name(s) for s in o_scopes]
            # Must strictly belong to same file and base scopes
            file_match = (p_file == o_file or p_file.endswith(f"/{o_file}") or o_file.endswith(f"/{p_file}"))
            if file_match and p_base_scopes == o_base_scopes and len(p_scopes) > 0:
                candidates.append(o)

        if len(candidates) == 1:
            o_match = candidates[0]
            result.matched[p] = o_match
            result.reverse_matched[o_match] = p
            matched_p.add(p)
            matched_o.add(o_match)
        elif len(candidates) > 1:
            # If multiple parameterized runs belong to the same planned test, mark as ambiguous
            # rather than silently picking one.
            result.ambiguous.append(p)

    # Missing & Unknown classification
    for p in planned:
        if p not in matched_p and p not in result.ambiguous:
            result.missing.append(p)

    for o in observed:
        if o not in matched_o:
            result.unknown.append(o)

    return result


def find_test_in_report_data(
    planned_nid: str,
    tests_map: Dict[str, Any],
) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
    """
    Locate a planned test in tests_map safely using canonical rules.
    
    Returns:
        (matched_observed_key, test_data_dict, match_status)
        where match_status in ['EXACT', 'CANONICAL', 'AMBIGUOUS', 'NOT_FOUND']
    """
    if planned_nid in tests_map:
        return planned_nid, tests_map[planned_nid], "EXACT"

    # Match across canonicalized keys
    p_can = canonical_nodeid(planned_nid)
    p_file, p_scopes = split_nodeid(planned_nid)

    canonical_matches = []
    suffix_matches = []

    for k, v in tests_map.items():
        k_can = canonical_nodeid(k)
        if k_can == p_can:
            canonical_matches.append((k, v))
            continue
        k_file, k_scopes = split_nodeid(k)
        if k_scopes == p_scopes and len(p_scopes) > 0:
            if (p_file == k_file or
                p_file.endswith(f"/{k_file}") or
                k_file.endswith(f"/{p_file}")):
                suffix_matches.append((k, v))

    if len(canonical_matches) == 1:
        k, v = canonical_matches[0]
        return k, v, "CANONICAL"
    elif len(canonical_matches) > 1:
        return None, None, "AMBIGUOUS"

    if len(suffix_matches) == 1:
        k, v = suffix_matches[0]
        return k, v, "CANONICAL"
    elif len(suffix_matches) > 1:
        return None, None, "AMBIGUOUS"

    return None, None, "NOT_FOUND"
