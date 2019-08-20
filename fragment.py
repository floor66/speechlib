import wave
import numpy as np
from os import path, makedirs
import struct
from hashlib import md5
import speech_recognition as sr

CTR = 0

class Window():
    def __init__(self, start_frame, end_frame, mean = None, delta = 0):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.mean = mean
        self.delta = delta

    def set_delta(self, val):
        self.delta = val

    def __len__(self):
        return 1 + self.end_frame - self.start_frame

    def __repr__(self):
        return "Window(start_frame=%i, end_frame=%i, len=%i, mean=%s, delta=%s)" % (
            self.start_frame, self.end_frame, self.__len__(), str(self.mean), str(self.delta)
            )

class Fragment():
    def __init__(self, source, start_frame = None, end_frame = None):
        global CTR
        self._id = CTR
        CTR += 1

        if type(source) is str:
            self.source = source
            self.src_audio_signal = self.load_wav(source)
            self.audio_file = self.source
            self.window = Window(0, len(self.src_audio_signal) - 1)
        elif type(source) is Fragment:
            self.source = source
            self.audio_file = self.source.audio_file
            self.src_audio_signal = self.source.src_audio_signal
            self.src_freq = self.source.src_freq
            self.window = Window(start_frame if start_frame >= 0 else 0, end_frame if end_frame < len(self.src_audio_signal) else len(self.src_audio_signal) - 1)
        else:
            raise ValueError("Can't create Fragment: source needs to eiter be the path to a .wav file or a Fragment")

        self.google_recognized_string = ""
        self.out_file = ""

    def load_wav(self, path):
        with wave.open(path, "rb") as src:
            self.src_freq = src.getframerate()
            return np.fromstring(src.readframes(-1), "Int16")

    def generate_hash(self):
        return md5(("%s+%s+%s+%s" % (self.audio_file, str(self.window.start_frame), str(self.window.end_frame), self.google_recognized_string)).encode()).hexdigest()

    def google_recognize_fragment(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.out_file) as source:
            audio = r.record(source)

        try:
            self.google_recognized_string = r.recognize_google(audio)
        except sr.UnknownValueError:
            #print("Google Speech Recognition could not understand audio")
            pass
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        except Exception as e:
            print(e)

    def generate_wav(self, out_dir, freq=44100.0):
        if not path.exists(out_dir):
            makedirs(out_dir)

        self.out_file = path.join(out_dir, "%i-fragment-%s.wav" % (self._id, self.generate_hash()))

        if not path.exists(self.out_file):
            with wave.open(self.out_file, "w") as out:
                #pylint: disable=no-member
                out.setnchannels(1)
                out.setsampwidth(2)
                out.setframerate(freq)

                for i in range(self.window.start_frame, self.window.end_frame):
                    data = struct.pack("<h", self.src_audio_signal[i])
                    out.writeframesraw(data)

    def __len__(self):
        return len(self.window)

    def __repr__(self):
        return "Fragment(_id=%i, source=%s, window=%s)" % (self._id, self.source, self.window)

