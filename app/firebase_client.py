from flask import request, jsonify
from firebase_admin import auth

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data['email']
    password = data['password']
    first_name = data['first_name']
    last_name = data['last_name']

    # Create user with Firebase Authentication
    user_record = auth.create_user(
        email=email,
        password=password
    )

    # Save additional user info in Firestore
    user_info = {
        'user_id': user_record.uid,
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'created_at': firestore.SERVER_TIMESTAMP,
        'last_login': None,
    }
    db.collection('users').document(user_record.uid).set(user_info)

    return jsonify({'message': 'User registered successfully', 'uid': user_record.uid}), 201
