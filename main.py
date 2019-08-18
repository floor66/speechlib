from os import path
import matplotlib.pyplot as plt
from speechlib import Settings, SpeechLib

settings = Settings()
settings.AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "samples/trump_1_min.wav")
settings.SILENCE_THRESHOLD = 300
settings.DELTA_THRESHOLD = 200
settings.WINDOW_SIZE = 7500
settings.MIN_SILENCE_LEN = 2000
settings.MIN_FRAGMENT_LEN = 10000
settings.RECOGNIZE = False

main = SpeechLib(settings)
main.settings.OUT_DIR = path.join(path.dirname(path.realpath(__file__)), "samples/out/%s/" % main.generate_runid())

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(abs(main.src_fragment.signal))

fragments, silences = main.fragments_by_silence(main.src_fragment)

for i, s in enumerate(silences):
    ax.axvline(s.start_frame, color="black", linestyle="dashed")
    ax.axvline(s.end_frame, color="grey", linestyle="dashed")
    ax.text(s.start_frame, 0, str(i))

fragments, windows = main.fragments_by_delta(fragments)

for i, f in enumerate(fragments):
    ax.axvline(f.start_frame, color="black")
    ax.axvline(f.end_frame, color="grey")
    ax.axvspan(f.start_frame, f.end_frame, color="red", alpha=0.2)
    ax.text(f.start_frame, -250, str(i))

# Windows/means
ax.plot([w.start_frame + (w.size // 2) for w in windows], [w.mean for w in windows], color="red")
[ax.axvline(w.start_frame, color="black", alpha=0.1) for w in windows]
[ax.text(w.start_frame + (w.size // 2), -500, str(int(w.mean))) for w in windows]

plt.show()

"""
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
"""