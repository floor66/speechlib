import wave
import numpy as np
from os import path, makedirs
import struct
from hashlib import md5
import speech_recognition as sr

class Window():
    def __init__(self, start_frame, end_frame, delta, mean):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.delta = delta
        self.mean = mean
        self.size = self.end_frame - self.start_frame

class Fragment():
    def __init__(self, source, start_frame = None, end_frame = None):
        if type(source) is str:
            self.source = source
            self.signal = self.load_wav(source)
            self.audio_file = self.source
            self.start_frame = 0
            self.end_frame = len(self.signal) - 1
        elif type(source) is Fragment:
            self.source = source
            self.audio_file = self.source.audio_file
            self.signal = self.source.signal
            self.start_frame = start_frame
            self.end_frame = end_frame
        else:
            raise ValueError("Fragment source needs to eiter be the path to a .wav file or a Fragment")

        self.google_recognized_string = ""
        self.out_file = ""

    def load_wav(self, path):
        with wave.open(path, "rb") as src:
            return np.fromstring(src.readframes(-1), "Int16")

    def generate_hash(self):
        return md5(("%s+%s+%s+%s" % (self.audio_file, str(self.start_frame), str(self.end_frame), self.google_recognized_string)).encode()).hexdigest()

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

    def generate_wav(self, out_dir):
        if not path.exists(out_dir):
            makedirs(out_dir)

        self.out_file = path.join(out_dir, "fragment-%s.wav" % self.generate_hash())

        with wave.open(self.out_file, "w") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(44100.0)

            for i in range(self.start_frame, self.end_frame):
                data = struct.pack("<h", self.signal[i])
                out.writeframesraw(data)

    def __repr__(self):
        return "Fragment(audio_file=%s, start_frame=%i, end_frame=%i)" % (self.audio_file, self.start_frame, self.end_frame)

