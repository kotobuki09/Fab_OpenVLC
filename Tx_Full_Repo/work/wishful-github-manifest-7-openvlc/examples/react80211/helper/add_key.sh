#! /bin/bash
if [ $# -lt 1 ]; then
	echo "usage $0 <controller_key_path> <user> <nodes_list> (use ',' to separate nodes in list )"
	exit
fi
key_path=$1
user=$2
nodes=$(echo $3 | tr "," "\n")
set -x
for sta in $nodes
do
	scp $key_path $user@$sta:~/controller_id_rsa.pub
	ssh $user@$sta 'cat ~/controller_id_rsa.pub >> ~/.ssh/authorized_keys'
done

for sta in $nodes
do
	scp ~/.ssh/portable_id_rsa.pub $user@$sta:~/portable_id_rsa.pub
	ssh $user@$sta 'cat ~/portable_id_rsa.pub >> ~/.ssh/authorized_keys'
done

scp ~/.ssh/portable_id_rsa nuc6:~/.ssh/id_rsa

set +x