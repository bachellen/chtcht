# app/blueprints/auth.py

from flask import Blueprint, request, jsonify, session
import pyrebase
from google.cloud import firestore
import os
from dotenv import load_dotenv
from ..pubsub_client import publisher, project_id

topic_path = publisher.topic_path(project_id, 'user-presence')


auth_blueprint = Blueprint('auth', __name__)

load_dotenv()
config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

db = firestore.Client(project='massive-carrier-422819-k2', database='chtcht')

@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        # Create user in Firebase Auth
        user = auth.create_user_with_email_and_password(data['email'], data['password'])
        # Prepare user data for Firestore
        user_data = {
            'email': data['email'],
            'displayName': data.get('displayName', ''),
            'createdAt': firestore.SERVER_TIMESTAMP,  # Sets the server timestamp
            'additionalInfo': data.get('additionalInfo', {})  # Optional additional info
        }
        # Save user data in Firestore
        db.collection('users').document(user['localId']).set(user_data)
        return jsonify({'message': 'User registered successfully', 'userId': user['localId']}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    try:
        user = auth.sign_in_with_email_and_password(data['email'], data['password'])
        future = publisher.publish(topic_path, b'Online', user_id=user['localId'])
        future.result()
        if user:
            return jsonify({'message': 'Login successful', 'token': user['idToken'], 'user_id': user['localId']}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': 'Failed to log in', 'details': str(e)}), 401
    
@auth_blueprint.route('/reset_password', methods=['POST'])
def reset_password():
    email = request.json.get('email')
    try:
        auth.send_password_reset_email(email)
        return jsonify({'message': 'Password reset email sent'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@auth_blueprint.route('/logout', methods=['POST'])
def logout():
    user = auth.current_user
    auth.current_user = None
    future = publisher.publish(topic_path, b'Offline', user_id=user['localId'])
    future.result()
    return jsonify({'message': 'Logged out successfully'}), 200

def save_user_to_firestore(user_data):
    db.collection('users').add(user_data)

@auth_blueprint.route('/user', methods=['GET'])
def get_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    try:
        user = auth.get_account_info(session['token'])
        return jsonify({'user': user}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve user', 'details': str(e)}), 400
