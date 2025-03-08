# Base image with Python 3.10.12
FROM python:3.10.12-slim

# Set working directory
WORKDIR /app

# Copy requirements file and scripts
COPY requirements.txt .
COPY main.py .
COPY config.yaml .
RUN mkdir -p  /app/vectorstore
RUN mkdir -p  /app/data
COPY /vectorstore/index.faiss ./vectorstore
COPY /vectorstore/index.pkl ./vectorstore
COPY /data/data.pdf ./data
COPY scripts/tokenizer.py ./scripts/
COPY scripts/audio_mic_test.py ./scripts/

# Create and activate virtual environment
RUN python -m venv env
ENV PATH="/app/env/bin:$PATH"

# Install dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    alsa-utils \
    pulseaudio \
    libasound2-dev

RUN apt-get update
RUN apt-get -y install cmake
RUN apt-get -y install python3-pyaudio
RUN apt install -y portaudio19-dev
RUN pip install --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib' pyaudio 
RUN pip install --upgrade pip
RUN pip install --no-deps -r requirements.txt
RUN apt install -y espeak-ng

# Run the tokenizer script
#RUN python scripts/tokenizer.py

# Run the main application
CMD ["python", "main.py"]
