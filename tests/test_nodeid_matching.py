"""
Unit tests for src/execution/nodeid_matching.py.
Verifies canonicalization, strict matching, parameterized matching, and cross-scope rejection.
"""

import pytest
from src.execution.nodeid_matching import (
    canonical_nodeid,
    split_nodeid,
    get_base_test_name,
    match_nodeids,
    find_test_in_report_data,
)


def test_canonical_nodeid_and_split():
    # Windows-style backslashes and redundant separators
    raw = r"tests\unit\test_core.py::TestClass::test_method[param-1]"
    norm = canonical_nodeid(raw)
    assert norm == "tests/unit/test_core.py::TestClass::test_method[param-1]"

    f_part, scopes = split_nodeid(raw)
    assert f_part == "tests/unit/test_core.py"
    assert scopes == ["TestClass", "test_method[param-1]"]

    # File only
    f_part, scopes = split_nodeid(r"src\test_standalone.py")
    assert f_part == "src/test_standalone.py"
    assert scopes == []


def test_get_base_test_name():
    assert get_base_test_name("test_func[a-b-c]") == "test_func"
    assert get_base_test_name("test_func") == "test_func"
    assert get_base_test_name("TestClass::test_func[123]") == "TestClass::test_func"


def test_match_nodeids_exact_and_suffix():
    planned = [
        "tests/test_a.py::test_one",
        "tests/test_b.py::TestB::test_two",
    ]
    observed = [
        "tests/test_a.py::test_one",
        "repo/tests/test_b.py::TestB::test_two",
    ]
    res = match_nodeids(planned, observed)
    assert res.is_complete
    assert res.matched["tests/test_a.py::test_one"] == "tests/test_a.py::test_one"
    assert res.matched["tests/test_b.py::TestB::test_two"] == "repo/tests/test_b.py::TestB::test_two"
    assert len(res.missing) == 0
    assert len(res.unknown) == 0


def test_match_nodeids_parameterized():
    planned = [
        "tests/test_p.py::test_calc",
    ]
    observed = [
        "tests/test_p.py::test_calc[case1]",
    ]
    res = match_nodeids(planned, observed)
    assert res.is_complete
    assert res.matched["tests/test_p.py::test_calc"] == "tests/test_p.py::test_calc[case1]"


def test_match_nodeids_ambiguous_and_no_cross_scope_fallback():
    # If planned maps to multiple observed parameterized runs, it must be flagged ambiguous
    planned = [
        "tests/test_p.py::test_calc",
        "tests/test_other.py::test_calc",
    ]
    observed = [
        "tests/test_p.py::test_calc[case1]",
        "tests/test_p.py::test_calc[case2]",
        "tests/test_unrelated.py::test_calc",
    ]
    res = match_nodeids(planned, observed)
    assert not res.is_complete
    # test_p.py has 2 candidates -> ambiguous
    assert "tests/test_p.py::test_calc" in res.ambiguous
    # test_other.py must NOT match test_unrelated.py -> missing
    assert "tests/test_other.py::test_calc" in res.missing
    assert "tests/test_unrelated.py::test_calc" in res.unknown


def test_find_test_in_report_data():
    data = {
        "tests/test_demo.py::test_foo": {"status": "passed"},
        "tests/test_demo.py::test_bar[p1]": {"status": "failed"},
        "sub/test_demo.py::test_baz": {"status": "passed"},
    }

    # EXACT
    k, v, s = find_test_in_report_data("tests/test_demo.py::test_foo", data)
    assert s == "EXACT"
    assert k == "tests/test_demo.py::test_foo"

    # CANONICAL / SUFFIX
    k, v, s = find_test_in_report_data(r"tests\test_demo.py::test_foo", data)
    assert s in ("EXACT", "CANONICAL")
    assert k == "tests/test_demo.py::test_foo"

    k, v, s = find_test_in_report_data("test_demo.py::test_baz", data)
    assert s == "CANONICAL"
    assert k == "sub/test_demo.py::test_baz"

    # NOT FOUND (cross-module rejection)
    k, v, s = find_test_in_report_data("other_file.py::test_foo", data)
    assert s == "NOT_FOUND"
    assert k is None
