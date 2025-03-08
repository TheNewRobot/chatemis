#!/usr/bin/env python3

from os import system 
import pyaudio
import speech_recognition as sr
#from gpt4all import GPT4All
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

warnings.filterwarnings("ignore")

#from scripts.llm_cpp import LLM_object

# We can consider using the warning library to delete the warning logs 

#wake_word = 'computer' # Don't move the microphone in your headset 

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
# breakpoint()
# Continuously run the code using the cached files in this path
#tiny_model_path = os.path.expanduser('/root/.cache/whisper/tiny.pt')
#base_model_path = os.path.expanduser('/root/.cache/whisper/base.pt')
#tiny_model = whisper.load_model('tiny.en')
#base_model = whisper.load_model('base.en')
source = sr.Microphone()
time_per_word = 0.05
wait_for_speech = 4
# tiktoken is frozen so it can load the vocab and the token from cached files, so we can use it online 
engine = pyttsx3.init()
engine.setProperty('voice', 'english-us')
engine.setProperty('rate', 190)
engine.setProperty('volume', 3.0) 
# Sampling frequency
freq = 44100

	
def print_and_speak(text):
	print(text)
	engine.say(text)
	engine.runAndWait()
	
print_and_speak("Setting up...")

config_path = './config.yaml'
with open(config_path, "r") as f:
	config = yaml.safe_load(f)
max_words = int(config['ollama']['word_count'])
faiss_path = config['tokenizer']['db_faiss_path']
embedding_model_name = config['tokenizer']['instructor_embeddings']
mode = config['ollama']['mode']
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
qa_chain = LLMChain(llm=llm, prompt=prompt_template)
device = None
if torch.cuda.is_available():
	device_name = torch.cuda.get_device_name(0)  
	print("You are good to go with cuda! Device: ", device_name)
	device = 'cuda'
else:
	print("You are good to go with cpu!")
	device = 'cpu'
model_kwargs = {'device': device}
encode_kwargs = {'normalize_embeddings': True}
embeddings = HuggingFaceInstructEmbeddings(model_name=embedding_model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)

vectorstore = FAISS.load_local(folder_path=faiss_path, embeddings=embeddings, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever()
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, memory=memory)

qa_chain = LLMChain(llm=llm, prompt=prompt_template)

def run_rag_with_memory(question: str) -> str:
    # (a) Retrieve relevant documents.
    retrieved_docs = retriever.get_relevant_documents(question)
    context = "\n\n".join(doc.page_content for doc in retrieved_docs)
    
    # (b) Prepare the conversation history.
    chat_history = ""
    for message in memory.chat_memory.messages:
        chat_history += f"{message.type.capitalize()}: {message.content}\n"
    
    # (c) Build the inputs for the chain.
    input_data = {
        "system_prompt": sys_prompt,
        "chat_history": chat_history,
        "context": context,
        "question": question,
    }
    
    # (d) Get the answer from the LLMChain.
    answer = qa_chain.run(input_data)
    
    # (e) Update memory with the new turn.
    memory.chat_memory.add_user_message(question)
    memory.chat_memory.add_ai_message(answer)
    
    return answer

def start_listening():
	#with source as s:
	#	print_and_speak('\nCalibrating... \n')
	#	r.adjust_for_ambient_noise(s, duration=2) 
	print("============================Artemis Assistant============================")
	print_and_speak("Hello! What can I do for you?")  

	while True:

		# Record audio for the given number of seconds
		#sd.wait()
		#write("recording0.wav", freq, recording)
		#result = base_model.transcribe('recording0.wav')
		#prompt_text = result['text']
		#if count % 10 == 0:
			#prompt = "You must keep your responses around " + str(max_words) + " words and follow these instructions when responding to all questions: " + config['ollama']['system_prompt'] + "\n\nAnswer this prompt: "
		#else:
			#prompt = ""
		if 'v' in mode.lower():
			
			print_and_speak("Calibrating...")
			time.sleep(2)
			with source as s:
				r.adjust_for_ambient_noise(s, duration=2)
				print_and_speak("Please state your question.")
				recording = r.record(s, duration=wait_for_speech)
			try:
				prompt = r.recognize_google(recording)

				if any(w in prompt for w in ['exit', 'quit', "shut down"]):
					print_and_speak("Shutting off...")
					break
				elif len(prompt.strip()) != 0:
					print('User: ' + prompt)

					print_and_speak("Processing...")
					response = run_rag_with_memory(prompt)
					print_and_speak(response)

					time.sleep(time_per_word*len(response))
			except: 
				pass
		elif 'k' in mode.lower():
			print("Write your question here: ")
			
			prompt = input()
			while len(prompt) == 0:
				print_and_say("Question input is empty. Please try again.")
				prompt = input()
			if any(w in result for w in ['exit', 'quit', "shut down"]):
				print_and_speak("Shutting off...")
				break
			print_and_speak("Processing...")
			response = run_rag_with_memory(prompt)
			print_and_speak(response)

			time.sleep(time_per_word*len(response['result']))

			#time.sleep(len(response['result'].split())*time_per_word)
		else:
			print("Invalid mode set. Modify the 'mode' value in the config.yaml file to resolve this.")
		prompt = ""
	#if listening_for_wake_word and not processing:
	#print_and_speak('\nThe Assistant has gone to sleep. \n')

if __name__ == '__main__':
    start_listening()
