import rticonnextdds_connector as rti

try:
    connector = rti.Connector(config_name="ChatAppParticipantLibrary::ChatAppMainParticipant",
                              url="USER_QOS_PROFILES.xml")
    print("DDS Connector initialized successfully.")
except Exception as e:
    print(f"Failed to initialize DDS Connector: {e}")
