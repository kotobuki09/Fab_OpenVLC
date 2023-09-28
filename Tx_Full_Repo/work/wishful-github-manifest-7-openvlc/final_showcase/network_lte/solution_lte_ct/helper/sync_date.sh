#! /bin/bash
if [ $# -lt 1 ]; then
	echo "usage $0 <user> <nodes_list> (use ',' to separate nodes in list )"
	exit
fi
nodes=$(echo $2 | tr "," "\n")
user=$1
set -x
for sta in $nodes
do
	controller_time=$(date +%T); ssh $user@$sta "sudo date +%T -s ${controller_time};" > /dev/null
done
set +x
