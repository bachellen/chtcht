# app/publish_client.py
from google.cloud import pubsub_v1

# Initialize Publisher and Subscriber clients
publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

# Define the project ID and topic/subscription names
project_id = "massive-carrier-422819-k2"
topic_id = "chat-messages"
subscription_id = "chat-messages-sub"

# Construct full path to the resources
topic_path = "projects/massive-carrier-422819-k2/topics/chat-messages"
subscription_path = "projects/massive-carrier-422819-k2/subscriptions/chat-messages-sub"
