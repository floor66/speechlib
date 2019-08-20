from os import path
import sys
import matplotlib.pyplot as plt
from speechlib import Settings, SpeechLib, microtime
from fragment import Fragment
import wave

def printf(content):
    sys.stdout.write(content)
    sys.stdout.flush()

DRAW = True
EXPORT = True
RECOGNIZE = True

settings = Settings()
settings.AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "samples/obama.wav")
settings.SILENCE_THRESHOLD = 500
settings.DELTA_THRESHOLD = 200

# In ms, so it works with all framerates
settings.WINDOW_SIZE = 200
settings.MIN_SILENCE_LEN = 300
settings.MIN_FRAGMENT_LEN = 400

main = SpeechLib(settings)
main.settings.OUT_DIR = path.join(path.dirname(path.realpath(__file__)), "samples/out/%s/" % main.generate_runid())

# Clip
min_fragment = Fragment(main.src_fragment, 0, (main.src_fragment.src_freq * 60))

t = microtime()
silence_fragments, silences = main.fragments_by_silence(min_fragment)
print("%i fragments by silence (%i ms)" % (len(silence_fragments), microtime() - t))

t = microtime()
delta_fragments, windows = [], []
for f in silence_fragments:
    if len(f) >= main.settings.MIN_FRAGMENT_LEN:
        _delta_fragments, _windows = main.fragments_by_delta(f)
        delta_fragments += _delta_fragments
        windows += _windows

print("%i fragments by delta (%i ms)" % (len(delta_fragments), microtime() - t))

if EXPORT:
    printf("Exporting... 0/%i\r" % len(delta_fragments))
    #[f.generate_wav(main.settings.OUT_DIR) for f in silence_fragments]
    for i, f in enumerate(delta_fragments):
        printf("Exporting... %i/%i\r" % (i + 1, len(delta_fragments)))
        f.generate_wav(main.settings.OUT_DIR, main.src_fragment.src_freq)
    print("")

if RECOGNIZE:
    printf("Recognizing... 0/%i\r" % len(delta_fragments))
    for i, f in enumerate(delta_fragments):
        f.google_recognize_fragment()

        printf("Recognizing... %i/%i\r" % ((i + 1), len(delta_fragments)))
        with open("res.txt", "a") as res:
            res.write(str(f._id))
            res.write("\t")
            res.write(f.google_recognized_string)
            res.write("\n")
    print("")

if DRAW:
    print("Drawing...")
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(abs(min_fragment.src_audio_signal[min_fragment.window.start_frame:min_fragment.window.end_frame]))

    # Silences
    for i, f in enumerate(silence_fragments):
        ax.plot([i for i in range(f.window.start_frame, f.window.end_frame)], [-140 for i in range(f.window.start_frame, f.window.end_frame)], color="black")
        ax.text(f.window.start_frame, -110, "SF%i" % f._id, color="black")

    for i, s in enumerate(silences):
        ax.plot([i for i in range(s.start_frame, s.end_frame)], [-310 for i in range(s.start_frame, s.end_frame)], color="grey")
        ax.text(s.start_frame, -280, "S%i" % i, color="grey")

    # Deltas/windows/means
    for i, f in enumerate(delta_fragments):
        y = -480 if i % 2 == 0 else -650
        ax.plot([i for i in range(f.window.start_frame, f.window.end_frame)], [y for i in range(f.window.start_frame, f.window.end_frame)], color="red")
        ax.text(f.window.start_frame, y + 30, "DF%i" % f._id, color="red")

    ax.plot([w.start_frame + (len(w) // 2) for w in windows], [w.mean for w in windows], color="red")
    for i, w in enumerate(windows):
        ax.axvline(w.start_frame, color="black", alpha=0.1)
        ax.text(w.start_frame + (len(w) // 2), int(w.mean), "%s (%s%s)" % (str(int(w.mean)), "+" if w.delta >= 0 else "", str(int(w.delta))))

    # wm = plt.get_current_fig_manager()
    # wm.window.state("zoomed")

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