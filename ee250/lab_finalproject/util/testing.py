import sounddevice as sd
from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate
import os

# Read and store all base sounds
base_audios = []

for base_file in os.listdir('../audios/base_hum_songs'):
    if base_file[0] != '.':
        print("\n\n++++++++ TESTING BASE: " + base_file + "++++++++++\n\n")

        samplerate, base_sound = wavfile.read('./audios/base_audios/' + base_file)

        lenght = base_sound.shape[0]/samplerate
        time = np.linspace(0., lenght, base_sound.shape[0])

        plt.plot(time, base_sound)
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude")
        # plt.show()

        base_band = base_file.split('_')[0]

        correlations = []

        for test_file in os.listdir('../audios/test_audios'):

            test_band = test_file.split('_')[0]

            if test_band == test_band:
            
                print("------- TESTING TEST: " + test_file + '\n')

                samplerate, test_sound = wavfile.read('../audios/test_audios/' + test_file)

                plt.plot(time, test_sound)
                plt.xlabel("Time [s]")
                plt.ylabel("Amplitude")
                # plt.show()

                corr = correlate(base_sound, test_sound, mode='same')

                #Plotting of Correlation
                plt.plot(time, corr)
                plt.title('Correlation ' + base_band + ' v.s ' + test_file)
                plt.xlabel('Time')
                plt.ylabel('Amplitude')
                plt.show()
    
                # Peak of correlation (point in the correlation vector where the waves are the most similar)
                
                peak = max(corr) 
                correlations.append(peak)
                print("Correlation Max: " + str(peak))

        print('\n' + str(correlations) + '\n\n')


"""

base = 4

for type in ('good','bad'):

    print('------------ testing type: ' + type)

    for i in range(1,3):
        filename = './audios/test' + type + str(base) + '_' + str(i) + '.wav'

        samplerate_in, incoming_sound = wavfile.read(filename)
        lenght_in = incoming_sound.shape[0]/samplerate_in
        time_in = np.linspace(0., lenght_in, incoming_sound.shape[0])

        corr = correlate(original_sound, incoming_sound, mode='full')

        peak = max(corr)
        print("Correlation Max: " + str(peak))

# Plotting of Base Sounds
plt.plot(time, original_sound)
plt.legend()
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
#plt.show()

#Plotting of Incoming Sounds
plt.plot(time_in, incoming_sound)
plt.legend()
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
#plt.show()

corr = correlate(original_sound, incoming_sound, mode='same')

plt.plot(time_og, corr)
plt.title('Overview')
plt.xlabel('Time')
plt.ylabel('Amplitude')
#plt.show()
corr_sum = np.sum(corr)
print("Correlation Sum:" + str(corr_sum))

# Find peak
peak = max(corr)
print("Correlation Max: " + str(peak))
# np.set_printoptions(threshold=sys.maxsize)
# print(corr)


# original_sound = AudioSegment.from_wav('d:/Documents/UC3M/Curso 5/USC/Fall Semester/EE 250L - IoT/Labs/Final Project/Tap Commands/command1.wav')
# og_sound_array = original_sound.get_array_of_samples()

"""
