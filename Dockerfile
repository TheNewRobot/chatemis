
FROM python:3.10.12-slim

# Set working directory
WORKDIR /app

# Copy requirements file and scripts
COPY requirements.txt .
COPY main.py .
COPY scripts/tokenizer.py ./scripts/

# Create and activate virtual environment
#RUN python -m venv env
#ENV PATH="/app/env/bin:$PATH"

# Install dependencies
#RUN pip install -r requirements.txt

# Run the tokenizer script
#RUN python scripts/tokenizer.py

# Run audio_mic_test
RUN python scripts/audio_mic_test.py
RUN aplay speech.wav

# Run the main application
CMD ["python", "main.py"]
