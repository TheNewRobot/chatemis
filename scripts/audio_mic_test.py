import pyaudio
import speech_recognition as sr
import pyttsx3


# Constants
MODE = 1
ENERGY_THRESHOLD = 2000  # Sensitive Microphones in loud rooms might set this to 4000 (good starting point)
PHRASE_TIME_LIMIT = 2    # seconds

r = sr.Recognizer()
mic = sr.Microphone(device_index=0)  # Change index to match your device

engine = pyttsx3.init('espeak')
engine.setProperty('voice', 'english-us')
engine.setProperty('rate', 190)
engine.setProperty('volume', 3.0)

def say_and_print(text):
	"""Prints the text to the console and uses the speech engine to say it."""
	print(text)
	engine.say(text)
	engine.runAndWait()

# Greet the user
say_and_print("Hello sir, welcome to this test!")

# Optional: Uncomment to list available microphones
#print('This is the list of available Microphones')
#print(sr.Microphone.list_microphone_names())

with mic as source:
	say_and_print("Calibration...")
	r.adjust_for_ambient_noise(source, duration=2.5)
	say_and_print("Listening...")
	audio = r.listen(source, phrase_time_limit=PHRASE_TIME_LIMIT)

if MODE == 0:
	# Mode 0: Record audio and save to file.
	try:
		with open("speech.wav", "wb") as f:
			say_and_print("Great, now we have recorded...")
			f.write(audio.get_wav_data())
	except Exception as e:
	    say_and_print("Error recording audio: " + str(e))
else:
# Mode 1: Attempt speech recognition.
	try:
		say_and_print("Recognizing...")
		result = r.recognize_google(audio)
		say_and_print("You said: " + result)
		with open('../prev_prompt.txt' ,'w') as f:
			f.write(result)
	except sr.UnknownValueError:
		say_and_print("Could not understand audio")
	except Exception as e:
		say_and_print("Error recognizing speech: " + str(e))
