#!/bin/bash
if [ -n "$1" ]
then
	curl http://$1:42280/getBIOS > BIOS.np
else
	echo "Usage: getBIOS.sh 192.168.0.22"
fi
