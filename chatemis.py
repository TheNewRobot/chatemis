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
model = GPT4All('/root/.local/share/nomic.ai/GPT4All/gpt4all-falcon-newbpe-q4_0.gguf')
