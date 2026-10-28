import pytest
from flask import Flask, Blueprint, url_for
from flask.ctx import AppContext
from flask.testing import FlaskClient

def test_blueprint_register_app():
    app = Flask(__name__)
    blueprint = Blueprint('test', __name__)

    @blueprint.route('/')
    def index():
        return 'Hello, World!'

    blueprint.register_app(app)

    with AppContext(app):
        assert url_for('test.index') == '/'
        client = FlaskClient(app)
        response = client.get('/')
        assert response.data.decode() == 'Hello, World!'