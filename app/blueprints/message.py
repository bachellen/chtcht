# app/blueprints/message.py

from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from rticonnextdds_connector import Connector
import os

message_blueprint = Blueprint('message', __name__)
db = firestore.client()

# Initialize DDS Connector for real-time messaging
connector = Connector(config_name="MyParticipantLibrary::MyPubParticipant",
                      url=os.path.join(os.path.dirname(__file__), 'chtcht.xml'))
output = connector.get_output("MyPublisher::MyChatWriter")
input = connector.get_input("MySubscriber::MyChatReader")

@message_blueprint.route('/messages', methods=['POST'])
def send_message():
    data = request.json
    message = {
        'sender_id': data['sender_id'],
        'conversation_id': data['conversation_id'],
        'text': data['text'],
        'timestamp': firestore.SERVER_TIMESTAMP
    }

    # Send message via DDS
    output.instance.set_dictionary({
        'sender_id': data['sender_id'],
        'conversation_id': data['conversation_id'],
        'text': data['text']
    })
    output.write()

    # Persist message to Firestore
    db.collection('messages').add(message)

    return jsonify({'message': 'Message sent successfully'}), 201

@message_blueprint.route('/messages/<conversation_id>', methods=['GET'])
def get_messages(conversation_id):
    # Retrieve new DDS messages
    input.wait()  # Adjust according to your application's real-time requirements
    input.take()
    messages = []
    for sample in input.samples.valid_data_iter:
        data = sample.get_dictionary()
        if data['conversation_id'] == conversation_id:
            messages.append(data)

    # Optionally, fetch additional messages from Firestore
    messages_query = db.collection('messages').where('conversation_id', '==', conversation_id)\
                       .order_by('timestamp', direction=firestore.Query.ASCENDING)
    firestore_messages = messages_query.stream()
    messages.extend([msg.to_dict() for msg in firestore_messages])

    return jsonify(messages), 200
