import os
from _pytest.capture import CaptureIO, FDCapture

def test_captureio_newline_preservation():
    capture_io = CaptureIO()
    input_data = "Hello\nWorld\r\n"
    expected_output = "Hello\nWorld\n"
    
    capture_io.write(input_data)
    captured = capture_io.getvalue()
    
    assert captured == expected_output, f"Expected {expected_output}, but got {captured}"

def test_fd_capture_newline_preservation():
    fd_capture = FDCapture()
    input_data = "Hello\nWorld\r\n"
    expected_output = "Hello\nWorld\n"
    
    fd_capture.write(input_data)
    captured = fd_capture.getvalue()
    
    assert captured == expected_output, f"Expected {expected_output}, but got {captured}"

def test_captureio_empty_input():
    capture_io = CaptureIO()
    input_data = ""
    expected_output = ""
    
    capture_io.write(input_data)
    captured = capture_io.getvalue()
    
    assert captured == expected_output, f"Expected {expected_output}, but got {captured}"

def test_fd_capture_empty_input():
    fd_capture = FDCapture()
    input_data = ""
    expected_output = ""
    
    fd_capture.write(input_data)
    captured = fd_capture.getvalue()
    
    assert captured == expected_output, f"Expected {expected_output}, but got {captured}"

def test_captureio_large_input():
    capture_io = CaptureIO()
    input_data = "Line1\nLine2\r\nLine3\rLine4\n"
    expected_output = "Line1\nLine2\nLine3\nLine4\n"
    
    capture_io.write(input_data)
    captured = capture_io.getvalue()
    
    assert captured == expected_output, f"Expected {expected_output}, but got {captured}"

def test_fd_capture_large_input():
    fd_capture = FDCapture()
    input_data = "Line1\nLine2\r\nLine3\rLine4\n"
    expected_output = "Line1\nLine2\nLine3\nLine4\n"
    
    fd_capture.write(input_data)
    captured = fd_capture.getvalue()
    
    assert captured == expected_output, f"Expected {expected_output}, but got {captured}"

def test_captureio_non_ascii_input():
    capture_io = CaptureIO()
    input_data = "Hello\nWorld\r\n"
    expected_output = "Hello\nWorld\n"
    
    capture_io.write(input_data)
    captured = capture_io.getvalue()
    
    assert captured == expected_output, f"Expected {expected_output}, but got {captured}"

def test_fd_capture_non_ascii_input():
    fd_capture = FDCapture()
    input_data = "Hello\nWorld\r\n"
    expected_output = "Hello\nWorld\n"
    
    fd_capture.write(input_data)
    captured = fd_capture.getvalue()
    
    assert captured == expected_output, f"Expected {expected_output}, but got {captured}"

def test_captureio_multiple_writes():
    capture_io = CaptureIO()
    input_data1 = "Line1\n"
    input_data2 = "Line2\r\nLine3\r"
    expected_output = "Line1\nLine2\nLine3\n"
    
    capture_io.write(input_data1)
    capture_io.write(input_data2)
    captured = capture_io.getvalue()
    
    assert captured == expected_output, f"Expected {expected_output}, but got {captured}"

def test_fd_capture_multiple_writes():
    fd_capture = FDCapture()
    input_data1 = "Line1\n"
    input_data2 = "Line2\r\nLine3\r"
    expected_output = "Line1\nLine2\nLine3\n"
    
    fd_capture.write(input_data1)
    fd_capture.write(input_data2)
    captured = fd_capture.getvalue()
    
    assert captured == expected_output, f"Expected {expected_output}, but got {captured}"

def test_captureio_readline():
    capture_io = CaptureIO()
    input_data = "Line1\nLine2\r\nLine3\rLine4\n"
    expected_output = ["Line1\n", "Line2\n", "Line3\n", "Line4\n"]
    
    capture_io.write(input_data)
    lines = capture_io.readlines()
    
    assert lines == expected_output, f"Expected {expected_output}, but got {lines}"

def test_fd_capture_readline():
    fd_capture = FDCapture()
    input_data = "Line1\nLine2\r\nLine3\rLine4\n"
    expected_output = ["Line1\n", "Line2\n", "Line3\n", "Line4\n"]
    
    fd_capture.write(input_data)
    lines = fd_capture.readlines()
    
    assert lines == expected_output, f"Expected {expected_output}, but got {lines}"

def test_captureio_readline_with_empty_input():
    capture_io = CaptureIO()
    input_data = ""
    expected_output = []
    
    capture_io.write(input_data)
    lines = capture_io.readlines()
    
    assert lines == expected_output, f"Expected {expected_output}, but got {lines}"

def test_fd_capture_readline_with_empty_input():
    fd_capture = FDCapture()
    input_data = ""
    expected_output = []
    
    fd_capture.write(input_data)
    lines = fd_capture.readlines()
    
    assert lines == expected_output, f"Expected {expected_output}, but got {lines}"