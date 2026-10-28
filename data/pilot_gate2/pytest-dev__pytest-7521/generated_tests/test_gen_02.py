import pytest
from _pytest.capture import CaptureIO, FDCapture, SysCapture
import os
import tmp_path

def test_capture_preserves_newline(tmp_path):
    file_path = tmp_path / "test_newline.txt"
    with FDCapture(file_path) as fd:
        fd.write("Hello\nWorld")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == "Hello\nWorld"

def test_capture_preserves_carriage_return(tmp_path):
    file_path = tmp_path / "test_carriage_return.txt"
    with FDCapture(file_path) as fd:
        fd.write("Hello\rWorld")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == "Hello\rWorld"

def test_capture_preserves_crlf(tmp_path):
    file_path = tmp_path / "test_crlf.txt"
    with FDCapture(file_path) as fd:
        fd.write("Hello\r\nWorld")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == "Hello\r\nWorld"

def test_capture_empty_string(tmp_path):
    file_path = tmp_path / "test_empty.txt"
    with FDCapture(file_path) as fd:
        fd.write("")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == ""

def test_capture_mixed_line_endings(tmp_path):
    file_path = tmp_path / "test_mixed.txt"
    with FDCapture(file_path) as fd:
        fd.write("a\nb\r\nc\r\n")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == "a\nb\r\nc\r\n"

def test_captureio_preserves_newline(tmp_path):
    file_path = tmp_path / "testio_newline.txt"
    with CaptureIO(file_path) as ci:
        ci.write("Hello\nWorld")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == "Hello\nWorld"

def test_captureio_preserves_carriage_return(tmp_path):
    file_path = tmp_path / "testio_carriage_return.txt"
    with CaptureIO(file_path) as ci:
        ci.write("Hello\rWorld")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == "Hello\rWorld"

def test_captureio_preserves_crlf(tmp_path):
    file_path = tmp_path / "testio_crlf.txt"
    with CaptureIO(file_path) as ci:
        ci.write("Hello\r\nWorld")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == "Hello\r\nWorld"

def test_captureio_empty_string(tmp_path):
    file_path = tmp_path / "testio_empty.txt"
    with CaptureIO(file_path) as ci:
        ci.write("")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == ""

def test_captureio_mixed_line_endings(tmp_path):
    file_path = tmp_path / "testio_mixed.txt"
    with CaptureIO(file_path) as ci:
        ci.write("a\nb\r\nc\r\n")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == "a\nb\r\nc\r\n"

def test_syscapture_preserves_newline(tmp_path):
    file_path = tmp_path / "testsys_newline.txt"
    with SysCapture(file_path) as sc:
        sc.write("Hello\nWorld")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == "Hello\nWorld"

def test_syscapture_preserves_carriage_return(tmp_path):
    file_path = tmp_path / "testsys_carriage_return.txt"
    with SysCapture(file_path) as sc:
        sc.write("Hello\rWorld")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == "Hello\rWorld"

def test_syscapture_preserves_crlf(tmp_path):
    file_path = tmp_path / "testsys_crlf.txt"
    with SysCapture(file_path) as sc:
        sc.write("Hello\r\nWorld")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == "Hello\r\nWorld"

def test_syscapture_empty_string(tmp_path):
    file_path = tmp_path / "testsys_empty.txt"
    with SysCapture(file_path) as sc:
        sc.write("")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == ""

def test_syscapture_mixed_line_endings(tmp_path):
    file_path = tmp_path / "testsys_mixed.txt"
    with SysCapture(file_path) as sc:
        sc.write("a\nb\r\nc\r\n")
    with open(file_path, 'r') as f:
        content = f.read()
    assert content == "a\nb\r\nc\r\n"