# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import pandas as pd
import numpy as np


#TODO 1: modify the following parameters
#Starting and end index, modify this
device_st = 1
device_end = 6

#Path to the dataset, modify this
data_path = "./vehicle_data/vehicle{}.csv"

#Path to your certificates, modify this
certificate_formatter = "thing_credentials/iotCar-{0:04d}/cert.pem"
key_formatter = "thing_credentials/iotCar-{0:04d}/private.key"


class MQTTClient:
    def __init__(self, device_id, cert, key):
        # For certificate based connection
        self.device_id = str(device_id)
        self.state = 0
        self.client = AWSIoTMQTTClient(self.device_id)
        #TODO 2: modify your broker address
        self.client.configureEndpoint("azkbo44dx0fr5-ats.iot.us-east-2.amazonaws.com", 8883)
        self.client.configureCredentials("./keys/AmazonRootCA1.pem", key, cert)
        self.client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec
        self.client.onMessage = self.customOnMessage
        # Subscribe to the result topic for this device
        result_topic = "example.processEmission/vehicle/emission/results"
        self.client.subscribeAsync(result_topic, 1, ackCallback=self.customSubackCallback, messageCallback=self.customOnMessage)
        print(f"[Device {self.device_id}] Subscribed to {result_topic}")


    def customOnMessage(self,message):
        #TODO 3: fill in the function to show your received message
        print("client {} received payload {} from topic {}".format(self.device_id,message.payload.decode() , message.topic))


    # Suback callback
    def customSubackCallback(self,mid, data):
        #You don't need to write anything here
        pass


    # Puback callback
    def customPubackCallback(self,mid):
        #You don't need to write anything here
        pass


    def publish(self, topic="vehicle/emission/data"):
    # Load the vehicle's emission data
        df = pd.read_csv(data_path.format(self.device_id))
        for index, row in df.iterrows():
            # Create a JSON payload from the row data
            raw_msg = row.to_dict()
            sdk_msg = {
                "sdk_version": "0.0.6",
                "message_id": f"veh_{self.device_id}_{int(time.time()*1000)}",
                "status": 200,
                "route": "MySensorMessageHandler.process_emission",
                "message": raw_msg
            }
            payload = json.dumps(sdk_msg)
            # Publish the payload to the specified topic
            #print(f"Publishing: {payload} to {topic}")
            self.client.publishAsync(topic, payload, 0, ackCallback=self.customPubackCallback)
            time.sleep(0.5)
            # Sleep to simulate real-time data publishing
            



print("Loading vehicle data...")
data = []
for i in range(device_st,device_end):
    a = pd.read_csv(data_path.format(i))
    data.append(a)

print("Initializing MQTTClients...")
clients = []
for device_id in range(device_st, device_end):
    client = MQTTClient(device_id,certificate_formatter.format(device_id,device_id) ,key_formatter.format(device_id,device_id))
    connected = client.client.connect()
    if connected:
        print(f" {device_id} connected")
    else:
        print(f" {device_id} failed to connect")
    clients.append(client)
 

while True:
    print("send now?")
    x = input()
    if x == "s":
        for i,c in enumerate(clients):
            c.publish()

    elif x == "d":
        for c in clients:
            c.client.disconnect()
        print("All devices disconnected")
        exit()
    else:
        print("wrong key pressed")

    time.sleep(3)





