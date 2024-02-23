import pyaudio
import speech_recognition as sr
import pyttsx3

# TODO: Include a simple function to print and say the same thing!
# Constants
MODE = 0
ENERGY_THRESHOLD = 6000
PHRASE_TIME_LIMIT = 3 # seconds

r = sr.Recognizer()
mic = sr.Microphone()

engine = pyttsx3.init('espeak')
engine.setProperty('voice', 'english-us')
engine.setProperty('rate', 250)
engine.setProperty('volume', 3.0) 
print("Hello sir, welcome to this test!")
engine.say("Hello sir, welcome to this test!")
engine.runAndWait()

# print('This is the list of available Microphones')
# sr.Microphone.list_microphone_names()

with mic as source:
    r.adjust_for_ambient_noise(source)
    print("Listening...")
    audio = r.listen(source, phrase_time_limit=PHRASE_TIME_LIMIT)

if MODE == 0:
    # Mode 0 just records audio 
    try:
        with open("speech.wav","wb") as f:
            print("Great, now we have recorded...")
            f.write(audio.get_wav_data())
    except Exception as e:
        print("Error recording audio:", e)
        
else: 
    # Mode 1 attempts speech recognition
    try:
        print("Recognizing...")
        result = r.recognize_google(audio)
        print("You said: " + result)
        engine.say(result)
        engine.runAndWait()

    except sr.UnknownValueError:
        print("Could not understand audio")
    except Exception as e:
        print("Error recognizing speech:", e)
