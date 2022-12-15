""" 
EE 250L Final Project: Humify!

Code by: 
    - Ramses Maurice, Contreras Sulbaran

https://github.com/ramsescs/ee250-finalproject
git@github.com:ramsescs/ee250-finalproject.git

Paradigm 1
==========
This file is part of paradigm 1, where the RPi will be the recognizer.

RPI Recognizer
--------------
Description: This is the file to be executed in the RPi, it sends a request to the other instance of execution
(VM/Server/Other Physical Machine), to start the recording (since I don't have a microphone compatible with the RPI).
Once the recording is done, the audio object is pickled and sent here where the RPI unpickles it and analyzes it to
find a match with one of the songs in DB. The result of the song matching will be displayed in the LCD screen.

The span of the recording will be signaled by the red LED. The end of the sound signal analysis will be signaled by
the buzzer.

"""

from scipy.io import wavfile
import threading
import paho.mqtt.client as mqtt
import time
import numpy as np
from scipy.signal import correlate
import matplotlib.pyplot as plt
import os
import sys
import pickle

# By appending the folder of all the GrovePi libraries to the system path here,
# we are successfully `import grovepi`
sys.path.append('../../Software/Python/')
sys.path.append('../../Software/Python/grove_rgb_lcd')

import grove_rgb_lcd as lcd
import grovepi

# GrovePi Port References
PORT_BUTTON = 7 # D4
PORT_BUZZER = 3 # D3
PORT_RED_LED = 8 # D8

# Global variables

# Lock for access restriction
lock = threading.Lock()

# Current matched song
match_song = ''
recognizer_ready = 1
base_dict = {}

LCD_LINE_LEN = 16

COR_THRESHOLD = 300

# Create the mqtt client instance
local_client = mqtt.Client()

# Recording Parameters
fs = 44100  # Sample rate
duration = 5  # Duration of recording
period = 1/fs

# Key: Song, Value: Msg to be printed on LCD
MSG_STORE = {
    'here-comes-the-sun_the-beatles': '  Here Comes the Sun by The Beatles!',
    'el-raton_fania-all-stars': '  El Raton by the Fania All Stars!',
    'la-flaca_jarabe-de-palo': '  La Flaca by Jarabe de Palo!',
    'smoke-on-the-water_deep-purple': '  Smoke on the Water by Deep Purple!',
    'stand-by-me_king': '  Stand by me by Ben E. King!',
    'no_match': '  No Match! Try Again.'
}

# Indicates succesful connection & subscribes to topics
def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    # subscribing to topics of interest
    # and setting up custom callbacks
    client.subscribe("ramsesma/recognizer")
    client.message_callback_add("ramsesma/recognizer", recognizer_callback)

    client.subscribe('ramsesma/salutator')
    client.message_callback_add("ramsesma/salutator", salutator_callback)

# A welcome message callback
def salutator_callback(client, userdata, msg):
    local_client.publish('ramsesma/rpisaluter', ' ') # This is just to signal VM
    print('Welcome to Humify! Press button to start recording.')

# Default message callback.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

# Song recognizer callback
def recognizer_callback(client, userdata, msg):

    grovepi.digitalWrite(PORT_RED_LED, 0)

    global recognizer_ready

    recognizer_ready = 0

    print('Humify is busy recognizing!')

    # incoming_sound = np.fromstring(content)
    incoming_sound = pickle.loads(msg.payload)

    # Compare the new incoming sound with all the sounds stored
    partial_match = 'no_match'
    match_peak = 0
    time = np.arange(0, duration, period)

    for base_song in base_dict:

        base_audio = base_dict[base_song]

        corr = correlate(base_audio, incoming_sound, mode='same')

        # Plotting of Correlation
        #plt.plot(time, corr)
        #plt.title('Overview')
        #plt.xlabel('Time')
        #plt.ylabel('Amplitude')
        # plt.show()

        # Peak of correlation (point in the correlation vector where the waves are the most similar)
        peak = max(corr)

        print(base_song)
        print(peak)

        if peak > match_peak and peak > COR_THRESHOLD:
            partial_match = base_song
            match_peak = peak

    print(partial_match)

    with lock:
        
        global match_song 
        match_song = partial_match
    
    # Execution of commands depending on the sound matched, if any
    # local_client.publish('ramsesma/speaker', match_song)
    print('Recognition done!')
    print('Song is: ' + MSG_STORE[match_song])
    recognizer_ready = 1
    grovepi.digitalWrite(PORT_BUZZER, 1)
    grovepi.digitalWrite(PORT_BUZZER, 0)


if __name__ == '__main__':

    # Read and store all base sounds in a dictionary (key: song name, value: audio)
    for file in os.listdir('./audios/base_hum_songs'):
        if file[0] != '.':
            samplerate, base_audio = wavfile.read(
                './audios/base_hum_songs/' + file)

            base_song = file.split('_hum')[0]

            base_dict[base_song] = base_audio

    # Setup

    # Define port modes
    grovepi.pinMode(PORT_BUZZER, "OUTPUT")
    grovepi.pinMode(PORT_BUTTON, "INPUT")
    grovepi.pinMode(PORT_RED_LED, "OUTPUT")
    # Index for scrolling LCD Screen
    ind = 0
    lcd.setRGB(66, 182, 245)
    # Set up default callback and on connect call
    local_client.on_message = on_message
    local_client.on_connect = on_connect
    # Connect to broker
    local_client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    # Create separate thread to handle incoming and outgoing messages
    local_client.loop_start()

    while True:

        try:
            
            if recognizer_ready:
                with lock:
                    # On button press, start recording
                    buttonRead = grovepi.digitalRead(PORT_BUTTON)

                if buttonRead:
                    grovepi.digitalWrite(PORT_RED_LED, 1)
                    local_client.publish("ramsesma/recorder", "REC")

            if match_song != '':
                with lock:

                    if match_song == 'no_match':
                        lcd.setRGB(207, 43, 10)
                    else:
                        lcd.setRGB(43, 235, 9)

                    lcd.setText_norefresh('Song is:')
                    lcd.setText_norefresh(
                        '\n' + MSG_STORE[match_song][ind:ind+LCD_LINE_LEN])
                    ind = (ind + 1) % len(MSG_STORE[match_song])

            else:
                with lock:
                    lcd.setText_norefresh('Press button\nto start!')

        except KeyboardInterrupt:

            # Gracefully shutdown on Ctrl-C
            lcd.setText('')
            lcd.setRGB(0, 0, 0)

            # Turn buzzer off just in case
            grovepi.digitalWrite(PORT_BUZZER, 0)

            break

        except IOError as ioe:
            if str(ioe) == '121':
                # Retry after LCD error
                time.sleep(0.25)

            else:
                raise
        
        time.sleep(1)
