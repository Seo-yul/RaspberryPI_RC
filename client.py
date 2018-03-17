'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
import time
import argparse
import json
import datetime
import re
import os
# Shadow JSON schema:
#
# Name: Bot
# {
#	"state": {
#		"desired":{
#			"property":<INT VALUE>
#		}
#	}
# }

class callbackContainer:

    def __init__(self, deviceShadowInstance): # deviceShadowInstance is deviceShadowHandler
        self.deviceShadowInstance = deviceShadowInstance
        print('Initializing device shadow...')
        self.deviceShadowInstance.shadowGet(self.customShadowCallback_Get, 5) # initialize device shadow
        self.device_num = '1'

    def custom_callback(self, client, userdata, message):

        '''
        print(client)
        print(userdata)
        print("Received a new message: ")
        print(message.payload)
        print("from topic: ")
        print(message.topic)
        print("--------------\n\n")
        '''

        topic = message.topic.split('/')
        messageDict = message.payload.decode('ascii')

        if topic[2] not in [self.device_num, '']:
            return
        else:
            print('Topic come arrived! topic = ' + str(topic))
            print('topic message :' + str(messageDict))

        if topic[1] == 'feed':
           # os.system("") now feed write here
            print('Feeding!')

        elif topic[1] == 'another func...':
            print('another func..')

    def customShadowCallback_Get(self, payload, responseStatus, token):
        # callback for shadowGet
        print('Invoke shadowGet callback: ' + payload)

        self.shadowDict = json.loads(payload)
        if self.shadowDict.get('state'):
            delta = self.shadowDict.get('state').get('delta')
            if delta:
                self.shadowDict['state']['reported'] = self.shadowDict['state']['desired']
                print(self.shadowDict['state']['reported'])
                deltaDict = {
                    'state' : {
                        'reported' : self.shadowDict['state']['reported']
                    }
                }
                self.deviceShadowInstance.shadowUpdate(json.dumps(deltaDict), None, 5)

            if self.shadowDict.get('state').get('desired') != self.shadowDict.get('state').get('reported'):
                for key in self.shadowDict['state']['reported']: # reported state keys
                    if key not in self.shadowDict['state']['desired']:
                        self.shadowDict['state']['reported'][key] = None

                reportedUpdate = {
                    'state' : {
                        'reported' : self.shadowDict['state']['reported']
                    }
                }

                self.deviceShadowInstance.shadowUpdate(json.dumps(reportedUpdate), None, 5)

        else:
            print('AWS IoT Thing Shadow doc initializing...')
            default = {'feedtime' : []}
            self.shadowDict = {
                'state' : {
                    'desired' : default,
                    'reported' : default
                }
            }
            print('self.shadowDict is updated: ' + json.dumps(self.shadowDict))
            self.deviceShadowInstance.shadowUpdate(json.dumps(self.shadowDict), None, 5)

    def customShadowCallback_Delta(self, payload, responseStatus, token):
        # callback for delta listener
        # update self.shadowDict
        #deltaDict = json.loads(payload, encoding = 'utf-8')['state']
        deltaDict = json.loads(payload)['state']
        print('Invoke delta listener callback: ' + str(deltaDict))

        for key in deltaDict.keys():
            self.shadowDict['state']['desired'][key] = deltaDict.get(key)
            self.shadowDict['state']['reported'][key] = deltaDict.get(key)

        print('self.shadowDict is updated: ' + str(self.shadowDict))

        newPayload = '{"state":{"reported":' + json.dumps(deltaDict) + '}}'
        self.deviceShadowInstance.shadowUpdate(newPayload, None, 5) # request to update the reported state

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="Bot", help="Targeted thing name")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicShadowDeltaListener",
                    help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Targeted topic")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
useWebsocket = args.useWebsocket
thingName = args.thingName # for thing shadow bongjafeed
clientId = args.clientId
topic = args.topic # for subscribing the topic 'bongjafeed/'

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

'''
# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
'''

# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = None
if useWebsocket:
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId, useWebsocket=True)
    myAWSIoTMQTTShadowClient.configureEndpoint(host, 443)
    myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId)
    myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
    myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTShadowClient configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()

# Create a deviceShadow with persistent subscription
deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(thingName, True)
callbackContainer_Bot = callbackContainer(deviceShadowHandler)
#print(callbackContainer_Bot.shadowDict['state']['desired'].get('feedtime'))

# Listen on deltas
deviceShadowHandler.shadowRegisterDeltaCallback(callbackContainer_Bot.customShadowCallback_Delta)

myAWSIoTMQTTClient = myAWSIoTMQTTShadowClient.getMQTTConnection()
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing         #
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz                                  #
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe(topic, 1, callbackContainer_Bot.custom_callback)

#print('bongja')
# Loop forever
while True:
    feedtime = callbackContainer_Bot.shadowDict['state']['desired']['feedtime']
    now = datetime.datetime.now().time().replace(second = 0, microsecond = 0)

    if len(feedtime) > 2:
        print('feedtime len: {}, {}, {}'.format(len(feedtime), feedtime, type(feedtime)))
        os.system("./BongjaBab 1")
        if str(now) in feedtime:
            print('bab na on da! Bongja is happy! Feeder sleeps for one minute...')
            os.system("python ./morter.py")
            time.sleep(60)

        else:
            print('bab an na wa... T^T')
    else:
        os.system("./BongjaBab 2")

    time.sleep(5)
