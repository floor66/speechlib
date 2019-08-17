import speech_recognition as sr
import wave as wav
from os import path, rename
import struct
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "samples/trump_1_min.wav")
SILENCE_THRESHOLD = 1000
MIN_SILENCE_LEN = 2000
MIN_PHRASE_LEN = 2000
DRAW = True
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
        fig = plt.figure()
        ax = fig.add_subplot(111)
        #t = np.linspace(0, len(signal) / src.getframerate(), num=len(signal))
        ax.plot(abs(signal))
        ax.axhline(SILENCE_THRESHOLD, color="black", linestyle="dashed")
        ax.axhline(-SILENCE_THRESHOLD, color="black", linestyle="dashed")

    # phrase = end of prev silence - half of prev silence to start of next silence + half of next silence
    phrases = []
    prev_silence = (0, 0, 0) # start, end, length
    for start, end, length in silences:
        phrases.append((prev_silence[1] - (prev_silence[2] // 2), start + (length // 2)))

        #if DRAW:
        #    ax.axvspan(start, end, color="black", alpha=0.25)
        
        prev_silence = (start, end, length)

    print(len(phrases), "phrases")
    i = 0
    for start, end in phrases:
        i += 1

        if (end - start) < MIN_PHRASE_LEN:
            continue

        if DRAW:
            ax.axvline(start, color="black")
            ax.axvline(end, color="black")
            ax.axvspan(start, end, color="red", alpha=0.25)
            ax.text(start, 1, str(i))
        
        if EXPORT:
            OUT_FILE = "samples/out/1min/%i/phrase-%i-%i_%i.wav" % (SILENCE_THRESHOLD, i, start, end)

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
                    s = r.recognize_google(audio)
                    print("phrase_%i: %s" % (i, s))
                    rename(OUT_FILE, OUT_FILE.replace(".wav", "_%s.wav" % s))
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
        ax.set_xlabel("Time (s)")
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: "%.2f" % (float(x) / 44100.0)))
        plt.show()


