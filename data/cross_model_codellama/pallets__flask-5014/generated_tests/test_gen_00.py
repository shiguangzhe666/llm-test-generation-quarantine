from flask import Blueprint, current_app, request, redirect, url_for, abort
from flask.json import jsonify

bp = Blueprint('api', __name__)

@bp.route('/')
def index():
    return 'Hello, World!'

@bp.route('/user/<name>')
def user(name):
    return f'Hello, {name}!'

@bp.route('/user/<name>/<int:age>')
def user_age(name, age):
    return f'{name} is {age} years old!'

@bp.route('/user/<name>/<int:age>/<color>')
def user_age_color(name, age, color):
    return f'{name} is {age} years old, and {color} is their favorite color!'

@bp.route('/user/<name>/<int:age>/<color>/<fruit>')
def user_age_color_fruit(name, age, color, fruit):
    return f'{name} is {age} years old, and {color} is their favorite color. Their favorite fruit is {fruit}!'

@bp.route('/user/<name>/<int:age>/<color>/<fruit>/<pet>')
def user_age_color_fruit_pet(name, age, color, fruit, pet):
    return f'{name} is {age} years old, and {color} is their favorite color. Their favorite fruit is {fruit}. Their favorite pet is {pet}!'