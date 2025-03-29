# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update && sudo apt-get install -y \
    portaudio19-dev \
    alsa-utils \
    pulseaudio \
    libasound2-dev

sudo apt-get update
sudo apt -y install ffmpeg
sudo apt-get -y install cmake
sudo apt-get -y install python3-pyaudio
sudo apt install -y portaudio19-dev
sudo apt install -y espeak-ng

# Install Python dependencies
echo "Installing Python packages..."
pip install --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib' pyaudio 
pip install --upgrade pip
pip install --no-deps -r requirements.txt

echo "Installation complete!"