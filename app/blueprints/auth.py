# app/blueprints/auth.py

from flask import Blueprint, request, jsonify
import firebase_admin
from firebase_admin import auth

auth_blueprint = Blueprint('auth', __name__)
firebase_admin.initialize_app()


@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        user = auth.create_user(
            email=data['email'],
            password=data['password']
        )
        return jsonify({'message': 'User registered successfully', 'uid': user.uid}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except firebase_admin.auth.UserAlreadyExistsError:
        return jsonify({'error': 'User already exists'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to register user', 'details': str(e)}), 500

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    try:
        user = auth.get_user_by_email(data['email'])

        # Authenticate user with Firebase
        user = auth.authenticate(email=data['email'], password=data['password'])

        if user:
            return jsonify({'message': 'Login successful', 'uid': user.uid}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    except auth.UserNotFoundError:
        return jsonify({'error': 'User not found'}), 404
    except auth.InvalidCredentialsError:
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': 'Failed to log in', 'details': str(e)}), 500