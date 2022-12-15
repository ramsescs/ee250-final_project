import sounddevice as sd
from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate
import os
import time

fs = 44100  # Sample rate
duration = 10  # Duration of recording
period = 1/fs


print('Init Recording - Test')
incoming_sound = sd.rec(int(duration * fs), samplerate=fs, channels=1)
sd.wait()  # Wait until recording is finished
print('Done Recording - Test')

time.sleep(3)
# samplerate, incoming_sound = wavfile.read('./audios/base_buzzer/long.wav')

# Compare the new incoming sound with all the sounds stored
partial_match = 'no_match'
match_peak = 0
time = np.arange(0, duration, period)

base_dict = {}

for file in os.listdir('./audios/base_whistle_commands'):
    if file[0] != '.':

        samplerate, base_audio = wavfile.read('./audios/base_whistle_commands/' + file)

        base_artist = file.split('_')[0]

        base_dict[base_artist] = base_audio

base_dict['asdsa'] = 'popo'
base_dict['ASA'] = 'popo'

for base_artist in base_dict:

    base_audio = base_dict[base_artist]

    print('Init Recording - Base')
    base_audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    print('Done Recording - Base')

    plt.plot(time, base_audio)
    plt.title('Base Audio: ' + base_artist)
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.show()

    plt.plot(time, incoming_sound)
    plt.title('Incoming Audio')
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.show()

    corr = correlate(base_audio[:,0], incoming_sound[:,0], mode='same')

    # Plotting of Correlation
    plt.plot(time, corr)
    plt.title('Correlation with: ' + base_artist)
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.show()

    # Peak of correlation (point in the correlation vector where the waves are the most similar)
    peak = max(corr)

    print(base_artist)
    print(peak)

    if peak > match_peak and peak > 90:
        partial_match = base_artist
        match_peak = peak

print(partial_match)
