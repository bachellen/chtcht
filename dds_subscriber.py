import rticonnextdds_connector as rti

def subscribe():
    try:
        with rti.Connector(config_name="ChatAppParticipantLibrary::ChatAppMainParticipant",
                           url="USER_QOS_PROFILES.xml") as connector:
            input = connector.get_input("Subscriber::Reader")
            print("Waiting for messages...")
            while True:
                input.wait()  # Waiting for data to be received
                input.take()
                for sample in input.samples.valid_data_iter:
                    data = sample.get_dictionary()
                    print(f"Received message: {data['message']}")
    except rti.Error as e:
        print(f"DDS Exception: {str(e)}")
        raise Exception(f"Failed to subscribe due to DDS error: {str(e)}")
    except Exception as e:
        print(f"General Exception: {str(e)}")
        raise Exception(f"Failed to subscribe due to unexpected")