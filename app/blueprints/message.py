from flask import Blueprint, request, jsonify
import dds_publisher
import firebase_admin
from firebase_admin import firestore, exceptions

message_blueprint = Blueprint('message', __name__)

@message_blueprint.route('/send', methods=['POST'])
def send_message():
    message_content = request.json.get('message', '')
    if not message_content:
        return jsonify({"success": False, "error": "No message content provided"}), 400

    try:
        # Publish message using DDS
        dds_publisher.publish_message(message_content)

        # Store message in Firebase Firestore
        db = firestore.client()
        doc_ref = db.collection('messages').add({'message': message_content})
        return jsonify({"success": True, "message": "Message sent and stored in Firestore."}), 200
    except exceptions.FirebaseError as e:
        return jsonify({"success": False, "error": f"Firebase error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
