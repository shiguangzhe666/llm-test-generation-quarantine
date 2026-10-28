import os
from _pytest.capture import CaptureIO, FDCapture
import pytest

def test_capture_io_newline_preservation():
    # Positive case: Writing and reading a newline-preserved string
    with CaptureIO() as capture:
        capture.write("Hello\nWorld")
        capture.flush()
        assert capture.getvalue() == "Hello\nWorld"

def test_fdcapture_newline_preservation():
    # Positive case: Writing and reading a newline-preserved string with FDCapture
    with FDCapture() as capture:
        capture.write("Hello\nWorld")
        capture.flush()
        assert capture.getvalue() == "Hello\nWorld"

def test_capture_io_empty_string():
    # Boundary condition: Writing an empty string
    with CaptureIO() as capture:
        capture.write("")
        capture.flush()
        assert capture.getvalue() == ""

def test_fdcapture_empty_string():
    # Boundary condition: Writing an empty string with FDCapture
    with FDCapture() as capture:
        capture.write("")
        capture.flush()
        assert capture.getvalue() == ""

def test_capture_io_single_newline():
    # Edge case: Writing a single newline character
    with CaptureIO() as capture:
        capture.write("\n")
        capture.flush()
        assert capture.getvalue() == "\n"

def test_fdcapture_single_newline():
    # Edge case: Writing a single newline character with FDCapture
    with FDCapture() as capture:
        capture.write("\n")
        capture.flush()
        assert capture.getvalue() == "\n"

def test_capture_io_carriage_return():
    # Error handling: Writing a carriage return character (should be preserved)
    with CaptureIO() as capture:
        capture.write("\r")
        capture.flush()
        assert capture.getvalue() == "\r"

def test_fdcapture_carriage_return():
    # Error handling: Writing a carriage return character with FDCapture (should be preserved)
    with FDCapture() as capture:
        capture.write("\r")
        capture.flush()
        assert capture.getvalue() == "\r"

def test_capture_io_multiple_lines():
    # Positive case: Writing multiple lines with newlines
    with CaptureIO() as capture:
        capture.write("Line 1\nLine 2\nLine 3")
        capture.flush()
        assert capture.getvalue() == "Line 1\nLine 2\nLine 3"

def test_fdcapture_multiple_lines():
    # Positive case: Writing multiple lines with newlines with FDCapture
    with FDCapture() as capture:
        capture.write("Line 1\nLine 2\nLine 3")
        capture.flush()
        assert capture.getvalue() == "Line 1\nLine 2\nLine 3"

def test_capture_io_mixed_newlines():
    # Edge case: Writing mixed newlines (should be preserved)
    with CaptureIO() as capture:
        capture.write("Line 1\r\nLine 2\nLine 3\r")
        capture.flush()
        assert capture.getvalue() == "Line 1\r\nLine 2\nLine 3\r"

def test_fdcapture_mixed_newlines():
    # Edge case: Writing mixed newlines with FDCapture (should be preserved)
    with FDCapture() as capture:
        capture.write("Line 1\r\nLine 2\nLine 3\r")
        capture.flush()
        assert capture.getvalue() == "Line 1\r\nLine 2\nLine 3\r"