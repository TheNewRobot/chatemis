sudo docker run --rm -it \
	--device /dev/snd \
	--group-add audio \
	--network=host \
	chatemis

