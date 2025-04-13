import boto3
import json
import os

# AWS IoT client
thingClient = boto3.client('iot', region_name='us-east-2')  # update region if needed

csv_file = 'thing_summary.csv'
file_exists = os.path.isfile(csv_file)
# Constants
THING_COUNT = 1000
THING_NAME_PREFIX = 'iotCar'
POLICY_NAME = 'MyIoTPolicy0' 
OUTPUT_DIR = 'thing_credentials'
THING_GROUP_NAME = 'ThingGroup1'  
EXISTING_COUNT = 10
# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_thing_and_cert(thing_name):
    print(f"🚗 Creating Thing: {thing_name}")
    response = thingClient.create_thing(thingName=thing_name)
    thingArn = response['thingArn']

    # Create certs and keys
    cert = thingClient.create_keys_and_certificate(setAsActive=True)
    certArn = cert['certificateArn']
    certId = cert['certificateId']
    publicKey = cert['keyPair']['PublicKey']
    privateKey = cert['keyPair']['PrivateKey']
    certificatePem = cert['certificatePem']

    # Save credentials
    path_prefix = os.path.join(OUTPUT_DIR, thing_name)
    os.makedirs(path_prefix, exist_ok=True)
    with open(os.path.join(path_prefix, 'public.key'), 'w') as f:
        f.write(publicKey)
    with open(os.path.join(path_prefix, 'private.key'), 'w') as f:
        f.write(privateKey)
    with open(os.path.join(path_prefix, 'cert.pem'), 'w') as f:
        f.write(certificatePem)

    # Attach policy
    thingClient.attach_policy(
        policyName=POLICY_NAME,
        target=certArn
    )

    # Attach cert to Thing
    thingClient.attach_thing_principal(
        thingName=thing_name,
        principal=certArn
    )
    # Add Thing to Thing Group
    thingClient.add_thing_to_thing_group(
        thingName=thing_name,
        thingGroupName=THING_GROUP_NAME
    )

    return {
        'thingName': thing_name,
        'thingArn': thingArn,
        'certArn': certArn,
        'certId': certId
    }

# MAIN LOOP
print(f"Starting creation of {THING_COUNT} Things...")

created = []

for i in range(EXISTING_COUNT, THING_COUNT+EXISTING_COUNT):
    thing_name = f"{THING_NAME_PREFIX}-{i+1:04d}"
    info = create_thing_and_cert(thing_name)
    created.append(info)

# Save summary CSV


with open(csv_file, 'a') as f:
    # Write header only if file doesn't exist yet
    if not file_exists:
        f.write("thingName,thingArn,certArn,certId\n")
    for item in created:
        f.write(f"{item['thingName']},{item['thingArn']},{item['certArn']},{item['certId']}\n")


print("✅ All Things created and saved.")
