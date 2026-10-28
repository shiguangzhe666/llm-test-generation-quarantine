import pytest
from flask import Blueprint

def test_blueprint_with_non_empty_name():
    # Positive case with non-empty name
    blueprint = Blueprint('valid_name', __name__)
    assert blueprint.name == 'valid_name'

def test_blueprint_with_empty_name():
    # Error case with empty name
    with pytest.raises(ValueError):
        Blueprint('', __name__)

def test_blueprint_with_none_name():
    # Error case with None name
    with pytest.raises(ValueError):
        Blueprint(None, __name__)

def test_blueprint_with_valid_name_type():
    # Positive case with valid name type
    blueprint = Blueprint('valid_name', __name__)
    assert type(blueprint.name) is str

def test_blueprint_with_name_length():
    # Positive case with name length within a reasonable range
    blueprint = Blueprint('a' * 64, __name__)
    assert blueprint.name == 'a' * 64

def test_blueprint_with_name_starting_with_underscores():
    # Error case with name starting with underscores
    with pytest.raises(ValueError):
        Blueprint('_invalid_name', __name__)

def test_blueprint_with_name_starting_with_digits():
    # Error case with name starting with digits
    with pytest.raises(ValueError):
        Blueprint('0invalid_name', __name__)

def test_blueprint_with_name_containing_invalid_characters():
    # Error case with name containing invalid characters
    with pytest.raises(ValueError):
        Blueprint('invalid/name', __name__)

def test_blueprint_with_valid_import_name():
    # Positive case with valid import name
    blueprint = Blueprint('valid_name', __name__)
    assert blueprint.import_name == __name__

def test_blueprint_with_invalid_import_name():
    # Error case with invalid import name
    with pytest.raises(ValueError):
        Blueprint('valid_name', '')