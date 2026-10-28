import pytest
from flask import Flask, Blueprint, request, url_for, current_app
from flask.ctx import AppContext
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
    def not_found(error):
        assert error.code == 404
        return 'Not Found'

    state = BlueprintSetupState(app, blueprint, 'test', __name__)
    blueprint._find_state = lambda: state
    app.register_blueprint(blueprint)

    with AppContext(app):
        assert url_for('test.index') == '/'
        assert current_app.blueprints['test'].before_request_funcs[None] == [before_request]
        assert current_app.error_handler_spec[None][404] == [not_found]

        with pytest.raises(KeyError):
            current_app.blueprints['nonexistent']

        @blueprint.app_template_filter()
        def my_filter(value):
            return value + ' filtered'

        assert app.jinja_env.filters['my_filter'](1) == '1 filtered'