# # dds_subscriber.py

# from rticonnextdds_connector import Connector

# # Configure the DDS Connector from the XML configuration file
# with Connector(config_name="MyParticipantLibrary::MySubParticipant",
#                url="USER_QOS_PROFILES.xml") as connector:

#     # Get the DDS DataReader
#     input = connector.get_input("MySubscriber::MyDataReader")

#     while True:
#         # Wait for data from the DDS Topic
#         input.wait()
#         input.take()

#         for sample in input.samples.valid_data_iter:
#             # Extract the message received
#             message = sample.get_string("data")
#             print(f"Received message: {message}")
