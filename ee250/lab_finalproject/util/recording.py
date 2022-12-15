import sounddevice as sd
from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt

fs = 44100  # Sample rate
duration = 1  # Duration of recording

print('Init Recording')
incoming_sound = sd.rec(int(duration * fs), samplerate=fs, channels=1)
sd.wait()  # Wait until recording is finished
print('Done Recording')


"""
plt.plot(time, incoming_sound)
plt.title('Overview')
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.show()
corr = correlate(og_sound_array, incoming_sound)
plt.plot(time, corr)
plt.title('Overview')
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.show()

/test_audios/greenday_good_test_4

/base_audios/rhcp_base.wav
"""


wavfile.write('./audios/base_hum_songs/nepe.wav', fs, incoming_sound)  # Save as WAV `file`