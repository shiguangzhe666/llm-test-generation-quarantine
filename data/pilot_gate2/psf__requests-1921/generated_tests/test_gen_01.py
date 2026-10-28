import pytest
from requests.sessions import merge_setting, Session

def test_merge_setting_with_both_none():
    request_setting = {'timeout': None}
    session_setting = {'timeout': None}
    result = merge_setting(request_setting, session_setting)
    assert result == {}

def test_merge_setting_request_has_value():
    request_setting = {'timeout': 10}
    session_setting = {'timeout': None}
    result = merge_setting(request_setting, session_setting)
    assert result == {'timeout': 10}

def test_merge_setting_session_has_value():
    request_setting = {'timeout': None}
    session_setting = {'timeout': 10}
    result = merge_setting(request_setting, session_setting)
    assert result == {'timeout': 10}

def test_merge_setting_with_empty_dicts():
    request_setting = {}
    session_setting = {}
    result = merge_setting(request_setting, session_setting)
    assert result == {}

def test_merge_setting_with_mixed_values():
    request_setting = {'timeout': 10, 'headers': {'User-Agent': 'test'}}
    session_setting = {'timeout': None, 'headers': None}
    result = merge_setting(request_setting, session_setting)
    assert result == {'headers': {'User-Agent': 'test'}}

def test_merge_setting_with_nested_none():
    request_setting = {'auth': (None, None)}
    session_setting = {'auth': (None, None)}
    result = merge_setting(request_setting, session_setting)
    assert result == {'auth': (None, None)}

def test_merge_setting_with_non_dict_class():
    request_setting = {'timeout': 10}
    session_setting = {'timeout': None}
    result = merge_setting(request_setting, session_setting, dict_class=dict)
    assert result == {'timeout': 10}