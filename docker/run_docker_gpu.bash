# If not working, first do: sudo rm -rf /tmp/.docker.xauth
# It still not working, try running the script as root.
## Build the image first
### docker build -t r2_path_planning .
## then run this script
## It has to be run in the environmnet with ROS
xhost local:root

XAUTH=/tmp/.docker.xauth

# This is only for the first time
# Change the name of the container each time you need to use it 
# you have to run this in a ROS-based environment to work, otherwise you will get an error in line --env

docker run -it \
    --name=chatemis \
    --network="host" \
    --env="DISPLAY=$DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --env="XAUTHORITY=$XAUTH" \
    --volume="$XAUTH:$XAUTH" \
    --privileged \
    --runtime=nvidia \
    --gpus=all \
    --volume="/dev:/dev" \
    osrf/ros:humble-desktop-full \
    /bin/bash
