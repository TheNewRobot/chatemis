# RoMeLa ChatBots!

## Overview

RoMeLa ChatBots is a specialized conversational AI system being developed for RoMeLa's advanced robotic platforms, including the humanoid robots ARTEMIS and COSMO, DARwIn, and other RoMeLa robots. The system aims to implement a retrieval-based architecture that will enable robots to engage in natural and informative conversations during laboratory demonstrations (offline!). By leveraging a knowledge base built from alumni theses and research publications specific to each robot, the system will allow robots to provide accurate, technical responses while maintaining engaging interactions with visitors.  Here’s a video demo of the fully offline system in action:

[Download video](./videos/demo.mp4) *(Fully offline interaction with BRUCE)* 

<div align="center">
  <img src="images/Jetson_Audio_Module.jpg" alt="RoMeLa Robot Demo" width="600" height="400">
  <p><em>Jetson Audio Module, designed to be adapted to small, medium and large form factors </em></p>
</div>

## System Requirements

- Ubuntu 22.04 LTS
- Python 3.10.12
- CTK 12.6
- nvidia-jetpack (6.0+b106)

## Hardware Components 

- Jetson Orin Nano + Audio Case (if you want us to release the CAD for the cute case, let us know!)
-  [Waveshare Audio Card for Jetson Nano](https://www.waveshare.com/audio-card-for-jetson-nano.htm) - USB audio codec designed specifically for Jetson Nano that provides audio input/output capabilities. We have validated that this can also work for a Jetson Orin Nano.


## Quick Start

### 1. Audio Source Check

In the "Sound" tab:

- Ensure the "Output Device" is set to "Speakers - USB PnP Audio Device."
- Ensure the "Input Device" is set to "Microphone - USB PnP Audio Device."

### 2. Environment Setup

Create and activate a Python virtual environment in the root of the project:

```bash
python -m venv jetsonchat
source jetsonchat/bin/activate
```

Install dependencies:
```bash
chmod +x misc/*.sh
./misc/install.sh
```

### 3. Audio System verification
Test your audio setup before running the main application:

```
python ./scripts/audio_mic_test.py
```

### 4. Initial configuration

1. Generate the vector database (first-time setup). It might take a long time depending on the size of your documents. Luckily, this will be done only once, be patient and let it run:
```
python scripts/tokenizer.py
```
Note: Ensure your RAG data is in the data folder before running this command. For the sake of this example, we included one paper related to one of our robots called BRUCE (Bipedal Robotic Unit with Compliant Enhanced locomotion).

2. Download an LLM model:
- Select a model compatible with ollama CUDA: https://ollama.com/search
- Write the name of the model in config.yaml in the "model" field

Check the models that are available through ollama with this command
```bash
ollama list
```
and then pull the one of your preference with this (example - the best one so far for this application)
```bash
ollama pull llama3.2:3b
```
After this you can run it offline

3. Adjust the parameters in config.yaml according to your application

  Important parameters

    - `mode`: Set to "k" for keyboard input or "v" for voice interaction
    - `model`: Choose "llama3" for balance, "mistral" for speed, or "llama3.2:70b" for quality
    - `word_count`: Controls response length (15-20: concise, 30-40: detailed)
    - `chunk_size`: Affects RAG precision (smaller: 300-400) vs. context (larger: 600-1000)


4. Start the main application:
```
python main.py 
```

## Docker Deployment

### If you are using Docker

(Optional) Make sure that your user is added to the docker group, otherwise there might be permission problems with the audio card
```bash
sudo usermod -aG docker $USER
```
And reboot after.

1. Open the Dockerfile and change "data.pdf" to the actual name of your PDF in the "data" folder and comment/uncomment lines as needed for tokenization.

2. Run the following command to build the Docker environment for the first time:
```bash
docker build -t jetsonchat .
```

3. Run the following command to start the Docker container with required pulseaudio information:
```bash
# Start and run the container
docker start chatemis
```

4. Run the script to create and start the container for the first time or when you want to execute it again:
```bash
./misc/docker_run.sh
```

5. Repeat the tokenization process, check the audio and then run the main python script! 

 **Warning:** Unless you want your Jetson becoming your roommate's 3 AM conversation partner, remember to stop that container! :)

 ## Performance Profiling 

During testing with the Llama 3.2:2b model, the system was asked:

User: "What is your name? What are you?"

Response: "My name is BRUCE, and I am a miniature bipedal robot with proprioceptive actuation. I'm designed to perform highly dynamic motions like those of a human's lower body, while also being able to interact with unstructured environments through my contacts sensing capabilities."

The response was generated in ~30 seconds, with a clear GPU utilization spike visible in the performance graph below at 25 seconds (check GPU utilization). This highlights the computational load of offline LLM inference on the Jetson Orin Nano while maintaining responsive interactions. I encourage to test different large language models and check what are the different responses that you obtain for the same question!

<div align="center">
  <img src="images/jetson_custom_view.png" alt="RoMeLa Robot Demo" width="450" height="600">
  <p><em> Peak GPU utilization during LLM inference (~30s response time) based on tegra-stats</em></p>
</div>

For detailed profiling tools and scripts, check the misc/ folder.


