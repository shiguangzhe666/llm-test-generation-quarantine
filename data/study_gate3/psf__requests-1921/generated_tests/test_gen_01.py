from requests.sessions import merge_setting, Session
from collections import OrderedDict

def test_merge_setting_positive_case():
    request_setting = {'a': 1, 'b': 2}
    session_setting = {'b': 3, 'c': 4}
    expected = OrderedDict([('a', 1), ('b', 3), ('c', 4)])
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_request_override():
    request_setting = {'a': 1, 'b': 2}
    session_setting = {'b': None, 'c': 4}
    expected = OrderedDict([('a', 1), ('b', 2), ('c', 4)])
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_session_override():
    request_setting = {'a': 1, 'b': 2}
    session_setting = {'b': 3, 'c': None}
    expected = OrderedDict([('a', 1), ('b', 3), ('c', None)])
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_both_override():
    request_setting = {'a': 1, 'b': 2}
    session_setting = {'b': None, 'c': None}
    expected = OrderedDict([('a', 1), ('b', 2), ('c', None)])
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_empty_request():
    request_setting = {}
    session_setting = {'b': 3, 'c': 4}
    expected = OrderedDict([('b', 3), ('c', 4)])
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_empty_session():
    request_setting = {'a': 1, 'b': 2}
    session_setting = {}
    expected = OrderedDict([('a', 1), ('b', 2)])
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_mixed_types():
    request_setting = {'a': 1, 'b': 'text'}
    session_setting = {'b': None, 'c': 4.5}
    expected = OrderedDict([('a', 1), ('b', 'text'), ('c', 4.5)])
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_non_dict_class():
    request_setting = {'a': 1, 'b': 2}
    session_setting = {'b': 3, 'c': 4}
    expected = {'a': 1, 'b': 3, 'c': 4}  # Using regular dict instead of OrderedDict
    assert merge_setting(request_setting, session_setting, dict_class=dict) == expected

def test_merge_setting_none_input():
    request_setting = {'a': 1, 'b': 2}
    session_setting = None
    expected = {'a': 1, 'b': 2}  # Assuming None input in session_setting should return request_setting
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_none_request():
    request_setting = None
    session_setting = {'b': 3, 'c': 4}
    expected = {'b': 3, 'c': 4}  # Assuming None input in request_setting should return session_setting
    assert merge_setting(request_setting, session_setting) == expected

def test_merge_setting_none_both():
    request_setting = None
    session_setting = None
    assert merge_setting(request_setting, session_setting) is None