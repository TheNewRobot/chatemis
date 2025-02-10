# RoMeLa ChatBots!

## Overview

RoMeLa ChatBots is a specialized conversational AI system being developed for RoMeLa's advanced robotic platforms, including the humanoid robots ARTEMIS and COSMO, DARwIn, and other laboratory robots. The system aims to implement a retrieval-based architecture that will enable robots to engage in natural and informative conversations during laboratory demonstrations. By leveraging a knowledge base built from alumni theses and research publications specific to each robot, the system will allow robots to provide accurate, technical responses while maintaining engaging interactions with visitors.

<div align="center">
  <img src="images/web.news_.robotmakers.BJM_.a.jpg" alt="RoMeLa Robot Demo" width="600" height="400">
  <p><em>RoMeLa Robot Demo Interaction</em></p>
</div>

TODOs:
+ Optimize the code:
  - Improve the relative imports in the yaml file
  - Create a pipeline for importing and quantizing models from Hugging Face to make them lightweight for the Jetson Orin Nano
  - Automate this optimization process
+ Restructure the project to make it easier to add new robots as they're built and need to be integrated into the system
+ Create a bash file to automate and unify the installation process. Note: The main environment was derived from this video: https://www.youtube.com/watch?v=6zAk0KHmiGw
+ Implement automatic fetching and loading of new LLMs based on their names (we can check Hugging Face, but models should be compatible with llama.cpp)
+ Automate the creation process in Docker


## System Requirements

- Ubuntu 22.04 LTS
- Python 3.10.12
- CUDA 12.4
- Jetson Orin Nano (for deployment)


## Quick Start

### 1. Environment Setup

Create and activate a Python virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 2. Audio System verification
Test your audio setup before running the main application:

```
python audio_mic_test.py
# Verify the recorded audio
aplay speech.wav
```

### 3. Initial configuration

1. Generate the vector database (first-time setup):
```
python scripts/tokenizer.py
```

2. Download an LLM model:
- Select a model compatible with llama.cpp CUDA
- Place it in the models/ directory
- Update the model path in config.yaml

3. Start the application:
```
python main.py 
```
For further reading you can check the `llm_cpp.py` class which is the llm hanlder!

## Docker Deployment

### If we're using Docker (TODO)

```
docker build -t chatemis .
```
### Run the container for the first time 
```
./docker/run_docker_gpu.bash
```
### Managing the Container
```
# Start the container
docker start chatemis

# Verify container status
docker ps -l

# Access the container
docker exec -it chatemis /bin/bash
```



