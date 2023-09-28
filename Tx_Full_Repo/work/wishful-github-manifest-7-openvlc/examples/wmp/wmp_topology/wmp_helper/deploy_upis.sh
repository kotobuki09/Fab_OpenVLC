#!/bin/bash

if [ $# -lt 1 ]; then
	echo "usage $0 'nodes list'     (use '' for list)"
	exit
fi

set -x
stations=$1
master_directory="wishful-github-manifest-3"
kill_before=0

if [ 1 -eq 1 ]; then

    for sta in $stations
    do
        rsync -avz  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude examples/* --exclude agent_modules/*  --exclude .repo/ ../../../../../$master_directory/  -e ssh root@$sta:~/wishful-github-manifest/
        rsync -avz  ../../../../../$master_directory/agent_modules/iperf/  -e ssh root@$sta:~/wishful-github-manifest/agent_modules/iperf/
        rsync -avz  ../../../../../$master_directory/agent_modules/wifi_wmp/  -e ssh root@$sta:~/wishful-github-manifest/agent_modules/wifi_wmp/
        rsync -avz  ../../../../../$master_directory/agent_modules/wifi/  -e ssh root@$sta:~/wishful-github-manifest/agent_modules/wifi/
        rsync -avz  ../../../../../$master_directory/examples/wmp/  -e ssh root@$sta:~/wishful-github-manifest/examples/wmp/
    done

fi

set +x


