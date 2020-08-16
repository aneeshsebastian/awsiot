
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import random
import re
import subprocess
import json
import base64

AllowedActions = ['both', 'publish', 'subscribe']

def printUSBDeviceDetails():
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb").decode('utf-8')
    #newdf = base64.b64encode(bytes(df, 'utf-8')).decode("ascii")
    print(df)
    
    data = {
        "time" : time.time(),
        "event": "PiEvent",
        "value": df
        }
    print(data)
    json_data = json.dumps(data)
    #json_data["PiEvent"] = df
    print("Raspberry Pi Data : "+json_data)
    return json_data

# Read in command-line parameters
#eventdata = printUSBDeviceDetails()
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="a2u7xya7xj9kj9-ats.iot.us-east-1.amazonaws.com")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="RootCert.crt")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="382310860e-certificate.pem.crt")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="382310860e-private.pem.key")

parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help="RasPi3_SDB")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="pi/Raspberry", help="Payload/topic")
parser.add_argument("-m", "--mode", action="store", dest="mode", default="both",
                    help="Operation modes: %s"%str(AllowedActions))
parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World from RasPi3",
                    help="Message fromRasPi3")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
clientId = args.clientId
topic = args.topic
# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
time.sleep(2)

# Publish to the same topic in a loop forever
loopCount = 0
#while True:
message = {}
message['message'] = args.message
message['sequence'] = loopCount
messageJson = json.dumps(message)
python_object = printUSBDeviceDetails()
json_string = json.dumps(python_object)
myAWSIoTMQTTClient.publish(topic,json_string,1)
print('Published topic %s: %s\n' % (topic, json_string))
        #loopCount += 1
    #time.sleep(3)
