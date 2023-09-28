#! /bin/bash
if [ $# -lt 1 ]; then
	echo "usage $0 'nodes list'     (use '' for list)"
	exit
fi
stations=$1
set -x
for sta in $stations
do
	controller_time=$(date +%T); ssh root@$sta "date +%T -s ${controller_time};" > /dev/null
done
set +x