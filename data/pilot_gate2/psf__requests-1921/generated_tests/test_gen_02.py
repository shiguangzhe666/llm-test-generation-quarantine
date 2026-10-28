import pytest
from requests.sessions import merge_setting, Session

class TestMergeSetting:
    def test_merge_setting_with_none_values(self):
        request_setting = {'timeout': 10, 'verify': True}
        session_setting = {'timeout': None, 'verify': None}
        result = merge_setting(request_setting, session_setting)
        assert result == {'timeout': 10}

    def test_merge_setting_with_both_none(self):
        request_setting = {'timeout': None, 'verify': None}
        session_setting = {'timeout': None, 'verify': None}
        result = merge_setting(request_setting, session_setting)
        assert result == {}

    def test_merge_setting_with_request_setting_only(self):
        request_setting = {'timeout': 10, 'verify': True}
        session_setting = {}
        result = merge_setting(request_setting, session_setting)
        assert result == {'timeout': 10, 'verify': True}

    def test_merge_setting_with_session_setting_only(self):
        request_setting = {}
        session_setting = {'timeout': 10, 'verify': True}
        result = merge_setting(request_setting, session_setting)
        assert result == {'timeout': 10, 'verify': True}

    def test_merge_setting_with_empty_settings(self):
        request_setting = {}
        session_setting = {}
        result = merge_setting(request_setting, session_setting)
        assert result == {}

    def test_merge_setting_with_mixed_none_and_non_none(self):
        request_setting = {'timeout': 10, 'verify': True, 'cert': '/path/to/cert'}
        session_setting = {'timeout': None, 'verify': None}
        result = merge_setting(request_setting, session_setting)
        assert result == {'timeout': 10, 'verify': True, 'cert': '/path/to/cert'}

    def test_merge_setting_with_non_dict_class(self):
        request_setting = {'timeout': 10, 'verify': True}
        session_setting = {'timeout': None, 'verify': None}
        result = merge_setting(request_setting, session_setting, dict_class=dict)
        assert result == {'timeout': 10}