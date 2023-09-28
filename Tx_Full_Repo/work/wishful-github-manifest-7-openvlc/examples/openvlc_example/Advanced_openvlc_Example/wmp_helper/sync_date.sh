#! /bin/bash
if [ $# -lt 1 ]; then
	echo "usage $0 nodes_list     (use ',' to separate nodes in list )"
	exit
fi

set -x
nodes=$(echo $1 | tr "," "\n")
stations=$nodes
for sta in $stations
do
	controller_time=$(date +%T); ssh root@$sta "date +%T -s ${controller_time};" > /dev/null
done
set +x