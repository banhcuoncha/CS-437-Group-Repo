from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time

# ==== Modify these ====
thing_name = "iotCar-0001"
ec2_ip = "3.133.159.43"  # your EC2 public IP
cert_path = "thing_credentials/iotCar-0001/cert.pem"
key_path = "thing_credentials/iotCar-0001/private.key"
root_ca = "AmazonRootCA1.pem"
topic = "clients/123/hello/world"
payload = { "test": "hello from iotCar-0001 via Greengrass" }
# =======================

client = AWSIoTMQTTClient(thing_name)
client.configureEndpoint(ec2_ip, 8883)
client.configureCredentials(root_ca, key_path, cert_path)
client.configureOfflinePublishQueueing(-1)  # Infinite offline queueing
client.configureDrainingFrequency(2)  # 2 Hz draining
client.configureConnectDisconnectTimeout(10)  # 10 sec
client.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and publish
print("📡 Connecting to Greengrass Core...")
client.connect()
print("✅ Connected!")

print(f"📤 Publishing to topic `{topic}`")
client.publish(topic, json.dumps(payload), 0)

time.sleep(1)
client.disconnect()
print("✅ Disconnected.")
