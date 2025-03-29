#!/bin/bash

# Script to run the RoMeLa ChatBot Docker container
# Place this in the misc folder

echo "============================================"
echo "Starting RoMeLa ChatBot container"
echo "============================================"

# Get current user ID dynamically
USER_ID=$(id -u)

# Check if the container already exists
if docker ps -a | grep -q chatemis; then
  echo "Container already exists, starting it..."
  docker start chatemis
  docker exec -it chatemis bash
else
  echo "Creating and running new ChatBot container..."
  # Run the container with required pulseaudio settings
  # The --rm flag is removed so container persists after exit
  docker run -it --name chatemis \
    --privileged \
    --device /dev/snd \
    --runtime nvidia \
    --network=host \
    -e PULSE_SERVER=unix:/run/user/${USER_ID}/pulse/native \
    -e PULSE_COOKIE=/tmp/pulse_cookie \
    -v /run/user/${USER_ID}/pulse:/run/user/${USER_ID}/pulse \
    -v ~/.config/pulse/cookie:/tmp/pulse_cookie:ro \
    -v /dev/shm:/dev/shm \
    jetsonchat \
    bash 
fi

echo "============================================"
echo "Container session ended"
echo "Container 'chatemis' is still running in the background"
echo "Use 'docker exec -it chatemis bash' to reconnect with a new shell"
echo "Use 'docker attach chatemis' to reconnect to the existing session"
echo "Use 'docker stop chatemis' to stop the container"
echo "============================================"