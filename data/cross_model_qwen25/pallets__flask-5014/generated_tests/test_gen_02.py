import pytest
from flask import Flask, Blueprint, request, url_for
from flask.blueprints import BlueprintSetupState

def test_blueprint_setup():
    app = Flask(__name__)
    blueprint = Blueprint('test', __name__)

    @blueprint.route('/')
    def index():
        return 'Index'

    @blueprint.before_app_request
    def before_request():
        assert request.blueprint == 'test'

    @blueprint.app_errorhandler(404)
    def handle_404(error):
        assert request.blueprint == 'test'
        return '404', 404

    app.register_blueprint(blueprint)

    with app.test_client() as client:
        response = client.get('/')
        assert response.data == b'Index'

        response = client.get('/nonexistent', follow_redirects=True)
        assert response.status_code == 404
        assert response.data == b'404'

def test_blueprint_setup_state():
    app = Flask(__name__)

    @app.route('/test')
    def test():
        assert request.blueprint == 'test'
        return 'Test'

    blueprint = Blueprint('test', __name__)

    @blueprint.before_app_request
    def before_request(state: BlueprintSetupState):
        assert state.blueprint == 'test'
        assert state.app == app

    app.register_blueprint(blueprint)

    with app.test_client() as client:
        response = client.get('/test')
        assert response.data == b'Test'