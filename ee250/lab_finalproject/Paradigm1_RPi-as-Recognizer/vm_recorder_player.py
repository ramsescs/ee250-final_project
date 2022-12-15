""" 
EE 250L Final Project: Humify!

Code by: 
    - Ramses Maurice, Contreras Sulbaran

https://github.com/ramsescs/ee250-finalproject
git@github.com:ramsescs/ee250-finalproject.git

Paradigm 1
==========
This file is part of paradigm 1, where the RPi will be the recognizer.

VM Recorder/Player
------------------
Description: This is the file to be executed in the VM/Other machine. It received a request from the RPI to start
the recording, and once it is done recording, it will send the sound signal vector as a pickled sequence.

"""
import sounddevice as sd
import threading
import paho.mqtt.client as mqtt
import time
from playsound import playsound
import pickle

lock = threading.Lock()

# Recording Parameters
fs = 44100  # Sample rate
duration = 10  # Duration of recording

# Global client so all functions can access it
local_client = mqtt.Client()

# Custom callback for the recorder topic (record button)
def recorder_callback(client, userdata, msg):

    content = str(msg.payload, "utf-8")
    
    if content == 'REC':
        # Record incoming sound
        # Lock to allow only one recording at a time
        with lock:

            print('Init Recording')

            incoming_sound = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()  # Wait until recording is finished

            print('Done Recording')

            pickled_sound = pickle.dumps(incoming_sound[:,0])

            local_client.publish('ramsesma/recognizer', pickled_sound)
    else:
        print("Error in REC format!")

# Setup once conneciton to broker is succesful
def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    # subscribing to topics of interest
    # and setting up custom callbacks
    client.subscribe("ramsesma/recorder")
    client.message_callback_add("ramsesma/recorder", recorder_callback)

    client.subscribe("ramsesma/speaker")
    client.message_callback_add("ramsesma/speaker", speaker_callback)

    client.subscribe('ramsesma/rpisaluter')
    client.message_callback_add("ramsesma/rpisaluter", rpisaluter_callback)

# A welcome message callback
def rpisaluter_callback(client, userdata, msg):
    print('Welcome to Humify! Press button to start recording.')

# Default Message Callback
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

if __name__ == '__main__':
    # Set up default callback and on connect call
    local_client.on_message = on_message
    local_client.on_connect = on_connect
    # Connect to broker
    local_client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    # Create separate thread to handle incoming and outgoing messages
    local_client.loop_start()

    local_client.publish('ramsesma/salutator', ' ') # Just to signal welcome

    while (True):
        time.sleep(1)