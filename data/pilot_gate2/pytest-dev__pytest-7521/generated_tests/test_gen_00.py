import pytest
from _pytest.capture import CaptureIO, FDCapture, SysCapture

def test_capture_preserves_newlines():
    capture = FDCapture()
    capture.write("hello\nworld\r\nfoo")
    content = capture.file.read()
    assert content == b"hello\nworld\r\nfoo"

def test_capture_empty_string():
    capture = FDCapture()
    capture.write("")
    content = capture.file.read()
    assert content == b""

def test_capture_carriage_return_only():
    capture = FDCapture()
    capture.write("\r")
    content = capture.file.read()
    assert content == b"\r"

def test_capture_line_feed_only():
    capture = FDCapture()
    capture.write("\n")
    content = capture.file.read()
    assert content == b"\n"

def test_capture_carriage_return_and_line_feed():
    capture = FDCapture()
    capture.write("\r\n")
    content = capture.file.read()
    assert content == b"\r\n"

def test_capture_mixed_newlines():
    capture = FDCapture()
    capture.write("a\r\nb\n\rc")
    content = capture.file.read()
    assert content == b"a\r\nb\n\rc"

def test_capture_multiple_carriage_returns():
    capture = FDCapture()
    capture.write("\r\r\r")
    content = capture.file.read()
    assert content == b"\r\r\r"

def test_capture_multiple_line_feeds():
    capture = FDCapture()
    capture.write("\n\n\n")
    content = capture.file.read()
    assert content == b"\n\n\n"

def test_capture_combination_of_carriage_return_and_line_feed():
    capture = FDCapture()
    capture.write("start\r\nmiddle\nend")
    content = capture.file.read()
    assert content == b"start\r\nmiddle\nend"

def test_capture_sys_capture_preserves_newlines():
    with SysCapture() as capture:
        print("hello\r\nworld")
    content = capture.gettext()
    assert content == "hello\r\nworld"

def test_capture_sys_capture_empty_string():
    with SysCapture() as capture:
        print("")
    content = capture.gettext()
    assert content == ""

def test_capture_sys_capture_carriage_return():
    with SysCapture() as capture:
        print("\r")
    content = capture.gettext()
    assert content == "\r"

def test_capture_sys_capture_line_feed():
    with SysCapture() as capture:
        print("\n")
    content = capture.gettext()
    assert content == "\n"

def test_capture_sys_capture_carriage_return_and_line_feed():
    with SysCapture() as capture:
        print("\r\n")
    content = capture.gettext()
    assert content == "\r\n"