import speech_recognition as sr

OUT_FILE = "samples/trump_1_min.wav"

# use the audio file as the audio source
r = sr.Recognizer()
with sr.AudioFile(OUT_FILE) as source:
    audio = r.record(source)  # read the entire audio file

# recognize speech using Google Speech Recognition
try:
    print(r.recognize_google(audio))
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))
