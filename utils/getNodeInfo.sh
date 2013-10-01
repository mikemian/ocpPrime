#!/bin/bash
if [ -n "$1" ]
then
	curl http://$1:42280/nodeInfo | python -mtools.json
else
	echo "Usage: getNodeInfo.sh 192.168.0.22"
fi