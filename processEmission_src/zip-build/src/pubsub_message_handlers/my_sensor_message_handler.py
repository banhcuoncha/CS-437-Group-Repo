 
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0.

'''
my_system_message_handler.py
'''

__version__ = "0.0.7"
__status__ = "Development"
__copyright__ = "Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved."
__author__ = "Dean Colcott <https://www.linkedin.com/in/deancolcott/>"

import logging, random, json
 
# Config the logger.
log = logging.getLogger(__name__)
 
class MySensorMessageHandler():
    '''
    This is an example class that is developed to handle PubSub messages from the 
    AWS Greengrass PubSub SDK. When this class is registered with the SDK, PubSub
    messages will be routed here when the message 'route' value matches any of the 
    function names in this class. 

    In this example, we provide a response to requests to polls a simulated set of 
    temperature sensors as a means of seperating specific PubSub code functionality.

    i.e:
    1) Register this class with the AWS Greengrass PubSub SDK
    2) Any received messages with 'route' = 'my_message_handler' will route to a function here called def my_message_handler()

    ```
    Message handling functions much be in the below format:
    def my_message_handler(self, protocol, topic, message_id, status, route, message):
        # Process message
    ```

    The SDK will decompose the received message fields and route to valid functions here accordingly.    
  
    '''

    def __init__(self, publish_message, publish_error, message_formatter, custom_publisher):
        '''
        A common patten when receiving a PubSub message is to create and publish a response
        so we in this example we pass a reference to the PubSub SDK publish_message, publis_error callbacks 
        and message_formatter object.

        '''
        self.publish_message = publish_message
        self.publish_error = publish_error
        self.message_formatter = message_formatter
        self.publish_to_custom_topic = custom_publisher
        self.max_co2_tracker = {}
        self.route = "process_emission"


    def process_emission(self, protocol, topic, message_id, status, route, message):
        try:
            
            vehicle_id = message["vehicle_id"]
            co2_val = float(message["vehicle_CO2"])
            topic1 = "vehicle/emission/results"
            prev_max = self.max_co2_tracker.get(vehicle_id, 0.0)
            if co2_val > prev_max:
                self.max_co2_tracker[vehicle_id] = co2_val
                result = {"vehicle_id": vehicle_id,
                    "max_CO2": co2_val}
                
                formatted = self.message_formatter.get_message(topic="kinesisfirehose/message",
                    message=result, 
                    message_id=message_id,
                    status=status)
                
                self.publish_message(protocol, message=formatted, topic="vehicle/emission/results")
                logging.info(f"Publishing formatted message: {formatted} on protocol mqtt")
                logging.info(f"[CO2] New max CO2 for {vehicle_id} with value: {co2_val}")
            else:
                logging.info(f"[CO2] CO2 {co2_val} not higher than {prev_max} for {vehicle_id}")
        except Exception as e:
            err_msg = f"[ERROR] Failed to process CO2 message: {e}"
            self.publish_error(protocol, err_msg)

                
   