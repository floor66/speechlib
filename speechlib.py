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
        if from_fragment.window.size < self.settings.WINDOW_SIZE:
            raise IndexError("Can't process fragment: WINDOW_SIZE is greater than the fragment length")

        if from_fragment.window.size < self.settings.MIN_FRAGMENT_LEN:
            raise IndexError("Can't process fragment: MIN_FRAGMENT_LEN is greater than the fragment length")

        fragments_found = []
        windows = []

        prev_wnd = None
        fragment_start = None
        i = 0
        while i < from_fragment.window.size:
            i_offset = i + from_fragment.window.start_frame
            curr_wnd = abs(from_fragment.signal[i_offset:i_offset+self.settings.WINDOW_SIZE])

            if prev_wnd is not None:
                delta = np.mean(curr_wnd) - np.mean(prev_wnd)

                if delta > self.settings.DELTA_THRESHOLD and fragment_start is None:
                    fragment_start = i_offset-self.settings.WINDOW_SIZE
                elif delta > self.settings.DELTA_THRESHOLD and fragment_start is not None and np.mean(curr_wnd) > self.settings.SILENCE_THRESHOLD:
                    if i_offset - fragment_start > self.settings.MIN_FRAGMENT_LEN:
                        fragments_found.append(Fragment(from_fragment, fragment_start, i_offset-self.settings.WINDOW_SIZE))
                        fragment_start = i_offset-self.settings.WINDOW_SIZE

                windows.append(Window(i_offset, i_offset+self.settings.WINDOW_SIZE, delta, np.mean(curr_wnd)))

            prev_wnd = curr_wnd
            i += self.settings.WINDOW_SIZE

        return fragments_found, windows

    def fragments_by_silence(self, from_fragment):
        if from_fragment.window.size < self.settings.SILENCE_THRESHOLD:
            raise IndexError("Can't process fragment: SILENCE_THRESHOLD is greater than the fragment length")

        silences = []
        silence_start = None
        for i in range(from_fragment.window.size):
            i_offset = i + from_fragment.window.start_frame
            if abs(from_fragment.signal[i_offset]) <= self.settings.SILENCE_THRESHOLD:
                if silence_start is None:
                    silence_start = i_offset
            elif silence_start is not None:
                if (i_offset - silence_start) > self.settings.MIN_SILENCE_LEN:
                    silences.append(Window(silence_start, i_offset))

                silence_start = None

        # Fragments start halfway prev silence and end halfway curr silence
        fragments_found = [Fragment(from_fragment, silences[i - 1].start_frame - (silences[i - 1].size // 4), silences[i].start_frame + (silences[i].size // 4)) for i in range(1, len(silences))]
        return fragments_found, silences