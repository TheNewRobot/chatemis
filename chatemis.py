from os import system
import speech_recognition as sr
from playsound import playsound
from gpt4all import GPT4All
import sys
import whisper
import warnings
import time
import os

wake_word = 'artemis'
model = GPT4All('/root/.local/share/nomic.ai/GPT4All/gpt4all-falcon-newbpe-q4_0.gguf')
breakpoint()