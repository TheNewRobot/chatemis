#!/usr/bin/env python3

from os import system 
import pyaudio
import speech_recognition as sr
#from gpt4all import GPT4All
import sys
import whisper
import warnings 
import time
import os
import yaml
# For Ubuntu
import pyttsx3
import torch
from ollama import ChatResponse, chat
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

#from scripts.llm_cpp import LLM_object

# We can consider using the warning library to delete the warning logs 

wake_word = 'computer' # Don't move the microphone in your headset 

listening_for_wake_word = True
processing = False
print("============================Initialization============================")
# Download the model from the GPT4All application

#    llama2 = LLM_object("config.yaml")
#    llama2.check_cuda()
#    model = llama2.qa_bot()
#    print('We are using this model: ')
#    print(llama2.llm_model)
r = sr.Recognizer()
# Run this code for the first time
# tiny_model = whisper.load_model('tiny')   
# base_model = whisper.load_model('base')
# breakpoint()
# Continuously run the code using the cached files in this path
#tiny_model_path = os.path.expanduser('/root/.cache/whisper/tiny.pt')
#base_model_path = os.path.expanduser('/root/.cache/whisper/base.pt')
tiny_model = whisper.load_model('tiny.en')
base_model = whisper.load_model('base.en')
source = sr.Microphone()
time_per_word = 0.3
wait_for_speech = 3
# tiktoken is frozen so it can load the vocab and the token from cached files, so we can use it online 
engine = pyttsx3.init()
engine.setProperty('voice', 'english-us')
engine.setProperty('rate', 125)
engine.setProperty('volume', 3.0) 


def print_and_speak(text):
	print(text)
	engine.say(text)
	engine.runAndWait()
	
print_and_speak("Setting up RAG")
# Create RetrievalQA
llm = OllamaLLM(model = "llama3.2")
config_path = './config.yaml'
with open(config_path, "r") as f:
	config = yaml.safe_load(f)
faiss_path = config['tokenizer']['db_faiss_path']
embedding_model_name = config['tokenizer']['instructor_embeddings']
device = None
if torch.cuda.is_available():
	device_name = torch.cuda.get_device_name(0)  
	print("You are good to go with cuda! Device: ", device_name)
	device = 'cuda'
else:
	print("You are good to go with cpu!")
	device = 'cpu'
model_kwargs = {"device": device}

embeddings = HuggingFaceEmbeddings(
    model_name=embedding_model_name,
    model_kwargs=model_kwargs
)
vectorstore = FAISS.load_local(folder_path=faiss_path, embeddings=embeddings, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever()
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)


def callback(recognizer, audio):
	#try:
	global listening_for_wake_word, processing
	if listening_for_wake_word and not processing:
		with open("wake_detect.wav", "wb") as f:
			f.write(audio.get_wav_data())
		result = tiny_model.transcribe('wake_detect.wav')
		text_input = result['text']
		if wake_word in text_input.lower().strip():
			print("Wake word detected. Please speak your prompt to Artemis!")
			print_and_speak('Listening')
			time.sleep(1.5)
			audio = ""
			listening_for_wake_word = False

	else:
		#try:
			time.sleep(wait_for_speech)
			with open("prompt.wav", "wb") as f:
				f.write(audio.get_wav_data())
			result = base_model.transcribe('prompt.wav')
			prompt_text = result['text']
			if len(prompt_text.strip()) == 0:
				print_and_speak("Empty prompt. Please speak again.")
				listening_for_wake_word = True
			else:
				processing = True
				print('User: ' + prompt_text)

				print_and_speak("Processing...")

				response = qa.invoke(prompt_text)
				print_and_speak(response['result'])
				time.sleep(len(response['result'].split())*time_per_word)
				listening_for_wake_word = True
				processing = False
				#print_and_speak("\nSay " + wake_word + " to wake me up.\n")
				with open("prompt.wav", "w") as f:
					f.write("")
				audio = ""
			#except Exception as e:
			#	print("Prompt error: ", e)
    #except:
    #    print("I couldn't understand the audio")
 
def start_listening():
	with source as s:
		print_and_speak('\nCalibrating... \n')
		r.adjust_for_ambient_noise(s, duration=2) 
	print("============================Artemis Assistant============================")
	print_and_speak("Hello Sir. What can I do for you?")   
	print_and_speak('\nSay '+ wake_word+ ' to wake me up. \n')
	while True:
		stop_flag = r.listen_in_background(source, callback)
		for _ in range(40): time.sleep(0.1)
	#if listening_for_wake_word and not processing:
	#print_and_speak('\nThe Assistant has gone to sleep. \n')

if __name__ == '__main__':
    start_listening()
