# app/blueprints/message.py

import datetime
from flask import Blueprint, request, jsonify, current_app
from ..pubsub_client import project_id, publisher, topic_path, subscriber, subscription_path
from google.cloud import firestore

# Initialize Firestore client
db = firestore.Client()


message_blueprint = Blueprint('message', __name__)

# @message_blueprint.route('/publish', methods=['POST'])
# def publish():
#     if request.is_json and 'message' in request.json:
#         data = request.json['message']
#         data = data.encode('utf-8')
#         current_app.logger.info(f"Publishing message: {data.decode()}")
#         try:
#             # Publish the message
#             future = publisher.publish(topic_path, data)
#             future.result()  # This will raise an exception if the publish fails
#             return jsonify({'status': 'success', 'message': 'Message published successfully'})
#         except Exception as e:
#             current_app.logger.error(f"Error publishing message: {str(e)}")
#             return jsonify({'status': 'error', 'message': 'Failed to publish message'}), 500
#     else:
#         current_app.logger.error("Invalid request format or missing 'message'")
#         return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

@message_blueprint.route('/publish', methods=['POST'])
def publish():
    if request.is_json:
        content = request.json
        sender_id = content.get('sender_id')
        receiver_id = content.get('receiver_id')
        message = content.get('message')
        timestamp = datetime.utcnow()

        # Prepare the message payload
        message_data = {
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'message': message,
            'timestamp': timestamp
        }

        # Encode message data for Pub/Sub
        data = str(message_data).encode("utf-8")

        # Attempt to publish the message to Pub/Sub
        try:
            future = publisher.publish(topic_path, data)
            future.result()  # Wait for publish to complete
            current_app.logger.info(f"Message published to Pub/Sub: {message}")
        except Exception as e:
            current_app.logger.error(f"Failed to publish message to Pub/Sub: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Failed to publish message'}), 500

        # Save the message to Firestore
        try:
            doc_ref = db.collection('messages').add(message_data)
            current_app.logger.info(f"Message saved to Firestore with ID: {doc_ref[1].id}")
        except Exception as e:
            current_app.logger.error(f"Failed to save message to Firestore: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Failed to save message'}), 500

        return jsonify({'status': 'success', 'message': 'Message published and saved successfully'})
    else:
        current_app.logger.error("Invalid request format or missing 'message'")
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

@message_blueprint.route('/subscribe', methods=['GET'])
def subscribe():
    try:
        response = subscriber.pull(request={
            "subscription": subscription_path,
            "max_messages": 10
        })
        current_app.logger.debug(f"Pull response: {response}")

        ack_ids = []
        messages = []
        for msg in response.received_messages:
            messages.append(msg.message.data.decode('utf-8'))
            ack_ids.append(msg.ack_id)

        if ack_ids:
            subscriber.acknowledge(request={
                "subscription": subscription_path,
                "ack_ids": ack_ids
            })
            current_app.logger.info(f"Acknowledged {len(ack_ids)} messages.")
        else:
            current_app.logger.info("No messages to acknowledge.")

        return jsonify({'status': 'success', 'messages': messages})
    except Exception as e:
        current_app.logger.error(f"Failed to subscribe and pull messages: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to pull messages'}), 500
