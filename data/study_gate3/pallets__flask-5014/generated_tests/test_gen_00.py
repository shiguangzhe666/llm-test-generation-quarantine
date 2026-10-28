import pytest
from flask import Blueprint

def test_blueprint_with_valid_name():
    # Test with a valid non-empty name
    blueprint = Blueprint('valid_name', 'module.name')
    assert blueprint.name == 'valid_name'

def test_blueprint_with_empty_name():
    # Test with an empty name, should raise ValueError
    with pytest.raises(ValueError):
        Blueprint('', 'module.name')

def test_blueprint_with_none_name():
    # Test with None as name, should raise ValueError
    with pytest.raises(ValueError):
        Blueprint(None, 'module.name')

def test_blueprint_with_long_name():
    # Test with a very long name ( Flask's Blueprint supports up to 255 characters )
    long_name = 'a' * 255
    blueprint = Blueprint(long_name, 'module.name')
    assert blueprint.name == long_name

def test_blueprint_with_special_characters_in_name():
    # Test with a name containing special characters ( Flask's Blueprint supports alphanumeric and some special characters )
    blueprint = Blueprint('valid_name@123', 'module.name')
    assert blueprint.name == 'valid_name@123'

def test_blueprint_with_name_starting_with_special_characters():
    # Test with a name starting with a special character ( Flask's Blueprint does not allow names starting with special characters )
    with pytest.raises(ValueError):
        Blueprint('@valid_name', 'module.name')

def test_blueprint_with_name_ending_with_special_characters():
    # Test with a name ending with a special character ( Flask's Blueprint does not allow names ending with special characters )
    with pytest.raises(ValueError):
        Blueprint('valid_name@', 'module.name')

def test_blueprint_with_name_containing_spaces():
    # Test with a name containing spaces ( Flask's Blueprint does not allow names with spaces )
    with pytest.raises(ValueError):
        Blueprint('valid name', 'module.name')

def test_blueprint_with_name_starting_with_underscore():
    # Test with a name starting with an underscore ( Flask's Blueprint does not allow names starting with underscores )
    with pytest.raises(ValueError):
        Blueprint('_valid_name', 'module.name')

def test_blueprint_with_name_ending_with_underscore():
    # Test with a name ending with an underscore ( Flask's Blueprint does not allow names ending with underscores )
    with pytest.raises(ValueError):
        Blueprint('valid_name_', 'module.name')

def test_blueprint_with_name_starting_with_number():
    # Test with a name starting with a number ( Flask's Blueprint does not allow names starting with numbers )
    with pytest.raises(ValueError):
        Blueprint('1valid_name', 'module.name')

def test_blueprint_with_name_ending_with_number():
    # Test with a name ending with a number ( Flask's Blueprint does not allow names ending with numbers )
    with pytest.raises(ValueError):
        Blueprint('valid_name1', 'module.name')