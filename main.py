#!/usr/bin/env python3

from os import system 
import pyaudio
import speech_recognition as sr
from gpt4all import GPT4All
import sys
import whisper
import warnings 
import time
import os
# For Ubuntu
import pyttsx3
from scripts.llm_cpp import LLM_object

# We can consider using the warning library to delete the warning logs 

wake_word = 'computer' # Don't move the microphone in your headset 
listening_for_wake_word = True
GPT = False
print("============================Initialization============================")
# Download the model from the GPT4All application
if GPT:
    model = GPT4All('/root/Arturo/mistral-7b-instruct-v0.1.Q4_0.gguf', allow_download=False)
else:
    llama2 = LLM_object("config.yaml")
    llama2.check_cuda()
    model = llama2.qa_bot()
    print('We are using this model: ')
    print(llama2.llm_model)
r = sr.Recognizer()
# Run this code for the first time
# tiny_model = whisper.load_model('tiny')   
# base_model = whisper.load_model('base')
# breakpoint()
# Continuously run the code using the cached files in this path
tiny_model_path = os.path.expanduser('/root/.cache/whisper/tiny.pt')
base_model_path = os.path.expanduser('/root/.cache/whisper/base.pt')
tiny_model = whisper.load_model(tiny_model_path)
base_model = whisper.load_model(base_model_path)
source = sr.Microphone()

# tiktoken is frozen so it can load the vocab and the token from cached files, so we can use it online 
engine = pyttsx3.init()
engine.setProperty('voice', 'english-us')
engine.setProperty('rate', 200)
engine.setProperty('volume', 3.0) 
#engine.say("Hello Sir. What can I do for you?")
#engine.runAndWait()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen_for_wake_word(audio):
    global listening_for_wake_word
    with open("wake_detect.wav", "wb") as f:
        f.write(audio.get_wav_data())
    result = tiny_model.transcribe('wake_detect.wav')
    text_input = result['text']
    if wake_word in text_input.lower().strip():
        print("Wake word detected. Please speak your prompt to Artemis!")
        print('Listening')
        speak('Listening')
        listening_for_wake_word = False

def prompt_gpt(audio):
    global listening_for_wake_word
    try:
        with open("prompt.wav", "wb") as f:
            f.write(audio.get_wav_data())
        result = tiny_model.transcribe('prompt.wav')
        prompt_text = result['text']
        if len(prompt_text.strip()) == 0:
            print("Empty prompt. Please speak again.")
            speak("Empty prompt. Please speak again.")
            listening_for_wake_word = True
        else:
            print('User: ' + prompt_text)
            if GPT:
                output = model.generate(prompt_text, max_tokens=100)
                print('GPT4All: ', output)
            else:
                output = model.invoke({'query': prompt_text})
                output = output['result']
                print('Llama2: ', output)
            speak(output)
            print('\nSay', wake_word, 'to wake me up. \n')
            listening_for_wake_word = True
    except Exception as e:
        print("Prompt error: ", e)

def callback(recognizer, audio):
    global listening_for_wake_word
    try:
        if listening_for_wake_word:
            listen_for_wake_word(audio)
        else:
            prompt_gpt(audio)
    except sr.UnknownValueError:
        print("I couldn't understand the audio")
    except sr.RequestError as e:
        print("We failed I had this error; {0}".format(e))

 
def start_listening():
    with source as s:
        print('\nCalibration... \n')
        r.adjust_for_ambient_noise(s, duration=2) 
    print("============================Artemis Assistant============================")
    print("Hello Sir. What can I do for you?")   
    print('\nSay', wake_word, 'to wake me up. \n')
    stop_flag = r.listen_in_background(source, callback)
    for _ in range(200): time.sleep(0.1)
    print('\nThe Assistant has gone to sleep. \n')

if __name__ == '__main__':
    start_listening()




