"""
Pytest structured reporter plugin.

Captures canonical nodeids (including classes, parameterized values),
accurate outcomes (PASSED, ASSERTION_FAILED, IMPORT_ERROR, COLLECTION_ERROR,
SKIPPED, EXCEPTION), per-test durations, and error details into a JSON report.
Maintains incremental flush so aborted runs preserve all completed tests.
"""

import json
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional


class StructuredCollector:
    def __init__(self, out_path: str):
        self.out_path = out_path
        self.tests: Dict[str, Dict[str, Any]] = {}
        self.collection_errors: List[Dict[str, Any]] = []
        self.runtime_order: List[str] = []
        self.active_test: Optional[str] = None
        self.start_time = time.time()
        os.makedirs(os.path.dirname(os.path.abspath(self.out_path)), exist_ok=True)
        self._flush(exitstatus=None)

    def _flush(self, exitstatus: Optional[int] = None):
        """Atomically persist current execution progress."""
        data = {
            "exitstatus": exitstatus,
            "runtime_order": list(self.runtime_order),
            "active_test": self.active_test,
            "collection_errors": self.collection_errors,
            "tests": self.tests,
        }
        tmp_file = f"{self.out_path}.tmp"
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_file, self.out_path)
        except Exception as exc:
            err_file = f"{self.out_path}.error"
            try:
                with open(err_file, "w", encoding="utf-8") as ef:
                    ef.write(f"REPORT_WRITE_ERROR: {type(exc).__name__}: {str(exc)}\n")
            except Exception:
                pass
            sys.stderr.write(f"[STRUCTURED_PLUGIN_ERROR] Failed to write report {self.out_path}: {exc}\n")

    def pytest_collectreport(self, report):
        if report.failed:
            longrepr = str(report.longrepr)
            err_cat = "COLLECTION_ERROR"
            if "ImportError" in longrepr or "ModuleNotFoundError" in longrepr:
                err_cat = "IMPORT_ERROR"
            self.collection_errors.append({
                "nodeid": report.nodeid,
                "outcome": err_cat,
                "error_type": err_cat,
                "error_message": longrepr[:1000],
            })
            self._flush()

    def pytest_runtest_logreport(self, report):
        nodeid = report.nodeid
        if nodeid not in self.tests:
            self.tests[nodeid] = {
                "nodeid": nodeid,
                "outcome": "PASSED",
                "duration": 0.0,
                "error_type": None,
                "error_message": None,
            }

        # Accumulate duration across phases (setup, call, teardown)
        self.tests[nodeid]["duration"] += getattr(report, "duration", 0.0)

        # Track runtime execution order and active test
        if nodeid not in self.runtime_order:
            self.runtime_order.append(nodeid)

        if report.when == "call" and not report.passed:
            self.active_test = nodeid
        elif report.when == "teardown":
            self.active_test = None

        # Handle skipped tests (usually happens in setup)
        if report.skipped:
            if self.tests[nodeid]["outcome"] == "PASSED":
                self.tests[nodeid]["outcome"] = "SKIPPED"
                self.tests[nodeid]["error_message"] = str(getattr(report, "longrepr", ""))[:300]
            self._flush()
            return

        # Handle setup failure (e.g. fixture or import error)
        if report.when == "setup" and report.failed:
            longrepr = str(report.longrepr)
            if "ImportError" in longrepr or "ModuleNotFoundError" in longrepr:
                err_cat = "IMPORT_ERROR"
            else:
                err_cat = "EXCEPTION"
            self.tests[nodeid]["outcome"] = err_cat
            self.tests[nodeid]["error_type"] = err_cat
            self.tests[nodeid]["error_message"] = longrepr[:1000]
            self._flush()

        elif report.when == "call":
            if report.failed:
                longrepr = str(report.longrepr)
                if "AssertionError" in longrepr or "assert " in longrepr.lower():
                    err_cat = "ASSERTION_FAILED"
                    err_type = "AssertionError"
                elif "ImportError" in longrepr or "ModuleNotFoundError" in longrepr:
                    err_cat = "IMPORT_ERROR"
                    err_type = "ImportError"
                elif "Timeout" in longrepr:
                    err_cat = "TIMEOUT"
                    err_type = "Timeout"
                else:
                    err_cat = "EXCEPTION"
                    exc_match = re.search(r"([A-Za-z0-9_]+Error|[A-Za-z0-9_]+Exception)", longrepr)
                    err_type = exc_match.group(1) if exc_match else "EXCEPTION"
                self.tests[nodeid]["outcome"] = err_cat
                self.tests[nodeid]["error_type"] = err_type
                self.tests[nodeid]["error_message"] = longrepr[:1000]
            self._flush()

        # Handle teardown failure
        elif report.when == "teardown" and report.failed:
            if self.tests[nodeid]["outcome"] == "PASSED":
                self.tests[nodeid]["outcome"] = "EXCEPTION"
                self.tests[nodeid]["error_type"] = "TEARDOWN_EXCEPTION"
                self.tests[nodeid]["error_message"] = str(report.longrepr)[:1000]
            self._flush()

    def pytest_sessionfinish(self, session, exitstatus):
        self.active_test = None
        self._flush(exitstatus=exitstatus)


def pytest_configure(config):
    if os.environ.get("HERMETIC_CI") == "1":
        import socket
        _orig_connect = socket.socket.connect
        def _hermetic_connect(self, address, *args, **kwargs):
            host = address[0] if isinstance(address, (tuple, list)) and len(address) > 0 else str(address)
            if host not in ("127.0.0.1", "localhost", "::1", "0.0.0.0"):
                raise OSError(f"[Hermetic CI Violation] Outbound network connection to {host} is blocked in hermetic CI sandbox")
            return _orig_connect(self, address, *args, **kwargs)
        socket.socket.connect = _hermetic_connect

    out_path = os.environ.get("PYTEST_STRUCTURED_REPORT_PATH")
    if out_path:
        config.pluginmanager.register(StructuredCollector(out_path), "structured_collector")
