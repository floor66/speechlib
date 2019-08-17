import speech_recognition as sr
import wave as wav
from os import path, rename, makedirs
import struct
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
from hashlib import md5

AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "samples/trump_1.wav")

SILENCE_THRESHOLD = 300
DELTA_THRESHOLD = 200
WINDOW_SIZE = 7500
MIN_SILENCE_LEN = 2000
MIN_FRAGMENT_LEN = 10000
DRAW = True
EXPORT = True
RECOGNIZE = True

RUN_ID = md5(("%s+%s+%s+%s+%s+%s" % (AUDIO_FILE, str(SILENCE_THRESHOLD), str(DELTA_THRESHOLD), str(WINDOW_SIZE), str(MIN_SILENCE_LEN), str(MIN_FRAGMENT_LEN))).encode()).hexdigest()
OUT_DIR = path.join(path.dirname(path.realpath(__file__)), "samples/out/%s/" % RUN_ID)

if EXPORT and not path.exists(OUT_DIR):
    makedirs(OUT_DIR)

# Detect silences in audio
with wav.open(AUDIO_FILE, "rb") as src:
    signal = src.readframes(-1)
    signal = np.fromstring(signal, "Int16")
    fragments = []
    means = []
    deltas = []

    if DRAW:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        #t = np.linspace(0, len(signal) / src.getframerate(), num=len(signal))
        ax.plot(abs(signal))

    prev_wnd = None
    fragment_start = None
    j = 1
    i = 0
    while i < len(signal):
        curr_wnd = abs(signal[i:i+WINDOW_SIZE])

        if prev_wnd is not None:
            delta = np.mean(curr_wnd) - np.mean(prev_wnd)

            # High delta -> start of word?
            # Low delta (-) -> end of word?
            if delta > DELTA_THRESHOLD and fragment_start is None:
                fragment_start = i-WINDOW_SIZE
            elif delta > DELTA_THRESHOLD and fragment_start is not None and np.mean(curr_wnd) > SILENCE_THRESHOLD:
                if i - fragment_start > MIN_FRAGMENT_LEN:
                    fragments.append((fragment_start, i-WINDOW_SIZE))
                    fragment_start = i-WINDOW_SIZE

            deltas.append((i, i+WINDOW_SIZE, delta))
            ax.text(i, 1, str(int(delta)))
            means.append((i, i+WINDOW_SIZE, np.mean(curr_wnd)))

        prev_wnd = curr_wnd
        i += WINDOW_SIZE
        j += 1

    if DRAW:
        ax2 = ax.twinx()
        ax2.plot([start + ((end - start) // 2) for start, end, _ in means], [mean for _, _, mean in means], color="red")

    print(len(fragments), "fragments")
    exports = []
    i = 0
    for start, end in fragments:
        i += 1

        if DRAW:
            ax.axvline(start, color="black")
            ax.axvline(end, color="grey")
            ax.axvspan(start, end, color="red", alpha=0.25)
            ax.text(start, 1, str(i))
        
        if EXPORT:
            OUT_FILE = path.join(OUT_DIR, "fragment-%s.wav" % i)

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

                # recognize speech using Google Speech Recognition
                s = ""
                try:
                    s = r.recognize_google(audio)
                except sr.UnknownValueError:
                    pass
                    #print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    pass
                    #print("Could not request results from Google Speech Recognition service; {0}".format(e))
                except Exception as e:
                    pass
                    #print(e)

                fragment_id = md5(("%s+%s+%s+%s" % (AUDIO_FILE, str(start), str(end), s)).encode()).hexdigest()
                exports.append((fragment_id, AUDIO_FILE, OUT_FILE, i, start, end, s))


    # CSV file with
    # Variables: AUDIO_FILE, SILENCE_THRESHOLD, DELTA_THRESHOLD, WINDOW_SIZE, MIN_SILENCE_LEN, MIN_fragment_LEN
    # Headers: fragment_id, src_file, export_file, fragment_no, start_frame, end_frame, google_speech_result
    if RECOGNIZE:
        OUT_FILE = "result_%s.txt" % RUN_ID
        headers = ["fragment_id", "src_file", "export_file", "fragment_no", "start_frame", "end_frame", "google_speech_result"]

        with open(path.join(OUT_DIR, OUT_FILE), "w") as out:
            out.write("# speechlib v0.1 output file\n\n")
            out.write("# variables used:\n")
            out.write("AUDIO_FILE;SILENCE_THRESHOLD;DELTA_THRESHOLD;WINDOW_SIZE;MIN_SILENCE_LEN;MIN_fragment_LEN\n")
            out.write("%s\n\n" % ";".join([AUDIO_FILE, str(SILENCE_THRESHOLD), str(DELTA_THRESHOLD), str(WINDOW_SIZE), str(MIN_SILENCE_LEN), str(MIN_FRAGMENT_LEN)]))
            out.write("# fragments detected:\n")
            out.write("%s\n" % ";".join(headers))
            for export in exports:
                out.write("%s\n" % ";".join([str(s) for s in export]))

    if DRAW:
        ax.set_xlabel("Time (s)")
        #ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: "%.2f" % (float(x) / 44100.0)))
        plt.show()
