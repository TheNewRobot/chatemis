import pyaudio
import speech_recognition as sr
import pyttsx3
from ollama import ChatResponse, chat


# Constants
MODE = 1
ENERGY_THRESHOLD = 2000  # Sensitive Microphones in loud rooms might set this to 4000 (good starting point)
	
#mic = sr.Microphone(device_index=0)  # Change index to match your device

engine = pyttsx3.init()

engine.setProperty('voice', 'english-us')
engine.setProperty('rate', 120)
engine.setProperty('volume', 3.0)

def say_and_print(text):
	"""Prints the text to the console and uses the speech engine to say it."""	    		
	print(text)
	engine.say(text)
	engine.runAndWait()
    
  
r = sr.Recognizer()
say_and_print("Hello sir, welcome to this test!")
with sr.Microphone() as source:
	print("Calibrating...")
	r.adjust_for_ambient_noise(source, duration=5)
	print("Speak Please")
	audio = r.record(source, duration=4)

# Greet the user

# Optional: Uncomment to list available microphones
#print('This is the list of available Microphones')
#print(sr.Microphone.list_microphone_names())

#with mic as source:
#    say_and_print("Calibration...")
#    r.adjust_for_ambient_noise(source, duration=2.5)
#    say_and_print("Listening...")
#    audio = r.listen(source, phrase_time_limit=PHRASE_TIME_LIMIT)

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
		result =  r.recognize_sphinx(audio)
		print("You said:" + result)
		response: ChatResponse = chat(model='llama3.2', messages=[
		  {
		    'role': 'user',
		    'content': result,
		  },
		])

		say_and_print(response.message.content)

	except sr.UnknownValueError:
	    say_and_print("Could not understand audio")
	except Exception as e:
	    say_and_print("Error recognizing speech: " + str(e))
    
  
