# app/blueprints/auth.py

from flask import Blueprint, request, jsonify
import pyrebase
import firebase_admin
from firebase_admin import  credentials, firestore

auth_blueprint = Blueprint('auth', __name__)

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)

config = {
    "apiKey": "AIzaSyDC1lNXAFbRZTbb9h2jPLsmQNl1kPKUmd0",
    "authDomain": "chtcht-18e13.firebaseapp.com",
    "projectId": "chtcht-18e13",
    "storageBucket": "chtcht-18e13.appspot.com",
    "messagingSenderId": "83880361772",
    "appId": "1:83880361772:web:12fa8a0cdc852660753689",
    "measurementId": "G-SFK6CSQY0G",
    "databaseURL": "https://chtcht-18e13.firebaseio.com"
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

db = firestore.client()

@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        user = auth.create_user_with_email_and_password(
            data['email'],
            data['password']
        )
        first_name = data['first_name']
        last_name = data['last_name']  
        # Add user to Firestore users collection
        user_data = {
            'userid': user.uid,
            'email': user.email,
            'password' :user.password,
            'first_name': first_name,
            'last_name': last_name,
            'created_at': firestore.SERVER_TIMESTAMP,
            'last_login': None,
      }
        db.collection('users').document(user.uid).set(user_data)
        return jsonify({'message': 'User registered successfully', 'uid': user.uid}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except auth.UserAlreadyExistsError:
        return jsonify({'error': 'User already exists'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to register user', 'details': str(e)}), 500

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    try:
        user = auth.sign_in_with_email_and_password(data['email'], data['password'])

        if user:
            return jsonify({'message': 'Login successful', 'token': user['idToken']}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': 'Failed to log in', 'details': str(e)}), 401