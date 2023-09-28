#!/bin/bash

if [ $# -lt 1 ]; then
	echo "usage $0 nodes_list     (use ',' to separate nodes in list )"
	exit
fi

set -x
nodes=$(echo $1 | tr "," "\n")
stations=$nodes
master_directory="wishful-github-manifest-7"
kill_before=0

if [ 1 -eq 1 ]; then

    for sta in $stations
    do
        rsync -avz  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude examples/* --exclude agent_modules/*  --exclude .repo/ ../../../../  -e ssh root@$sta:~/wishful-github-manifest/
        rsync -avz  ../../../../agent_modules/iperf/  -e ssh root@$sta:~/wishful-github-manifest/agent_modules/iperf/
        rsync -avz  ../../../../agent_modules/wifi_wmp/  -e ssh root@$sta:~/wishful-github-manifest/agent_modules/wifi_wmp/
        rsync -avz  ../../../../agent_modules/wifi/  -e ssh root@$sta:~/wishful-github-manifest/agent_modules/wifi/
        rsync -avz  ../../../../agent_modules/net_linux/  -e ssh root@$sta:~/wishful-github-manifest/agent_modules/net_linux/
        ssh root@$sta 'mkdir ~/wishful-github-manifest/examples/Get_Started_Examples'
        rsync -avz  ../../../../examples/Get_Started_Examples/Advanced_WMP_Example/  -e ssh root@$sta:~/wishful-github-manifest/examples/Get_Started_Examples/Advanced_WMP_Example/
    done

fi

set +x


