from datetime import timedelta
import logging
from flask import Flask, current_app, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from .blueprints.auth import auth_blueprint
from .blueprints.message import message_blueprint
import os
from dotenv import load_dotenv
from google.cloud import  firestore
from .pubsub_client import subscriber, project_id, subscription_id
import threading
import time


load_dotenv()

socketio = SocketIO(cors_allowed_origins='*')

db = firestore.Client(project=project_id, database='chtcht')
subscription_path = subscriber.subscription_path(project_id, subscription_id)
subscriber_future = None

polling_thread = None
stop_event = threading.Event()

def poll_pubsub_messages(app):
    with app.app_context():
        while not stop_event.is_set():
            response = subscriber.pull(subscription=subscription_path, max_messages=10)
            for received_message in response.received_messages:
                handle_pubsub_message(received_message.message)
                subscriber.acknowledge(subscription=subscription_path, ack_ids=[received_message.ack_id])
            time.sleep(1)  # Adjust the polling interval as needed

def handle_pubsub_message(message):
    receiver_id = message.attributes.get('receiver_id')
    message_content = message.data.decode('utf-8')
    sender_id = message.attributes.get('sender_id')

    # Emit WebSocket event
    socketio.emit('new_message', {'sender_id': sender_id, 'receiver_id': receiver_id, 'message': message_content})
    print(f'Emitted new_message event: {{"receiver_id": {receiver_id}, "message": {message_content}, "sender_id": {sender_id}}}')

def start_pubsub_polling(app):
    global polling_thread
    if polling_thread is None or not polling_thread.is_alive():
        print("Starting Pub/Sub polling...")
        stop_event.clear()
        polling_thread = threading.Thread(target=poll_pubsub_messages, args=(app,))
        polling_thread.start()
    else:
        print("Pub/Sub polling already active.")

def stop_pubsub_polling():
    global polling_thread
    if polling_thread and polling_thread.is_alive():
        print("Stopping Pub/Sub polling...")
        stop_event.set()
        polling_thread.join()
    else:
        print("Pub/Sub polling is not active.")

def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app) 

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True
    )
    app.config['FIREBASE_API_KEY'] = os.getenv('FIREBASE_API_KEY')

    if test_config:
        app.config.update(test_config)

    # Configure logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='app.log', filemode='a')
    
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)

    # Register blueprints
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(message_blueprint, url_prefix='/messages')

    socketio.init_app(app)

    # Define routes to manage Pub/Sub polling
    @app.route('/start_polling', methods=['POST'])
    def start_polling():
        start_pubsub_polling(app)
        return jsonify({'status': 'Polling started'})

    @app.route('/stop_polling', methods=['POST'])
    def stop_polling():
        stop_pubsub_polling()
        return jsonify({'status': 'Polling stopped'})

    # Automatically start Pub/Sub polling when the app starts
    start_pubsub_polling(app)

    return app

if __name__ == '__main__':
    app = create_app()
    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)  # Adjust host and port as needed
    except KeyboardInterrupt:
        stop_pubsub_polling()
        print("Server shut down gracefully.")
