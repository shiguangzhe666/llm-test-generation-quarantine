import pytest

from flask import Blueprint

def test_blueprint_with_non_empty_name():
    # Positive case with non-empty name
    blueprint = Blueprint('valid_name', 'valid_module')
    assert blueprint.name == 'valid_name'

def test_blueprint_with_empty_name_fails():
    # Error case: Blueprint should raise ValueError on empty name
    with pytest.raises(ValueError):
        Blueprint('', 'valid_module')

def test_blueprint_with_space_name_fails():
    # Error case: Blueprint should raise ValueError on name with spaces
    with pytest.raises(ValueError):
        Blueprint('  invalid name  ', 'valid_module')

def test_blueprint_with_name_starting_with_underscore_fails():
    # Error case: Blueprint should raise ValueError on name starting with underscore
    with pytest.raises(ValueError):
        Blueprint('_invalid_name', 'valid_module')

def test_blueprint_with_name_ending_with_underscore_fails():
    # Error case: Blueprint should raise ValueError on name ending with underscore
    with pytest.raises(ValueError):
        Blueprint('invalid_name_', 'valid_module')

def test_blueprint_with_special_characters_fails():
    # Error case: Blueprint should raise ValueError on name with special characters
    with pytest.raises(ValueError):
        Blueprint('invalid/name', 'valid_module')

def test_blueprint_with_only_digits_fails():
    # Error case: Blueprint should raise ValueError on name with only digits
    with pytest.raises(ValueError):
        Blueprint('12345', 'valid_module')

def test_blueprint_with_valid_module_name():
    # Positive case with valid module name
    blueprint = Blueprint('valid_name', 'valid_module')
    assert blueprint.import_name == 'valid_module'

def test_blueprint_with_invalid_module_name_fails():
    # Error case: Blueprint should not raise ValueError on invalid module name
    # This is a non-error case, as the module name is not validated here
    blueprint = Blueprint('valid_name', 'invalid_module')
    assert blueprint.import_name == 'invalid_module'

def test_blueprint_with_valid_module_name_and_empty_name_fails():
    # Error case: Blueprint should raise ValueError on empty name
    with pytest.raises(ValueError):
        Blueprint('', 'valid_module')

def test_blueprint_with_valid_module_name_and_space_name_fails():
    # Error case: Blueprint should raise ValueError on name with spaces
    with pytest.raises(ValueError):
        Blueprint('  invalid name  ', 'valid_module')

def test_blueprint_with_valid_module_name_and_name_starting_with_underscore_fails():
    # Error case: Blueprint should raise ValueError on name starting with underscore
    with pytest.raises(ValueError):
        Blueprint('_invalid_name', 'valid_module')

def test_blueprint_with_valid_module_name_and_name_ending_with_underscore_fails():
    # Error case: Blueprint should raise ValueError on name ending with underscore
    with pytest.raises(ValueError):
        Blueprint('invalid_name_', 'valid_module')

def test_blueprint_with_valid_module_name_and_special_characters_fails():
    # Error case: Blueprint should raise ValueError on name with special characters
    with pytest.raises(ValueError):
        Blueprint('invalid/name', 'valid_module')

def test_blueprint_with_valid_module_name_and_only_digits_fails():
    # Error case: Blueprint should raise ValueError on name with only digits
    with pytest.raises(ValueError):
        Blueprint('12345', 'valid_module')