#!/bin/bash

#if [ $# -lt 1 ]; then
#	echo "usage $0 <user> <nodes_list> (use ',' to separate nodes in list )"
#	exit
#fi

set -x

     cd helper
#     ex -sc $"%s/\r$//e|x" deploy_upis.sh
#     sh deploy_upis.sh root alix04,alix05  #deploy framework on alixnodes
     ex -sc $"%s/\r$//e|x" sync_date.sh
     sh sync_date.sh root alix04,alix05  #sync nodes time
     cd ..

    ssh root@alix04 "killall -9 iperf & killall -9 python3 & killall -9 hostapd"
    ssh root@alix05 "killall -9 iperf & killall -9 python3 & killall -9 hostapd"
    ssh root@alix04 "cd ~/wishful-github-manifest/final_showcase/network_wifi/solution_wifi_ct && python3 agent --config agent_cfg_ap.yaml > agent.out 2> agent.err < /dev/null &" &
    ssh root@alix05 "cd ~/wishful-github-manifest/final_showcase/network_wifi/solution_wifi_ct && python3 agent --config agent_cfg_sta.yaml > agent.out 2> agent.err < /dev/null &" &
    sleep 2
    python3 controller_wifi --config controller_cfg_nuc12.yaml --nodes node_info.txt
    ssh root@alix04 "killall -9 iperf & killall -9 python3 & killall -9 hostapd"
    ssh root@alix05 "killall -9 iperf & killall -9 python3 & killall -9 hostapd"

set +x


