from fragment import Fragment, Window
from hashlib import md5
import numpy as np

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

    def fragments_by_delta(self, from_fragment):
        if len(from_fragment.signal) < self.settings.WINDOW_SIZE:
            raise IndexError("Can't process fragment: WINDOW_SIZE is greater than the fragment length")

        if len(from_fragment.signal) < self.settings.MIN_FRAGMENT_LEN:
            raise IndexError("Can't process fragment: MIN_FRAGMENT_LEN is greater than the fragment length")

        fragments_found = []
        windows = []

        prev_wnd = None
        fragment_start = None
        i = 0
        while i < len(from_fragment.signal):
            curr_wnd = abs(from_fragment.signal[i:i+self.settings.WINDOW_SIZE])

            if prev_wnd is not None:
                delta = np.mean(curr_wnd) - np.mean(prev_wnd)

                if delta > self.settings.DELTA_THRESHOLD and fragment_start is None:
                    fragment_start = i-self.settings.WINDOW_SIZE
                elif delta > self.settings.DELTA_THRESHOLD and fragment_start is not None and np.mean(curr_wnd) > self.settings.SILENCE_THRESHOLD:
                    if i - fragment_start > self.settings.MIN_FRAGMENT_LEN:
                        fragments_found.append(Fragment(from_fragment, fragment_start, i-self.settings.WINDOW_SIZE))
                        fragment_start = i-self.settings.WINDOW_SIZE

                windows.append(Window(i, i+self.settings.WINDOW_SIZE, delta, np.mean(curr_wnd)))

            prev_wnd = curr_wnd
            i += self.settings.WINDOW_SIZE

        return fragments_found, windows