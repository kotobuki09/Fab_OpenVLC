#! /bin/bash
if [ $# -lt 1 ]; then
	echo "usage $0 nodes_list     (use ',' to separate nodes in list )"
	exit
fi
nodes=$(echo $1 | tr "," "\n")
stations=$nodes
set -x
for sta in $stations
do
	ssh root@alix02 "ping -c 2 192.168.3.1$sta"
done
set +x