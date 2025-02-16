import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
	print("Calibrating...")
	r.adjust_for_ambient_noise(source, duration=2)
	print("Speak Please")
	audio = r.record(source, duration=2)
	result =  r.recognize_sphinx(audio)
	print("You said:" + result)

