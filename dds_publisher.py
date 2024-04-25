# dds_publisher.py

from rticonnextdds_connector import Connector
import time

# Configure the DDS Connector from the XML configuration file
with Connector(config_name="MyParticipantLibrary::MyPubParticipant",
               url="USER_QOS_PROFILES.xml") as connector:

    # Get the DDS DataWriter
    output = connector.get_output("MyPublisher::MyDataWriter")

    while True:
        # Write a new message to DDS Topic
        message = "Hello from DDS Publisher"
        output.instance.set_string("data", message)
        output.write()
        print(f"Sent message: {message}")
        
        # Wait before sending the next message
        time.sleep(1)
