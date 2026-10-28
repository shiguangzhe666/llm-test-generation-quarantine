import pytest
import re
from collections import OrderedDict
from config_parser import ConfigParser

def test_config_parser_init_defaults():
    parser = ConfigParser(defaults={"key": "value"})
    assert parser._defaults == {"key": "value"}
    assert parser._sections == OrderedDict()

def test_config_parser_read_string_empty_input():
    parser = ConfigParser()
    parser.read_string("")
    assert parser._sections == OrderedDict()
    assert parser._defaults == {}

def test_config_parser_read_string_valid_section():
    parser = ConfigParser()
    parser.read_string("[section]\nkey=value")
    assert parser._sections == OrderedDict({"section": OrderedDict({"key": "value"})})
    assert parser._defaults == {}

def test_config_not_empty_line_skipped():
    parser = ConfigParser()
    parser.read_string("key=value\n\n# comment\n; another comment")
    assert parser._sections == OrderedDict()
    assert parser._defaults == {"key": "value"}

def test_config_parser_read_string_section_header_only():
    parser = ConfigParser()
    parser.read_string("[section]")
    assert parser._sections == OrderedDict({"section": OrderedDict()})
    assert parser._defaults == {}

def test_config_parser_read_string_quotes_around_value():
    parser = ConfigParser()
    parser.read_string("key=\"value with spaces\"")
    assert parser._defaults == {"key": "value with spaces"}

def test_config_parser_read_string_interpolated_value():
    parser = ConfigParser()
    parser.read_string("key=${section:key}")
    assert parser._defaults == {"key": "${section:key}"}

def test_config_parser_read_string_invalid_line():
    parser = ConfigParser()
    with pytest.raises(ValueError, match=r"Invalid line 1: key=value"):
        parser.read_string("key=value")

def test_config_parser_get_existing_section_key():
    parser = ConfigParser()
    parser.read_string("[section]\nkey=value")
    assert parser.get("section", "key") == "value"

def test_config_parser_get_default_value():
    parser = ConfigParser(defaults={"key": "value"})
    assert parser.get("section", "key") == "value"

def test_config_parser_get_with_fallback():
    parser = ConfigParser()
    parser.read_string("[section]\nkey=value")
    assert parser.get("section", "key", fallback="default") == "value"
    assert parser.get("section", "missing", fallback="default") == "default"

def test_config_parser_get_missing_key():
    parser = ConfigParser()
    parser.read_string("[section]\nkey=value")
    with pytest.raises(KeyError, match=r"No option 'missing' in section 'section'"):
        parser.get("section", "missing")

def test_config_parser_getint_valid_integer():
    parser = ConfigParser()
    parser.read_string("[section]\nkey=42")
    assert parser.getint("section", "key") == 42

def test_config_parser_getint_invalid_integer():
    parser = ConfigParser()
    parser.read_string("[section]\nkey=invalid")
    with pytest.raises(ValueError, match=r"Cannot convert 'invalid' to int for \[section\/key\]"):
        parser.getint("section", "key")

def test_config_parser_getint_with_fallback():
    parser = ConfigParser()
    parser.read_string("[section]\nkey=invalid")
    assert parser.getint("section", "key", fallback=42) == 42

def test_config_parser_getboolean_valid_true():
    parser = ConfigParser()
    parser.read_string("[section]\nkey=true")
    assert parser.getboolean("section", "key") is True

def test_config_parser_getboolean_valid_false():
    parser = ConfigParser()
    parser.read_string("[section]\nkey=false")
    assert parser.getboolean("section", "key") is False

def test_config_parser_getboolean_invalid_string():
    parser = ConfigParser()
    parser.read_string("[section]\nkey=invalid")
    with pytest.raises(ValueError, match=r"Cannot convert 'invalid' to bool for \[section\/key\]"):
        parser.getboolean("section", "key")

def test_config_parser_items_combined_defaults_and_section():
    parser = ConfigParser(defaults={"key": "default"})
    parser.read_string("[section]\nkey=value")
    assert parser.items("section") == [("key", "value")]

def test_config_parser_items_with_missing_section():
    parser = ConfigParser(defaults={"key": "default"})
    parser.read_string("[section]\nkey=value")
    assert parser.items("missing_section") == [("key", "default")]

def test_config_parser_interpolate_basic():
    parser = ConfigParser()
    parser.read_string("[section]\nkey=${section:key}")
    assert parser._interpolate("value ${section:key}", "section") == "value value"

def test_config_parser_interpolate_section_key():
    parser = ConfigParser()
    parser.read_string("[section]\nkey=value")
    assert parser._interpolate("${section:key}", "section") == "value"

def test_config_parser_interpolate_missing_variable():
    parser = ConfigParser()
    assert parser._interpolate("${missing}", "section") == "${missing}"

def test_config_parser_interpolate_nested():
    parser = ConfigParser()
    parser.read_string("[section1]\nkey1=value1\n[section2]\nkey2=${section1:key1}")
    assert parser._interpolate("${section2:key2}", "section2") == "value1"

def test_config_parser_interpolate_non_string_value():
    parser = ConfigParser()
    assert parser._interpolate(42, "section") == 42

def test_config_parser_to_dict():
    parser = ConfigParser()
    parser.read_string("[section1]\nkey1=value1\n[section2]\nkey2=value2")
    assert parser.to_dict() == {"section1": {"key1": "value1"}, "section2": {"key2": "value2"}}
