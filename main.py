#!/usr/bin/env python3

import math
import os
import time
import warnings
from typing import Dict, Any

import pyaudio
import pyttsx3
import torch
import wave
import whisper
import yaml
from langchain.chains import LLMChain, RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama.llms import OllamaLLM

# Suppress warnings
warnings.filterwarnings("ignore")

class ArtemisAssistant:
    """Artemis voice assistant class that handles audio I/O, speech recognition, and LLM responses."""
    
    def __init__(self, config_path: str = './config.yaml'):
        """Initialize the assistant with configuration from yaml file."""
        print("============================ Initialization ============================")
        print("Setting up...")
        
        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Initialize text-to-speech engine
        self.engine = self._init_tts_engine()
        
        # Initialize speech recognition components
        self.whisper_model = self._init_whisper_model()
        self.audio = pyaudio.PyAudio()
        
        # Setup LLM and RAG components
        self.llm, self.memory, self.qa_chain, self.retriever = self._init_llm_components()
        
        # Print setup completion message
        self.print_and_speak("Setting up complete!")
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from yaml file."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config
    
    def _init_tts_engine(self) -> pyttsx3.Engine:
        """Initialize and configure text-to-speech engine."""
        engine = pyttsx3.init()
        engine.setProperty('voice', 'english-us')
        engine.setProperty('rate', 190)
        engine.setProperty('volume', 3.0)
        return engine
    
    def _init_whisper_model(self) -> whisper.model:
        """Initialize and load Whisper model for speech recognition."""
        return whisper.load_model('base.en')
    
    def _init_llm_components(self):
        """Initialize LLM, memory, and retrieval components for RAG."""
        # Get config values
        max_words = int(self.config['ollama']['word_count'])
        faiss_path = self.config['tokenizer']['db_faiss_path']
        embedding_model_name = self.config['tokenizer']['instructor_embeddings']
        
        # Set up system prompt
        sys_prompt = self.config['ollama']['system_prompt'] + f"\n\nPlease keep all of your responses within {max_words} words."
        
        # Set device (CUDA if available, otherwise CPU)
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if device == 'cuda':
            device_name = torch.cuda.get_device_name(0)
            print(f"Using CUDA: {device_name}")
        else:
            print("Using CPU")
        
        # Initialize LLM
        
        self.model = self.config['ollama']['model']
        
        llm = OllamaLLM(model=self.model, system=sys_prompt)
        
        print(f"Using this LLM : {self.model}")
        
        # Set up memory
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Set up prompt template
        prompt_template = PromptTemplate(
            input_variables=["system_prompt", "chat_history", "context", "question"],
            template=(
                "System Prompt:\n{system_prompt}\n\n"
                "Conversation History:\n{chat_history}\n\n"
                "Retrieved Context:\n{context}\n\n"
                "Based on the above, answer the question: {question}"
            )
        )
        
        # Set up embeddings
        model_kwargs = {'device': device}
        encode_kwargs = {'normalize_embeddings': True}
        embeddings = HuggingFaceInstructEmbeddings(
            model_name=embedding_model_name, 
            model_kwargs=model_kwargs, 
            encode_kwargs=encode_kwargs
        )
        
        # Set up vector store and retriever
        vectorstore = FAISS.load_local(
            folder_path=faiss_path, 
            embeddings=embeddings, 
            allow_dangerous_deserialization=True
        )
        retriever = vectorstore.as_retriever()
        
        # Set up QA chain
        qa_chain = LLMChain(llm=llm, prompt=prompt_template)
        
        return llm, memory, qa_chain, retriever
    
    def print_and_speak(self, text: str) -> None:
        """Print text to console and speak it through the TTS engine."""
        print(text)
        self.engine.say(text)
        self.engine.runAndWait()
        
    def filter_thinking(self, response):
        """Remove thinking tags and content from LLM response."""
        import re
        # Remove <think>...</think> blocks
        filtered_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        # Remove any other potential thinking markers
        filtered_response = re.sub(r'\[thinking\].*?\[/thinking\]', '', filtered_response, flags=re.DOTALL)
        return filtered_response.strip()

    def run_rag_with_memory(self, question: str) -> str:
        """Process a question through the RAG pipeline and update memory."""
        # Retrieve relevant documents
        retrieved_docs = self.retriever.get_relevant_documents(question)
        context = "\n\n".join(doc.page_content for doc in retrieved_docs)
        
        # Format chat history
        chat_history = ""
        for message in self.memory.chat_memory.messages:
            chat_history += f"{message.type.capitalize()}: {message.content}\n"
        
        # Prepare input for chain
        input_data = {
            "system_prompt": self.config['ollama']['system_prompt'],
            "chat_history": chat_history,
            "context": context,
            "question": question,
        }
        
        # Get answer from chain
        answer = self.qa_chain.run(input_data)
        
        # Apply filter to remove thinking output
        answer = self.filter_thinking(answer)
        
        # Update memory with question and answer
        self.memory.chat_memory.add_user_message(question)
        self.memory.chat_memory.add_ai_message(answer)
        
        return answer
    
    def record_audio(self) -> str:
        """Record audio from microphone and convert to text."""
        # Set audio parameters from config
        FORMAT = pyaudio.paInt16
        CHANNELS = self.config['ollama']['channels']
        RATE = int(self.config['ollama']['rate'])
        CHUNK = self.config['ollama']['chunk']
        INDEX = self.config['ollama']['index']
        WAVE_OUTPUT_FILENAME = self.config['ollama']['wave_filename']
        wait_for_speech = self.config['ollama']['wait_for_speech']
        
        # Open audio stream
        stream = self.audio.open(
            format=FORMAT, 
            channels=CHANNELS,
            rate=RATE, 
            input=True, 
            input_device_index=INDEX,
            frames_per_buffer=CHUNK
        )
        
        # Record audio
        frames = []
        for _ in range(0, math.ceil(RATE / CHUNK * wait_for_speech)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        # Stop and close stream
        stream.stop_stream()
        stream.close()
        
        # Save audio to file
        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        
        # Transcribe audio
        transcription = self.whisper_model.transcribe(WAVE_OUTPUT_FILENAME)
        return transcription['text']
    
    def start_voice_mode(self) -> bool:
        """Run the assistant in voice mode. Returns False if shutdown requested."""
        self.print_and_speak("Can I help you? ")
        
        # Record and process audio
        self.print_and_speak("Processing...")
        prompt = self.record_audio()
        
        # Check for shutdown command
        if prompt.lower() == "shut down.":
            self.print_and_speak("Shutting off...")
            return False
        
        # Process non-empty prompt
        if prompt.strip():
            print(f'User: {prompt}')
            
            # Get response from RAG
            response = self.run_rag_with_memory(prompt)
            self.print_and_speak(response)
            
            # Wait based on response length
            time_per_word = self.config['ollama']['time_per_word']
            time.sleep(time_per_word * len(response.split()))
        
        return True
    
    def start_keyboard_mode(self) -> bool:
        """Run the assistant in keyboard mode. Returns False if shutdown requested."""
        print("Write your question here: ")
        
        # Get input from keyboard
        prompt = input()
        while not prompt:
            self.print_and_speak("Question input is empty. Please try again.")
            prompt = input()
        
        # Check for shutdown command
        if prompt.lower() == "shut down":
            self.print_and_speak("Shutting off...")
            return False
        
        # Process prompt
        self.print_and_speak("Processing...")
        response = self.run_rag_with_memory(prompt)
        self.print_and_speak(response)
        
        # Wait based on response length
        time_per_word = self.config['ollama']['time_per_word']
        time.sleep(time_per_word * len(response.split()))
        
        return True
    
    def start_listening(self) -> None:
        """Main loop for the assistant."""
        print("============================ Artemis Assistant ============================")
        self.print_and_speak("Hello! What can I do for you?")
        
        # Get mode from config
        mode = self.config['ollama']['mode']
        
        # Main loop
        continue_listening = True
        while continue_listening:
            if 'v' in mode.lower():
                # Voice mode
                time.sleep(2)  # Brief pause before starting
                continue_listening = self.start_voice_mode()
            elif 'k' in mode.lower():
                # Keyboard mode
                continue_listening = self.start_keyboard_mode()
            else:
                print("Invalid mode set. Modify the 'mode' value in the config.yaml file to resolve this.")
                break


if __name__ == '__main__':
    assistant = ArtemisAssistant()
    assistant.start_listening()