import speech_recognition as sr
import wave as wav
from os import path, rename
import struct
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "samples/trump_1.wav")
OUT_FILE = "samples/out/full/phrase-{0}-{1}_{2}.wav"

SILENCE_THRESHOLD = 500
DELTA_THRESHOLD = 100
WINDOW_SIZE = 10000
MIN_SILENCE_LEN = 2000
MIN_PHRASE_LEN = 10000
DRAW = True
EXPORT = True
RECOGNIZE = True

# Detect silences in audio
with wav.open(AUDIO_FILE, "rb") as src:
    signal = src.readframes(-1)
    signal = np.fromstring(signal, "Int16")
    phrases = []
    means = []
    deltas = []

    if DRAW:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        #t = np.linspace(0, len(signal) / src.getframerate(), num=len(signal))
        ax.plot(abs(signal))

    prev_wnd = None
    phrase_start = None
    j = 1
    i = 0
    while i < len(signal):
        curr_wnd = abs(signal[i:i+WINDOW_SIZE])

        if prev_wnd is not None:
            delta = np.mean(curr_wnd) - np.mean(prev_wnd)

            # High delta -> start of word
            # Low delta (-) -> end of word
            if delta > DELTA_THRESHOLD and phrase_start is None:
                phrase_start = i-WINDOW_SIZE
            elif delta > DELTA_THRESHOLD and phrase_start is not None and curr_wnd[-1] > SILENCE_THRESHOLD:
                if i - phrase_start > MIN_PHRASE_LEN:
                    phrases.append((phrase_start, i-WINDOW_SIZE))
                    phrase_start = i-WINDOW_SIZE

            deltas.append((i, i+WINDOW_SIZE, delta))
            means.append((i, i+WINDOW_SIZE, np.mean(curr_wnd)))

        prev_wnd = curr_wnd
        i += WINDOW_SIZE
        j += 1

    if DRAW:
        ax2 = ax.twinx()
        ax2.plot([start + ((end - start) // 2) for start, end, _ in means], [mean for _, _, mean in means], color="red")

    print(len(phrases), "phrases")
    i = 0
    for start, end in phrases:
        i += 1

        if DRAW:
            ax.axvline(start, color="black")
            ax.axvline(end, color="grey")
            ax.axvspan(start, end, color="red", alpha=0.25)
            ax.text(start, 1, str(i))
        
        if EXPORT:
            _OUT_FILE = OUT_FILE.format(i, start, end)

            with wav.open(_OUT_FILE, "w") as out:
                out.setnchannels(1)
                out.setsampwidth(2)
                out.setframerate(44100.0)

                for j in range(start, end):
                    data = struct.pack("<h", signal[j])
                    out.writeframesraw(data)

            if RECOGNIZE:
                # use the audio file as the audio source
                r = sr.Recognizer()
                with sr.AudioFile(_OUT_FILE) as source:
                    audio = r.record(source)  # read the entire audio file

                # # recognize speech using Google Speech Recognition
                try:
                    s = r.recognize_google(audio)
                    print("phrase_%i: %s" % (i, s))
                    rename(_OUT_FILE, _OUT_FILE.replace(".wav", "_%s.wav" % s))
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


