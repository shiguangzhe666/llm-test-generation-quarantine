### ✅ **Test Suite: `ConfigParser`**

```python
import pytest
from data.sample_project.config_parser import ConfigParser

# ---------------------------
# 1. Test ConfigParser Initialization
# ---------------------------

def test_config_parser_init_with_defaults():
    defaults = {'key1': 'value1'}
    parser = ConfigParser(defaults)
    assert parser._defaults == defaults
    assert isinstance(parser._sections, dict)
    assert len(parser._sections) == 0

def test_config_parser_init_no_defaults():
    parser = ConfigParser()
    assert parser._defaults == {}
    assert isinstance(parser._sections, dict)
    assert len(parser._sections) == 0

# ---------------------------
# 2. Test Reading Config Strings
# ---------------------------

def test_read_string_valid():
    config_str = """
    [section1]
    key1 = value1
    key2 = value2

    [section2]
    key3 = value3
    """
    parser = ConfigParser()
    parser.read_string(config_str)
    assert parser.sections() == ['section1', 'section2']
    assert parser._sections['section1'] == {'key1': 'value1', 'key2': 'value2'}
    assert parser._sections['section2'] == {'key3': 'value3'}

def test_read_string_empty():
    parser = ConfigParser()
    parser.read_string('')
    assert parser.sections() == []
    assert parser._sections == {}

def test_read_string_comments():
    config_str = """
    # This is a comment
    ; Another comment
    [section]
    key = value
    """
    parser = ConfigParser()
    parser.read_string(config