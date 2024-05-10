# app/__init__.py
import logging

from flask import Flask
from .blueprints.auth import auth_blueprint
from .blueprints.message import message_blueprint
from .blueprints.users import users_blueprint

def create_app():
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='app.log', filemode='a')
    
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)

    # Register blueprints
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(message_blueprint, url_prefix='/messages')
    app.register_blueprint(users_blueprint, url_prefix='/users')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)  # Adjust host and port as needed
