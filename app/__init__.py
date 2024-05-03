# app/__init__.py

from flask import Flask
from .blueprints.auth import auth_blueprint
from .blueprints.message import message_blueprint
# from .blueprints.users import users_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(message_blueprint, url_prefix='/messages')
    # app.register_blueprint(users_blueprint, url_prefix='/users')
    return app
