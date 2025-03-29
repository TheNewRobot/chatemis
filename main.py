#!/usr/bin/env python3

from os import system 
import pyaudio
import speech_recognition as sr
import sys
import whisper
import time
import os
import yaml
# For Ubuntu
import pyttsx3
import torch
from ollama import ChatResponse, chat
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain_ollama.llms import OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from InstructorEmbedding import INSTRUCTOR
from langchain_community.vectorstores import FAISS
import sounddevice as sd
from scipy.io.wavfile import write
import warnings
import threading
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import pyaudio
import wave
import math

warnings.filterwarnings("ignore")

#from scripts.llm_cpp import LLM_object

# We can consider using the warning library to delete the warning logs 

#wake_word = 'computer' # Don't move the microphone in your headset 

listening_for_wake_word = True
processing = False
print("============================Initialization============================")

r = sr.Recognizer()
# Run this code for the first time
# breakpoint()
# Continuously run the code using the cached files in this path
#tiny_model_path = os.path.expanduser('/root/.cache/whisper/tiny.pt')
base_model_path = os.path.expanduser('/root/.cache/whisper/base.pt')
#tiny_model = whisper.load_model('tiny.en')
base_model = whisper.load_model('base.en')
source = sr.Microphone()


config_path = './config.yaml'
with open(config_path, "r") as f:
	config = yaml.safe_load(f)

# Set up TTS engine
engine = pyttsx3.init()
engine.setProperty('voice', 'english-us')
engine.setProperty('rate', 190)
engine.setProperty('volume',3.0) 

# Function to print and speak text
def print_and_speak(text):
	print(text)
	engine.say(text)
	engine.runAndWait()

# Get information from congig file
print_and_speak("Setting up...")
max_words = int(config['ollama']['word_count'])
faiss_path = config['tokenizer']['db_faiss_path']
embedding_model_name = config['tokenizer']['instructor_embeddings']
mode = config['ollama']['mode']
FORMAT = pyaudio.paInt16
CHANNELS = config['ollama']['channels']
RATE = int(config['ollama']['rate'])
CHUNK = config['ollama']['chunk']
WAVE_OUTPUT_FILENAME = config['ollama']['wave_filename']
INDEX = config['ollama']['index']
audio = pyaudio.PyAudio()
time_per_word = config['ollama']['time_per_word']
wait_for_speech = config['ollama']['wait_for_speech']
sys_prompt = config['ollama']['system_prompt'] + "\n\nPlease keep all of your responses within " + str(max_words) + " words."

# Create RetrievalQA
llm = OllamaLLM(model = config['ollama']['model'], system=sys_prompt)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
prompt_template = PromptTemplate(
    input_variables=["system_prompt", "chat_history", "context", "question"],
    template=(
        "System Prompt:\n{system_prompt}\n\n"
        "Conversation History:\n{chat_history}\n\n"
        "Retrieved Context:\n{context}\n\n"
        "Based on the above, answer the question: {question}"
    )
)

# Set device
device = None
if torch.cuda.is_available():
	device_name = torch.cuda.get_device_name(0)  
	print("You are good to go with cuda! Device: ", device_name)
	device = 'cuda'
else:
	print("You are good to go with cpu!")
	device = 'cpu'

# Set up embeddings
model_kwargs = {'device': device}
encode_kwargs = {'normalize_embeddings': True}
embeddings = HuggingFaceInstructEmbeddings(model_name=embedding_model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)

# Set up data for RAG
vectorstore = FAISS.load_local(folder_path=faiss_path, embeddings=embeddings, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever()
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, memory=memory)

qa_chain = LLMChain(llm=llm, prompt=prompt_template)

# Function to get information from data and remember past messages
def run_rag_with_memory(question: str) -> str:
    retrieved_docs = retriever.get_relevant_documents(question)
    context = "\n\n".join(doc.page_content for doc in retrieved_docs)
    
    chat_history = ""
    for message in memory.chat_memory.messages:
        chat_history += f"{message.type.capitalize()}: {message.content}\n"
    
    input_data = {
        "system_prompt": sys_prompt,
        "chat_history": chat_history,
        "context": context,
        "question": question,
    }
    

    answer = qa_chain.run(input_data)
    
    memory.chat_memory.add_user_message(question)
    memory.chat_memory.add_ai_message(answer)
    
    return answer

def start_listening():
	
	print("============================Artemis Assistant============================")
	print_and_speak("Hello! What can I do for you?")  

	while True:
		# Voice mode
		if 'v' in mode.lower():
			
			time.sleep(2)
			
			print_and_speak("Please state your question.")
			# Record audio from user
			stream = audio.open(format=FORMAT, channels=CHANNELS,
					rate=RATE, input=True,input_device_index = INDEX,
					frames_per_buffer=CHUNK)
			Recordframes = []
			 
			for i in range(0, math.ceil(RATE / CHUNK * wait_for_speech)):
			    data = stream.read(CHUNK)
			    Recordframes.append(data)
			 
			stream.stop_stream()
			stream.close()
			print_and_speak("Processing...")
			waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
			waveFile.setnchannels(CHANNELS)
			waveFile.setsampwidth(audio.get_sample_size(FORMAT))
			audio.terminate()
			waveFile.setframerate(RATE)
			waveFile.writeframes(b''.join(Recordframes))
			waveFile.close()
				
			prompt = base_model.transcribe(WAVE_OUTPUT_FILENAME)['text']

			if prompt.lower() == "shut down.":
				print_and_speak("Shutting off...")
				break
			elif len(prompt.strip()) != 0:
				print('User: ' + prompt)
				
				# Get response
				response = run_rag_with_memory(prompt)
				print_and_speak(response)

				time.sleep(time_per_word*len(response))
		# Keyboard mode
		elif 'k' in mode.lower():
			print("Write your question here: ")
			
			prompt = input()
			while len(prompt) == 0:
				print_and_say("Question input is empty. Please try again.")
				prompt = input()
			if prompt.lower() == "shut down":
				print_and_speak("Shutting off...")
				break
			print_and_speak("Processing...")
			response = run_rag_with_memory(prompt)
			print_and_speak(response)

			time.sleep(time_per_word*len(response))
		else:
			print("Invalid mode set. Modify the 'mode' value in the config.yaml file to resolve this.")
		prompt = ""


if __name__ == '__main__':
    start_listening()
