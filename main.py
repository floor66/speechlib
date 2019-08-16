import speech_recognition as sr
import wave as wav
from os import path
import struct
import matplotlib.pyplot as plt
import numpy as np

AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "samples/trump_1.wav")
SILENCE_THRESHOLD = 1000
MIN_SILENCE_LEN = 2000
MIN_PHRASE_LEN = 2000
DRAW = False
EXPORT = True
RECOGNIZE = True

# Detect silences in audio
with wav.open(AUDIO_FILE, "rb") as src:
    signal = src.readframes(-1)
    signal = np.fromstring(signal, "Int16")

    silences = []
    silence_start = None
    for i in range(len(signal)):
        if abs(signal[i]) <= SILENCE_THRESHOLD: # there is silence
            if silence_start is None: # we are not recording
                    silence_start = i # start "recording" this silence
        elif silence_start is not None: # there is sound, stop recording current silence?
            if (i - silence_start) > MIN_SILENCE_LEN: # was this silence long enough?
                silences.append((silence_start, i, i - silence_start))

            silence_start = None

    if DRAW:
        #plt.plot([pow(s, 2) for s in signal])
        #t = np.linspace(0, len(signal) / src.getframerate(), num=len(signal))
        plt.plot(signal)
        plt.axhline(SILENCE_THRESHOLD, color="black", linestyle="dashed")
        plt.axhline(-SILENCE_THRESHOLD, color="black", linestyle="dashed")

    # phrase = end of prev silence - half of prev silence to start of next silence + half of next silence
    phrases = []
    prev_silence = (0, 0, 0) # start, end, length
    for start, end, length in silences:
        phrases.append((prev_silence[1] - (prev_silence[2] // 2), start + (length // 2)))

        #if DRAW:
        #    plt.axvspan(start, end, color="black", alpha=0.25)
        
        prev_silence = (start, end, length)

    print(len(phrases), "phrases")
    i = 0
    for start, end in phrases:
        i += 1

        if (end - start) < MIN_PHRASE_LEN:
            continue

        if DRAW:
            plt.axvline(start, color="black")
            plt.axvline(end, color="black")
            plt.axvspan(start, end, color="red", alpha=0.25)
            plt.text(start, 1, str(i))
        
        if EXPORT:
            OUT_FILE = "samples/out/full/%i/phrase-%i-%i_%i.wav" % (SILENCE_THRESHOLD, i, start, end)

            with wav.open(OUT_FILE, "w") as out:
                out.setnchannels(1)
                out.setsampwidth(2)
                out.setframerate(44100.0)

                for j in range(start, end):
                    data = struct.pack("<h", signal[j])
                    out.writeframesraw(data)

            if RECOGNIZE:
                # use the audio file as the audio source
                r = sr.Recognizer()
                with sr.AudioFile(OUT_FILE) as source:
                    audio = r.record(source)  # read the entire audio file

                # # recognize speech using Google Speech Recognition
                try:
                    print("phrase_%i: %s" % (i, r.recognize_google(audio)))
                except sr.UnknownValueError:
                    pass
                    #print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    pass
                    #print("Could not request results from Google Speech Recognition service; {0}".format(e))
                except Exception as e:
                    pass
                    #print(e)

    if DRAW:
        plt.show()


