import speech_recognition as sr
import wave as wav
from os import path
import struct
import matplotlib.pyplot as plt
import numpy as np

AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "samples/trump_1_min.wav")
THRESHOLD = 500

with wav.open(AUDIO_FILE, "rb") as src:
    signal = src.readframes(-1)
    signal = np.fromstring(signal, "Int16")

    words = []
    word = []
    for i in range(len(signal)):
        if abs(signal[i]) > THRESHOLD:
            word.append(signal[i])
        else:
            word = []

    print(words)

    t = np.linspace(0, len(signal) / src.getframerate(), num=len(signal))
    plt.plot(words[0])
    plt.axhline(THRESHOLD, color="black")
    plt.axhline(-THRESHOLD, color="black")
    plt.show()

# # use the audio file as the audio source
# r = sr.Recognizer()
# with sr.AudioFile(AUDIO_FILE) as source:
#     audio = r.record(source)  # read the entire audio file

# print(audio)

# # # recognize speech using Google Speech Recognition
# try:
#     # for testing purposes, we're just using the default API key
#     # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
#     # instead of `r.recognize_google(audio)`
#     print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
# except sr.UnknownValueError:
#     print("Google Speech Recognition could not understand audio")
# except sr.RequestError as e:
#     print("Could not request results from Google Speech Recognition service; {0}".format(e))

