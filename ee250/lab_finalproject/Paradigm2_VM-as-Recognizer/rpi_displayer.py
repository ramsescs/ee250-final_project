""" 
EE 250L Final Project: Humify!

Code by: 
    - Ramses Maurice, Contreras Sulbaran

https://github.com/ramsescs/ee250-finalproject
git@github.com:ramsescs/ee250-finalproject.git

Paradigm 2
==========
This file is part of paradigm 2, where the VM will be the recognizer.

RPI Request/Displayer
---------------------
Description: This is the file to be executed in the RPi, it sends a request to the other instance of execution
(VM/Server/Other Physical Machine), to start the recording (since I don't have a microphone compatible with the RPI)
& analyze it to match it with a song in DB. The span of the recording will be signaled by the red LED.

Once a match is found, it will be signaled by the buzzer & the result is sent here to be displayed in the LCD screen.

"""

import threading
import paho.mqtt.client as mqtt
import time
import sys

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
led_lock = threading.Lock()

# Current matched song
match_song = ''
# This controls requests to be sent one at a time
recognizer_ready = 1

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
    client.subscribe("ramsesma/signal_rec")
    client.message_callback_add("ramsesma/signal_rec", signal_rec_callback)
    client.subscribe("ramsesma/displayer")
    client.message_callback_add("ramsesma/displayer", displayer_callback)
    client.subscribe('ramsesma/salutator')
    client.message_callback_add("ramsesma/salutator", salutator_callback)

# Signals recording in progress, when VM indicates so
def signal_rec_callback(client, userdata, msg):
    print('SIGNAL REC RECEIVED')
    content = str(msg.payload, "utf-8")

    print('Waiting for lock LED')
    with led_lock:
        if content == 'ON':
            print('turning LED ON')
            grovepi.digitalWrite(PORT_RED_LED, 1)
        elif content == 'OFF':
            print('turning LED OFF')
            grovepi.digitalWrite(PORT_RED_LED, 0)
        else:
            print("Error in Singal REC format!")

# Signals match with buzzer and sets match_song variable 
# so the song is displayed in LCD, once VM sends match
def displayer_callback(client, userdata, msg):

    content = str(msg.payload, "utf-8")
    grovepi.digitalWrite(PORT_BUZZER, 1)
    grovepi.digitalWrite(PORT_BUZZER, 0)

    with lock:
        global match_song
        match_song = content

        global recognizer_ready
        recognizer_ready = 1        

# A welcome message callback
def salutator_callback(client, userdata, msg):
    local_client.publish('ramsesma/rpisaluter', ' ') # This is just to signal VM
    print('Welcome to Humify! Press button to start recording.')

# Default message callback.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))


if __name__ == '__main__':

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
            with lock:
                # On button press, start recording
                buttonRead = grovepi.digitalRead(PORT_BUTTON)
                    
                if recognizer_ready and buttonRead:
                    recognizer_ready = 0
                    grovepi.digitalWrite(PORT_RED_LED, 1)
                    local_client.publish("ramsesma/recognizer", "REC")

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
