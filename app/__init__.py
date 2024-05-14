# app/__init__.py
from datetime import timedelta
import logging
from flask import Flask
from flask_cors import CORS
from .blueprints.auth import auth_blueprint
from .blueprints.message import message_blueprint
import os
from dotenv import load_dotenv
load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app) 
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True
    )
    app.config['FIREBASE_API_KEY'] = os.getenv('FIREBASE_API_KEY')
    # print("Configured API Key:", app.config['FIREBASE_API_KEY'])  # Debugging print


    if test_config:
        app.config.update(test_config)
    if test_config:
        app.config.update(test_config)
    # Configure logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='app.log', filemode='a')
    
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)

    # Register blueprints
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(message_blueprint, url_prefix='/messages')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)  # Adjust host and port as needed
