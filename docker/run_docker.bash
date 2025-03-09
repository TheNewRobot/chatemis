sudo docker run --rm -it \
	--device /dev/snd \
	--group-add audio \
	--network=host \
	chatemis

#NOTE: You must add the line "load-module module-native-protocol-tcp auth-ip-acl=127.0.0.1" to the file /etc/pulse/default.pa for this to work properly. This only needs to be done once.
