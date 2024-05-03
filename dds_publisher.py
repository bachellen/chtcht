import rticonnextdds_connector as rti

def publish_message(message):
    try:
        with rti.Connector(config_name="ChatAppParticipantLibrary::ChatAppMainParticipant",
                           url="USER_QOS_PROFILES.xml") as connector:
            output = connector.get_output("Publisher::Writer")
            output.instance.set_string("message", message)
            output.write()
            print(f"Message published: {message}")
    except rti.Error as e:
        print(f"DDS Exception: {str(e)}")
        raise Exception(f"Failed to publish message due to DDS error: {str(e)}")
    except Exception as e:
        print(f"General Exception: {str(e)}")
        raise Exception(f"Failed to publish message due to unexpected error: {str(e)}")
