# app/blueprints/users.py

from flask import Blueprint, request, jsonify
from firebase_admin import firestore

users_blueprint = Blueprint('users', __name__)
db = firestore.client()

@users_blueprint.route('/user/<uid>', methods=['GET'])
def get_user(uid):
    user_ref = db.collection('users').document(uid)
    user = user_ref.get()
    if user.exists:
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@users_blueprint.route('/user/<uid>', methods=['PUT'])
def update_user(uid):
    user_ref = db.collection('users').document(uid)
    user_data = request.json
    user_ref.update(user_data)
    return jsonify({'message': 'User updated successfully'}), 200

@users_blueprint.route('/user/<uid>', methods=['DELETE'])
def delete_user(uid):
    db.collection('users').document(uid).delete()
    return jsonify({'message': 'User deleted successfully'}), 200
