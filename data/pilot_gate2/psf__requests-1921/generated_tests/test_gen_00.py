from requests.sessions import merge_setting, Session

def test_merge_setting_with_none_values():
    request_setting = {'timeout': 10, 'verify': True}
    session_setting = {'timeout': None, 'cert': None}
    expected = {'timeout': 10}
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_with_only_none_values():
    request_setting = {'timeout': None, 'verify': None}
    session_setting = {}
    expected = {}
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_with_request_overriding_session():
    request_setting = {'timeout': 30, 'verify': True}
    session_setting = {'timeout': 10, 'verify': False}
    expected = {'timeout': 30, 'verify': True}
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_with_session_overriding_request():
    request_setting = {'timeout': 5, 'verify': False}
    session_setting = {'timeout': 10, 'verify': True}
    expected = {'timeout': 10, 'verify': True}
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_with_empty_settings():
    request_setting = {}
    session_setting = {}
    expected = {}
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_with_non_dict_class():
    request_setting = {'timeout': 10, 'verify': True}
    session_setting = {'timeout': None, 'verify': None}
    expected = {'timeout': 10}
    assert merge_setting(request_setting, session_setting, dict_class=dict) == expected

def test_merge_setting_with_no_none_values():
    request_setting = {'timeout': 10, 'verify': True}
    session_setting = {'timeout': 10, 'verify': True}
    expected = {'timeout': 10, 'verify': True}
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_with_mixed_values():
    request_setting = {'timeout': 5, 'verify': True, 'cert': 'path/to/cert'}
    session_setting = {'timeout': 10, 'verify': False, 'cert': None}
    expected = {'timeout': 10, 'verify': True, 'cert': 'path/to/cert'}
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_with_only_session_none():
    request_setting = {'timeout': 10, 'verify': True}
    session_setting = {'timeout': None, 'verify': None, 'cert': None}
    expected = {'timeout': 10, 'verify': True}
    assert merge_setting(request_setting, session_setting) == expected