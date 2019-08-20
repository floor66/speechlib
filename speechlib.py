from fragment import Fragment, Window
from hashlib import md5
import numpy as np
import time

microtime = lambda: int(round(time.time() * 1000))

class Settings():
    def __init__(self):
        return

class SpeechLib():
    def __init__(self, settings):
        self.settings = settings
        self.src_fragment = Fragment(self.settings.AUDIO_FILE)

    def generate_runid(self):
        return md5(("%s+%s+%s+%s+%s+%s" % (self.settings.AUDIO_FILE, str(self.settings.SILENCE_THRESHOLD),
         str(self.settings.DELTA_THRESHOLD), str(self.settings.WINDOW_SIZE),
         str(self.settings.MIN_SILENCE_LEN), str(self.settings.MIN_FRAGMENT_LEN))).encode()).hexdigest()

    def extract_windows(self, from_fragment, WINDOW_SIZE=None):
        WINDOW_SIZE = self.settings.WINDOW_SIZE if WINDOW_SIZE is None else WINDOW_SIZE

        if len(from_fragment) < WINDOW_SIZE:
            raise IndexError("Can't process fragment: WINDOW_SIZE is greater than the fragment length")

        return [Window(
                from_fragment.window.start_frame + (i * WINDOW_SIZE),
                from_fragment.window.start_frame + ((i + 1) * WINDOW_SIZE),
                np.mean(
                    abs(from_fragment.src_audio_signal[from_fragment.window.start_frame + (i * WINDOW_SIZE):from_fragment.window.start_frame + ((i + 1) * WINDOW_SIZE)])
                )
            ) for i in range(len(from_fragment) // WINDOW_SIZE)]

    def fragments_by_delta(self, from_fragment):
        if len(from_fragment) < self.settings.MIN_FRAGMENT_LEN:
            raise IndexError("Can't process fragment: MIN_FRAGMENT_LEN is greater than the fragment length")

        fragments_found = []
        windows = self.extract_windows(from_fragment)

        fragment_start = None
        for i in range(len(windows)):
            windows[i].delta = windows[i].mean - windows[i - 1].mean if i > 0 else windows[i].mean

            if windows[i].delta > self.settings.DELTA_THRESHOLD and fragment_start is None:
                fragment_start = windows[i].start_frame
            elif windows[i].delta > self.settings.DELTA_THRESHOLD and fragment_start is not None and windows[i].mean > self.settings.SILENCE_THRESHOLD:
                if windows[i].start_frame - fragment_start >= self.settings.MIN_FRAGMENT_LEN:
                    fragments_found.append(Fragment(from_fragment, fragment_start, windows[i].start_frame))
                    fragment_start = windows[i].start_frame

        if fragment_start is not None:
            fragments_found.append(Fragment(from_fragment, fragment_start, from_fragment.window.end_frame))

        return fragments_found, windows

    def fragments_by_silence(self, from_fragment, SILENCE_THRESHOLD=None):
        if len(from_fragment) < self.settings.MIN_SILENCE_LEN:
            raise IndexError("Can't process fragment: MIN_SILENCE_LEN is greater than the fragment length")

        SILENCE_THRESHOLD = self.settings.SILENCE_THRESHOLD if SILENCE_THRESHOLD is None else SILENCE_THRESHOLD

        silences = []
        windows = self.extract_windows(from_fragment, WINDOW_SIZE=1000)
        silence_start = None
        for i in range(len(windows)):
            if windows[i].mean <= SILENCE_THRESHOLD:
                if silence_start is None:
                    silence_start = windows[i].start_frame
            elif silence_start is not None:
                if (windows[i].start_frame - silence_start) >= self.settings.MIN_SILENCE_LEN:
                    silences.append(Window(silence_start, windows[i].start_frame))

                silence_start = None

        # for i in range(len(from_fragment)):
        #     i_offset = i + from_fragment.window.start_frame
        #     if abs(from_fragment.src_audio_signal[i_offset]) <= SILENCE_THRESHOLD:
        #         if silence_start is None:
        #             silence_start = i_offset
        #     elif silence_start is not None:
        #         if (i_offset - silence_start) >= self.settings.MIN_SILENCE_LEN:
        #             silences.append(Window(silence_start, i_offset))

        #         silence_start = None

        # Fragments start 3/4 prev silence and end 1/4 curr silence
        fragments_found = [Fragment(from_fragment, silences[i - 1].end_frame - (len(silences[i - 1]) // 4), silences[i].start_frame + (len(silences[i]) // 4)) for i in range(1, len(silences))]
        return fragments_found, silences