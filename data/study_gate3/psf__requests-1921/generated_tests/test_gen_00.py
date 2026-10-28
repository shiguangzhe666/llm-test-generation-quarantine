import pytest
from requests.sessions import merge_setting, Session

def test_merge_setting_positive_case():
    request_setting = {'timeout': 10, 'verify': True}
    session_setting = {'timeout': 30, 'cert': '/path/to/cert'}
    expected = {'timeout': 30, 'verify': True, 'cert': '/path/to/cert'}
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_with_none_values():
    request_setting = {'timeout': 10, 'verify': True}
    session_setting = {'timeout': None, 'cert': '/path/to/cert'}
    expected = {'verify': True, 'cert': '/path/to/cert'}
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_with_empty_dict():
    request_setting = {}
    session_setting = {'timeout': 30, 'cert': '/path/to/cert'}
    expected = {'timeout': 30, 'cert': '/path/to/cert'}
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_with_all_none():
    request_setting = {'timeout': None, 'verify': None}
    session_setting = {'timeout': None, 'cert': None}
    expected = {}
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_with_conflicting_keys():
    request_setting = {'timeout': 10, 'verify': True}
    session_setting = {'timeout': 30, 'verify': False}
    expected = {'timeout': 30, 'verify': True}  # The first value should be preserved
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_with_non_dict_class():
    request_setting = {'timeout': 10, 'verify': True}
    session_setting = {'timeout': 30, 'cert': '/path/to/cert'}
    expected = {'timeout': 30, 'verify': True, 'cert': '/path/to/cert'}
    assert merge_setting(request_setting, session_setting, dict_class=dict) == expected

def test_merge_setting_with_invalid_input():
    with pytest.raises(TypeError):
        merge_setting(None, {'timeout': 30, 'cert': '/path/to/cert'})
    with pytest.raises(TypeError):
        merge_setting({'timeout': 10, 'verify': True}, None)
    with pytest.raises(TypeError):
        merge_setting(None, None)
    with pytest.raises(TypeError):
        merge_setting({'timeout': 10, 'verify': True}, {'timeout': 30, 'cert': '/path/to/cert'}, dict_class=123)