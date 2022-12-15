EE 250L Final Project: Humify!

Code by: 
    - Ramses Maurice, Contreras Sulbaran

Git Hub Links:
https://github.com/ramsescs/ee250-finalproject
git@github.com:ramsescs/ee250-finalproject.git

Google Drive Link to Demo:
--->

Description of Project
----------------------

Sometimes we can't get a song out of out head, but we don't remember the lyrics, we just remember the melody and we can't stop humming it! That's why I decided to create Humify!

Humify! is a "hum" recognizing app designed for RPi's, it is able to recognize songs from just hearing the "hummed" version of it, just like Shazam would with the original recording of the song.

How does it work?

Run the app, wait for the blue screen and "press the button" message, press it and Humify! will start recording your humming. After 10 seconds of recording, Humify! will analyze the sound signal provided in time domain, being able to represent the sound wave's amplitude over time, this way it can recognize the humming pattern in the "hummed" songs it has stored in the database (./audio/base_hum_songs folder)

There are 2 designs I choose for this program: Paradigm 1 & Paradigm 2. The first one was the one I decided to begin with to give the RPi more responsabilities. In it the RPi is in charge of both analyzing the wave and displaying the result, along with sending the signal to start the recording. The second one, I decided to make it as it would make more sense to me in a real life scenario, where the recorded sound signal is sent to a server (in this case my VM), where the signal is analyzed to match it with thousands or millions (but just 5 in my case) of songs. Once a match is found, or not, the result is sent to the RPi to be displayed.

I would recommend to run "Paradigm 2" instead, because as I said I think it has more sense in a real life scenario, and even more, if I the RPi had a microphone, since then it would record directly from the RPi and then send the recording to the server, instead of just sending a signal to start the recording in another device with microphone.

Instructions
------------

1. Run the "rpi ... .py" files in the RPi and the "vm ... .py" files in a different device.
2. Once they're connected (signaled by a welcome message), press the button and start humming.
3. After 10 seconds, the recording stops and its analyzed. A beep will indicate the end of the analysis and the results will be shown. A green screen indicated there was a match, and the song matched will be shown. A red screen indicated there was no match.
