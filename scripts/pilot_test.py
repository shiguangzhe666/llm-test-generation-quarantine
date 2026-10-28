"""
End-to-end pilot test: Generate LLM tests, run repeatedly, check flakiness.

This pilot uses a simple local Python project (no Docker needed)
to validate our complete pipeline before scaling to SWE-bench.

Steps:
1. Create a small sample Python module with a known bug
2. Generate tests using a free LLM (simulated for now with template-based)
3. Run tests repeatedly with our executor
4. Analyze flakiness
5. Test on buggy vs fixed version
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================
# Step 1: Create a sample project with a known bug
# ============================================================

SAMPLE_MODULE_FIXED = '''
"""Sample module: URL parser with edge case handling."""

def parse_url_params(url):
    """Parse URL query parameters into a dictionary.
    
    Args:
        url: A URL string potentially containing query parameters.
        
    Returns:
        Dictionary of parameter name -> value mappings.
    """
    if not url or not isinstance(url, str):
        return {}
    
    if '?' not in url:
        return {}
    
    query_string = url.split('?', 1)[1]
    
    # Strip fragment identifier
    if '#' in query_string:
        query_string = query_string.split('#')[0]
    
    if not query_string:
        return {}
    
    params = {}
    for pair in query_string.split('&'):
        if '=' in pair:
            key, value = pair.split('=', 1)
            params[key] = value
        else:
            params[pair] = ''
    
    return params


def normalize_path(path):
    """Normalize a file path by resolving '..' and '.' components.
    
    Args:
        path: A file path string.
        
    Returns:
        Normalized path string.
    """
    if not path:
        return ''
    
    parts = path.replace('\\\\', '/').split('/')
    result = []
    
    for part in parts:
        if part == '..':
            if result and result[-1] != '..':
                result.pop()
            else:
                result.append(part)
        elif part == '.':
            continue
        elif part:
            result.append(part)
    
    normalized = '/'.join(result)
    if path.startswith('/'):
        normalized = '/' + normalized
    
    return normalized


def merge_configs(base, override):
    """Deep merge two configuration dictionaries.
    
    Args:
        base: Base configuration dict.
        override: Override configuration dict.
        
    Returns:
        New merged dictionary.
    """
    if not isinstance(base, dict) or not isinstance(override, dict):
        return override
    
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result
'''

# Buggy version: parse_url_params doesn't strip '#' fragment from query
SAMPLE_MODULE_BUGGY = SAMPLE_MODULE_FIXED.replace(
    """    # Strip fragment identifier
    if '#' in query_string:
        query_string = query_string.split('#')[0]
    
    if not query_string:""",
    """    # BUG: missing fragment stripping
    if not query_string:"""
)

# ============================================================
# Step 2: Generate test cases (template-based for pilot)
# ============================================================

GENERATED_TESTS_STABLE = '''
"""Generated tests for sample_module - stable version."""
import pytest
from sample_module import parse_url_params, normalize_path, merge_configs


class TestParseUrlParams:
    def test_basic_params(self):
        result = parse_url_params("http://example.com?a=1&b=2")
        assert result == {"a": "1", "b": "2"}
    
    def test_empty_url(self):
        assert parse_url_params("") == {}
    
    def test_none_url(self):
        assert parse_url_params(None) == {}
    
    def test_no_params(self):
        assert parse_url_params("http://example.com") == {}
    
    def test_single_param(self):
        assert parse_url_params("http://x.com?key=val") == {"key": "val"}
    
    def test_param_no_value(self):
        result = parse_url_params("http://x.com?flag")
        assert result == {"flag": ""}
    
    def test_empty_query(self):
        assert parse_url_params("http://x.com?") == {}
    
    def test_multiple_equals(self):
        result = parse_url_params("http://x.com?a=1=2")
        assert result == {"a": "1=2"}


class TestNormalizePath:
    def test_simple_path(self):
        assert normalize_path("/a/b/c") == "/a/b/c"
    
    def test_dotdot(self):
        assert normalize_path("/a/b/../c") == "/a/c"
    
    def test_dot(self):
        assert normalize_path("/a/./b") == "/a/b"
    
    def test_empty(self):
        assert normalize_path("") == ""
    
    def test_relative(self):
        assert normalize_path("a/b/c") == "a/b/c"


class TestMergeConfigs:
    def test_basic_merge(self):
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = merge_configs(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}
    
    def test_deep_merge(self):
        base = {"x": {"a": 1, "b": 2}}
        override = {"x": {"b": 3}}
        result = merge_configs(base, override)
        assert result == {"x": {"a": 1, "b": 3}}
    
    def test_base_unchanged(self):
        base = {"a": 1}
        override = {"b": 2}
        merge_configs(base, override)
        assert base == {"a": 1}
'''

# Tests with intentional flakiness patterns (simulating LLM output)
GENERATED_TESTS_FLAKY = '''
"""Generated tests for sample_module - contains flaky patterns."""
import pytest
import random
import time
import os
from sample_module import parse_url_params, normalize_path, merge_configs


class TestParseUrlParamsFlaky:
    def test_basic_params(self):
        result = parse_url_params("http://example.com?a=1&b=2")
        assert result == {"a": "1", "b": "2"}
    
    def test_random_params(self):
        """FLAKY: uses unseeded random to generate test data."""
        n = random.randint(1, 5)
        params = "&".join("k{}=v{}".format(i, i) for i in range(n))
        url = "http://x.com?" + params
        result = parse_url_params(url)
        assert len(result) == n
    
    def test_dict_ordering(self):
        """POTENTIALLY FLAKY: asserts on string representation of dict."""
        result = parse_url_params("http://x.com?z=1&a=2&m=3")
        # This assertion depends on dict ordering (stable in Python 3.7+, but bad practice)
        result_str = str(result)
        assert "z" in result_str and "a" in result_str
    
    def test_timing_sensitive(self):
        """FLAKY: timing-dependent assertion with impossibly tight threshold."""
        import time
        start = time.perf_counter()
        for _ in range(1000):
            parse_url_params("http://x.com?a=1&b=2&c=3")
        elapsed = time.perf_counter() - start
        # Impossibly tight: will pass sometimes (JIT warmup) but fail often
        assert elapsed < 0.0005, "Took {}s".format(elapsed)
    
    def test_with_tempfile(self):
        """POTENTIALLY FLAKY: uses hardcoded temp path."""
        tmpdir = os.path.join(os.environ.get("TEMP", "/tmp"), "test_url_cache")
        os.makedirs(tmpdir, exist_ok=True)
        filepath = os.path.join(tmpdir, "test.txt")
        with open(filepath, "w") as f:
            f.write("http://x.com?a=1")
        with open(filepath, "r") as f:
            url = f.read()
        result = parse_url_params(url)
        assert result == {"a": "1"}
        # cleanup
        try:
            os.remove(filepath)
            os.rmdir(tmpdir)
        except OSError:
            pass


class TestNormalizePathFlaky:
    def test_simple(self):
        assert normalize_path("/a/b/c") == "/a/b/c"
    
    def test_with_random_depth(self):
        """FLAKY: random test input without seed."""
        depth = random.randint(2, 8)
        parts = ["dir{}".format(i) for i in range(depth)]
        path = "/" + "/".join(parts)
        result = normalize_path(path)
        assert result == path


class TestMergeConfigsFlaky:
    def test_basic(self):
        result = merge_configs({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}
    
    def test_large_random_merge(self):
        """FLAKY: random config generation without seed."""
        base = {"key_{}".format(i): random.randint(0, 100) for i in range(10)}
        override = {"key_{}".format(i): random.randint(0, 100) for i in range(5, 15)}
        result = merge_configs(base, override)
        # Check override keys take precedence
        for k in override:
            assert result[k] == override[k]
'''

# Test that detects the bug (fails on buggy, passes on fixed)
BUG_DETECTING_TEST = '''
"""Test that detects the specific bug in parse_url_params."""
from sample_module import parse_url_params


def test_url_with_fragment():
    """This test catches the bug: fragment not stripped from query."""
    result = parse_url_params("http://x.com?a=1&b=2#section1")
    # Buggy version: b's value becomes "2#section1" instead of "2"
    assert result["b"] == "2", "Fragment leaked into query value: got {}".format(result.get("b"))


def test_url_fragment_only():
    """Another test for fragment handling."""
    result = parse_url_params("http://x.com?key=value#top")
    assert result == {"key": "value"}
'''


def run_pilot():
    """Run the complete pilot test."""
    
    print("=" * 60)
    print("END-TO-END PILOT TEST")
    print("=" * 60)
    
    # Create temp project directory
    pilot_dir = Path(tempfile.mkdtemp(prefix="llm_test_pilot_"))
    print("Working directory: {}".format(pilot_dir))
    
    try:
        # Write fixed version
        fixed_dir = pilot_dir / "fixed"
        fixed_dir.mkdir()
        (fixed_dir / "sample_module.py").write_text(SAMPLE_MODULE_FIXED)
        (fixed_dir / "test_stable.py").write_text(GENERATED_TESTS_STABLE)
        (fixed_dir / "test_flaky.py").write_text(GENERATED_TESTS_FLAKY)
        (fixed_dir / "test_bug_detect.py").write_text(BUG_DETECTING_TEST)
        
        # Write buggy version
        buggy_dir = pilot_dir / "buggy"
        buggy_dir.mkdir()
        (buggy_dir / "sample_module.py").write_text(SAMPLE_MODULE_BUGGY)
        (buggy_dir / "test_stable.py").write_text(GENERATED_TESTS_STABLE)
        (buggy_dir / "test_flaky.py").write_text(GENERATED_TESTS_FLAKY)
        (buggy_dir / "test_bug_detect.py").write_text(BUG_DETECTING_TEST)
        
        # Import our executor
        from src.execution.repeated_executor import run_repeated
        
        results = {}
        
        # ---- Test stable tests on fixed version ----
        print("\n--- Phase 1: Stable tests on FIXED version ---")
        r1 = run_repeated(
            test_file="test_stable.py",
            project_dir=str(fixed_dir),
            num_runs=10,
            timeout=30,
        )
        results["stable_fixed"] = {
            "pass": r1.pass_count, "fail": r1.fail_count,
            "flaky": r1.is_flaky, "rate": r1.flakiness_rate,
            "category": r1.flakiness_category,
        }
        
        # ---- Test flaky tests on fixed version ----
        print("\n--- Phase 2: Flaky tests on FIXED version ---")
        r2 = run_repeated(
            test_file="test_flaky.py",
            project_dir=str(fixed_dir),
            num_runs=10,
            timeout=30,
        )
        results["flaky_fixed"] = {
            "pass": r2.pass_count, "fail": r2.fail_count,
            "flaky": r2.is_flaky, "rate": r2.flakiness_rate,
            "category": r2.flakiness_category,
            "error_types": r2.unique_error_types,
        }
        
        # ---- Test bug-detecting tests on both versions ----
        print("\n--- Phase 3: Bug-detecting tests on FIXED version ---")
        r3 = run_repeated(
            test_file="test_bug_detect.py",
            project_dir=str(fixed_dir),
            num_runs=5,
            timeout=30,
        )
        results["bugdetect_fixed"] = {
            "pass": r3.pass_count, "fail": r3.fail_count,
        }
        
        print("\n--- Phase 4: Bug-detecting tests on BUGGY version ---")
        r4 = run_repeated(
            test_file="test_bug_detect.py",
            project_dir=str(buggy_dir),
            num_runs=5,
            timeout=30,
        )
        results["bugdetect_buggy"] = {
            "pass": r4.pass_count, "fail": r4.fail_count,
        }
        
        # ---- Summary ----
        print("\n" + "=" * 60)
        print("PILOT RESULTS SUMMARY")
        print("=" * 60)
        
        print("\n1. Stable tests on fixed code:")
        print("   Pass: {}/{}  Flaky: {}".format(
            results["stable_fixed"]["pass"], 10, results["stable_fixed"]["flaky"]))
        
        print("\n2. Flaky tests on fixed code:")
        print("   Pass: {}/{}  Flaky: {} ({})".format(
            results["flaky_fixed"]["pass"], 10,
            results["flaky_fixed"]["flaky"], results["flaky_fixed"]["category"]))
        if results["flaky_fixed"]["error_types"]:
            print("   Error types: {}".format(results["flaky_fixed"]["error_types"]))
        
        print("\n3. Bug detection (fixed vs buggy):")
        print("   Fixed: {}/{} passed".format(results["bugdetect_fixed"]["pass"], 5))
        print("   Buggy: {}/{} passed".format(results["bugdetect_buggy"]["pass"], 5))
        
        can_detect = results["bugdetect_fixed"]["pass"] > results["bugdetect_buggy"]["pass"]
        print("   Bug detected: {}".format("YES" if can_detect else "NO"))
        
        print("\n" + "=" * 60)
        print("FEASIBILITY VALIDATION")
        print("=" * 60)
        checks = {
            "Tests execute successfully": results["stable_fixed"]["pass"] > 0,
            "Stable tests are stable": not results["stable_fixed"]["flaky"],
            "Flakiness observable": results["flaky_fixed"]["flaky"] or results["flaky_fixed"]["fail"] > 0,
            "Bug detection works": can_detect,
            "Pipeline runs end-to-end": True,
        }
        all_pass = True
        for check, passed in checks.items():
            status = "PASS" if passed else "FAIL"
            print("  [{}] {}".format(status, check))
            if not passed:
                all_pass = False
        
        print("\nOverall: {}".format("ALL CHECKS PASSED" if all_pass else "SOME CHECKS FAILED"))
        
        # Save results
        output_path = Path(__file__).parent.parent / "results" / "pilot_results.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "pilot_dir": str(pilot_dir),
                "results": results,
                "checks": {k: v for k, v in checks.items()},
            }, f, indent=2)
        print("\nResults saved to: {}".format(output_path))
        
    finally:
        # Cleanup
        shutil.rmtree(pilot_dir, ignore_errors=True)
        print("\nCleaned up temp directory")


if __name__ == "__main__":
    run_pilot()
