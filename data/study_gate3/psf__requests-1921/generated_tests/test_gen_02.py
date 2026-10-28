from requests.sessions import merge_setting, Session
from collections import OrderedDict

def test_merge_setting_with_default_dict_class():
    request_setting = {"timeout": 10, "verify": True}
    session_setting = {"timeout": None, "cert": "/path/to/cert"}
    expected = OrderedDict([("verify", True), ("cert", "/path/to/cert")])
    result = merge_setting(request_setting, session_setting)
    assert result == expected

def test_merge_setting_with_no_session_settings():
    request_setting = {"timeout": 10, "verify": True}
    session_setting = {}
    expected = OrderedDict([("timeout", 10), ("verify", True)])
    result = merge_setting(request_setting, session_setting)
    assert result == expected

def test_merge_setting_with_no_request_settings():
    request_setting = {}
    session_setting = {"timeout": None, "cert": "/path/to/cert"}
    expected = OrderedDict([("cert", "/path/to/cert")])
    result = merge_setting(request_setting, session_setting)
    assert result == expected

def test_merge_setting_with_nested_dicts():
    request_setting = {"timeout": 10, "cert": {"ca": "/path/to/ca"}}
    session_setting = {"timeout": None, "cert": {"ca": None, "key": "/path/to/key"}}
    expected = OrderedDict([("timeout", 10), ("cert", {"key": "/path/to/key"})])
    result = merge_setting(request_setting, session_setting)
    assert result == expected

def test_merge_setting_with_merging_lists():
    request_setting = {"timeout": 10, "proxies": {"http": "http://user:pass@10.10.1.10:3128"}}
    session_setting = {"timeout": None, "proxies": {"https": "https://10.10.1.10:3128"}}
    expected = OrderedDict([("timeout", 10), ("proxies", {"http": "http://user:pass@10.10.1.10:3128", "https": "https://10.10.1.10:3128"})])
    result = merge_setting(request_setting, session_setting)
    assert result == expected

def test_merge_setting_with_merging_lists_with_none():
    request_setting = {"timeout": 10, "proxies": {"http": None}}
    session_setting = {"timeout": None, "proxies": {"https": "https://10.10.1.10:3128"}}
    expected = OrderedDict([("timeout", 10), ("proxies", {"https": "https://10.10.1.10:3128"})])
    result = merge_setting(request_setting, session_setting)
    assert result == expected

def test_merge_setting_with_merging_lists_with_none_in_request():
    request_setting = {"timeout": 10, "proxies": {"https": None}}
    session_setting = {"timeout": None, "proxies": {"http": "http://user:pass@10.10.1.10:3128"}}
    expected = OrderedDict([("timeout", 10), ("proxies", {"http": "http://user:pass@10.10.1.10:3128"})])
    result = merge_setting(request_setting, session_setting)
    assert result == expected

def test_merge_setting_with_merging_lists_with_none_in_both():
    request_setting = {"timeout": 10, "proxies": {"https": None}}
    session_setting = {"timeout": None, "proxies": {"https": None}}
    expected = OrderedDict([("timeout", 10)])
    result = merge_setting(request_setting, session_setting)
    assert result == expected

def test_merge_setting_with_merging_lists_with_empty_dict():
    request_setting = {"timeout": 10, "headers": {"User-Agent": "test"}}
    session_setting = {"timeout": None, "headers": {}}
    expected = OrderedDict([("timeout", 10), ("headers", {"User-Agent": "test"})])
    result = merge_setting(request_setting, session_setting)
    assert result == expected

def test_merge_setting_with_merging_lists_with_empty_dict_in_request():
    request_setting = {"timeout": 10, "headers": {}}
    session_setting = {"timeout": None, "headers": {"User-Agent": "test"}}
    expected = OrderedDict([("timeout", 10), ("headers", {"User-Agent": "test"})])
    result = merge_setting(request_setting, session_setting)
    assert result == expected

def test_merge_setting_with_merging_lists_with_empty_dict_in_session():
    request_setting = {"timeout": 10, "headers": {"User-Agent": "test"}}
    session_setting = {"timeout": None, "headers": {}}
    expected = OrderedDict([("timeout", 10), ("headers", {"User-Agent": "test"})])
    result = merge_setting(request_setting, session_setting)
    assert result == expected

def test_merge_setting_with_merging_lists_with_empty_dict_in_both():
    request_setting = {"timeout": 10, "headers": {}}
    session_setting = {"timeout": None, "headers": {}}
    expected = OrderedDict([("timeout", 10)])
    result = merge_setting(request_setting, session_setting)
    assert result == expected

def test_merge_setting_with_merging_lists_with_empty_dict_in_both():
    request_setting = {"timeout": 10, "headers": {}}
    session_setting = {"timeout": None, "headers": {}}
    expected = OrderedDict([("timeout", 10)])
    result = merge_setting(request_setting, session_setting)
    assert result == expected

def test_merge_setting_with_merging_lists_with_empty_dict_in_both():
    request_setting = {"timeout": 10, "headers": {}}
    session_setting = {"timeout": None, "headers": {}}
    expected = OrderedDict([("timeout", 10)])
    result = merge_setting(request_setting, session_setting)
    assert result == expected