# app/blueprints/message.py

from datetime import datetime
from flask import Blueprint, json, request, jsonify, current_app,session
from ..pubsub_client import project_id, publisher, topic_path, subscriber, subscription_path
from google.cloud import firestore
import pyrebase
import os
from dotenv import load_dotenv

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
# Initialize Firestore client
db = firestore.Client(project='massive-carrier-422819-k2', database='chtcht')

message_blueprint = Blueprint('message', __name__)

@message_blueprint.route('/publish', methods=['POST'])
def publish():
   # Verify the Firebase token
    required_fields = ['receiver_id', 'message']
    data = request.get_json()
    try:
        token = request.headers.get('Authorization').split('Bearer ')[1]
        if not data or any(field not in data for field in required_fields):
            return jsonify({'error': 'Missing required data'}), 400
    except Exception as e :
        current_app.logger.error(f"Failed to publish message: {str(e)}")
        return jsonify({'error': 'Unauthorized'}), 401
    # Check for user authorization and required fields

    try:

        # Prepare your data
        user = auth.get_account_info(token)
        user_id = user['users'][0]['localId']
        # to save in db
        data = {
            'sender_id': user_id,
            'receiver_id': request.json.get('receiver_id'),
            'message': request.json.get('message'),
            'timestamp': datetime.now().isoformat()  # Convert datetime to ISO 8601 string format
        }
        # to publish 
        pub_data = {
            'message': request.json.get('message')  ,
            'timestamp': datetime.now().isoformat()  # Convert datetime to ISO 8601 string format
        }
        # Message attributes
        attributes = {
            'sender_id': user_id,
            'receiver_id': request.json.get('receiver_id')
        }

        # Convert dictionary to JSON string
        json_data = json.dumps(pub_data)

        # Encode JSON string to bytes for Pub/Sub
        encoded_data = json_data.encode('utf-8')

        # Publish to Pub/Sub
        future = publisher.publish(topic_path, encoded_data, **attributes)
        pubsub_message_id = future.result()
        current_app.logger.info(f"Message published to Pub/Sub: {pubsub_message_id}")

        # Save to Firestore
        doc_ref = db.collection('messages').add(data)
        firestore_document_id = doc_ref[1].id
        current_app.logger.info(f"Message saved to Firestore with ID: {firestore_document_id}")

        return jsonify({'status': 'success', 'pubsub_message_id': pubsub_message_id, 'firestore_document_id': firestore_document_id, 'message': 'Message published successfully' }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to publish message: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@message_blueprint.route('/subscribe', methods=['GET'])
def subscribe():
    if not request.headers.get('Authorization').split('Bearer ')[1]:
        return jsonify({'error': 'Unauthorized, please login again'}), 401
    token = request.headers.get('Authorization').split('Bearer ')[1]
    try:
        # Verify the Firebase token
        user = auth.get_account_info(token)
        user_id = user['users'][0]['localId']
        response = subscriber.pull(subscription=subscription_path, max_messages=10)
        ack_ids = []
        messages = []
    
        for msg in response.received_messages:
            attributes = msg.message.attributes
            if attributes['receiver_id'] == user_id:
                ack_ids.append(msg.ack_id)
                try:
                    message_data = json.loads(msg.message.data.decode('utf-8'))
                    messages.append(message_data)
                    current_app.logger.info(f"Processed message: {message_data}")
                except json.JSONDecodeError as e:
                    current_app.logger.error(f"Failed to decode JSON message: {str(e)}")
                    continue  # Continue processing other messages even if one fails

        if ack_ids:
            subscriber.acknowledge(subscription=subscription_path, ack_ids=ack_ids)
            current_app.logger.info(f"Acknowledged {len(ack_ids)} messages.")

        return jsonify({'status': 'success', 'messages': messages}), 200

    except Exception as e:
        current_app.logger.error(f"Failed to subscribe and pull messages: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
