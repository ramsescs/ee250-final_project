""" 
EE 250L Final Project: Humify!

Code by: 
    - Ramses Maurice, Contreras Sulbaran

https://github.com/ramsescs/ee250-finalproject
git@github.com:ramsescs/ee250-finalproject.git

Paradigm 2
==========
This file is part of paradigm 2, where the VM will be the recognizer.

VM Recognizer/Player
--------------------
Description: This is the file to be executed in the VM/Other machine. It received a request from the RPI to start
the recording, and once it is done recording, it will be analyzed here to find a match with one of the songs in DB. 
The result of the sound signal analysis will be then sent to the RPi to be displayed.

"""

import sounddevice as sd
import threading
import paho.mqtt.client as mqtt
import time
import simpleaudio
from scipy.signal import correlate
from scipy.io import wavfile
import os
import matplotlib.pyplot as plt

lock = threading.Lock()

# Recording Parameters
fs = 44100  # Sample rate
duration = 10  # Duration of recording

# Global variables/constants
local_client = mqtt.Client()
base_dict = {}
COR_THRESHOLD = 300
play_object = None

# Custom callback for the recognizer topic (once button is clicked)
def recognizer_callback(client, userdata, msg):

    content = str(msg.payload, "utf-8")

    local_client.publish("ramsesma/signal_rec", "ON")

    if content == 'REC':
    
        # Lock to allow only one request at a time
        with lock:

            # Record incoming sound

            print('Init Recording')

            incoming_sound = sd.rec(
                int(duration * fs), samplerate=fs, channels=1)
            sd.wait()  # Wait until recording is finished

            print('Done Recording')

            local_client.publish("ramsesma/signal_rec", "OFF")

            print('Humify is busy recognizing!')

            # Compare the new incoming sound with all the sounds stored
            match_song = 'no_match'
            match_peak = 0

            for base_song in base_dict:
                
                print('Checking match with: ' + base_song)

                base_audio = base_dict[base_song]

                corr = correlate(base_audio, incoming_sound[:,0], mode='same')

                # Plotting of Correlation
                # plt.plot(time, corr)
                # plt.title('Overview')
                # plt.xlabel('Time')
                # plt.ylabel('Amplitude')
                # plt.show()

                # Peak of correlation (point in the correlation vector where the waves are the most similar)
                peak = max(corr)

                print('Peak correlation: ' + str(peak) + '\n')

                if peak > match_peak and peak > COR_THRESHOLD:
                    match_song = base_song
                    match_peak = peak

            # Execution of commands depending on the sound matched, if any
            print('Recognition done!')

            local_client.publish("ramsesma/displayer", match_song)

            if(match_song != 'no_match'):
                print('Match found: ' + match_song)
                
            else:
                print('No match found. Try again!')

    else:
        print("Error in REC format!")

# Setup once conneciton to broker is succesful
def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    # subscribing to topics of interest
    # and setting up custom callbacks
    client.subscribe("ramsesma/recognizer")
    client.message_callback_add("ramsesma/recognizer", recognizer_callback)

    client.subscribe('ramsesma/rpisaluter')
    client.message_callback_add("ramsesma/rpisaluter", rpisaluter_callback)

# A welcome message callback
def rpisaluter_callback(client, userdata, msg):
    print('Welcome to Humify! Press button to start recording.')

# Default Message Callback
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))


if __name__ == '__main__':

    for file in os.listdir('./audios/base_hum_songs'):
        if file[0] != '.':
            samplerate, base_audio = wavfile.read(
                './audios/base_hum_songs/' + file)

            base_song = file.split('_hum')[0]

            base_dict[base_song] = base_audio

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