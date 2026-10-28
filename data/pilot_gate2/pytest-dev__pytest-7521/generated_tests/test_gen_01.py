from _pytest.capture import CaptureIO, FDCapture, SysCapture
import sys

def test_capture_preserves_newlines():
    with SysCapture() as capture:
        sys.stdout.write("Hello\nWorld\rThis is\r\na test")
        sys.stdout.flush()
        captured = capture.gettext()
    assert captured == "Hello\nWorld\rThis is\r\na test"

def test_capture_empty_string():
    with SysCapture() as capture:
        sys.stdout.write("")
        sys.stdout.flush()
        captured = capture.gettext()
    assert captured == ""

def test_capture_with_carriage_return():
    with SysCapture() as capture:
        sys.stdout.write("\r")
        sys.stdout.flush()
        captured = capture.gettext()
    assert captured == "\r"

def test_capture_with_crlf():
    with SysCapture() as capture:
        sys.stdout.write("\r\n")
        sys.stdout.flush()
        captured = capture.gettext()
    assert captured == "\r\n"

def test_capture_mixed_newlines():
    with SysCapture() as capture:
        sys.stdout.write("A\nB\rC\r\nD")
        sys.stdout.flush()
        captured = capture.gettext()
    assert captured == "A\nB\rC\r\nD"

def test_capture_large_data():
    data = "\n".join(["Line"] * 1000)
    with SysCapture() as capture:
        sys.stdout.write(data)
        sys.stdout.flush()
        captured = capture.gettext()
    assert captured == data

def test_capture_multiple_newlines():
    with SysCapture() as capture:
        sys.stdout.write("\n\n\n")
        sys