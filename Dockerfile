# Base image with Python 3.10.12
FROM python:3.10.12-slim

ARG PYTHON_ENV_NAME=jetsonchat

# Set working directory
WORKDIR /app

# Create required directories
RUN mkdir -p /app/vectorstore /app/data /app/misc/performance

# Copy configuration files
COPY requirements.txt config.yaml main.py ./

# Copy performance monitoring scripts
COPY misc/performance/ ./misc/performance/

# Set up for either pre-tokenized or raw data processing
# OPTION 1: If you already tokenized your documents
#COPY /vectorstore/index.faiss /vectorstore/index.pkl ./vectorstore/

# OPTION 2: If you need to tokenize documents during build
COPY data/data.pdf ./data/
COPY scripts/tokenizer.py ./scripts/
COPY scripts/audio_mic_test.py ./scripts/

# Create virtual environment
RUN python -m venv ${PYTHON_ENV_NAME}

# Set environment variables to use the virtual environment
ENV PATH="/app/${PYTHON_ENV_NAME}/bin:$PATH"
ENV VIRTUAL_ENV="/app/${PYTHON_ENV_NAME}"

# Install system dependencies (grouped by purpose)
RUN apt-get update && apt-get install -y \
    # Audio dependencies
    portaudio19-dev \
    libasound2-dev \
    alsa-utils \
    pulseaudio \
    pulseaudio-utils \
    flac \
    # Media processing
    ffmpeg \
    # Build tools
    cmake \
    # Text-to-speech
    espeak-ng \
    # Python audio support
    python3-pyaudio

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --global-option='build_ext' \
    --global-option='-I/usr/local/include' \
    --global-option='-L/usr/local/lib' \
    pyaudio && \
    pip install --no-deps -r requirements.txt

# Run the tokenizer script (Remove this if using pre-tokenized documents)
# RUN python scripts/tokenizer.py

# Launch the application
# CMD ["python", "main.py"]