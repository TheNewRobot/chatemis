from os import system
import speech_recognition as sr
from playsound import playsound
import gpt4all 
import sys
import whisper
import warnings
import time
import os

wake_word = 'artemis'
model = GPT4All('/home/romela/Downloads/mistral-7b-instruct-v0.1.Q4_0.gguf')
