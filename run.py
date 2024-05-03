from flask import Flask
# from  import 
from blueprints.message import message_blueprint
# from blueprints.users import users_blueprint

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'MuhailahAtheer'  # Adjust this as needed

    # Register blueprints
    # app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(message_blueprint, url_prefix='/messages')
    # app.register_blueprint(users_blueprint, url_prefix='/users')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=3000)  # Adjust host and port as needed
