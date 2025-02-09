# Instruction in how to run this one
Don't forget to install alsa

# Test audio 
It is highly recommended to first run <audio_mic_test.py> to see that everything is working. then you can play with alsa the following file
```
aplay speech.wav
```
and comment this lines in /usr/share/alsa/alsa.conf

```
# pcm.rear cards.pcm.rear
# pcm.center_lfe cards.pcm.center_lfe
# pcm.side cards.pcm.side
# pcm.surround21 cards.pcm.surround21
# pcm.surround40 cards.pcm.surround40
# pcm.surround41 cards.pcm.surround41
# pcm.surround50 cards.pcm.surround50
# pcm.surround51 cards.pcm.surround51
# pcm.surround71 cards.pcm.surround71
```
Start the docker container
```
docker start chatemis
```
check if it's running
```
docker ps -l
```
run it again with this command (in different terminals, if you want)
```
docker exec -it chatemis /bin/bash
```
