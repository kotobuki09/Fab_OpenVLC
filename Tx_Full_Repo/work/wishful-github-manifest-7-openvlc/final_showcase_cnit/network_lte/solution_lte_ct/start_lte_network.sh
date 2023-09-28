#!/bin/bash

#if [ $# -lt 1 ]; then
#	echo "usage $0 <user> <nodes_list> (use ',' to separate nodes in list )"
#	exit
#fi

set -x

     cd helper
         ex -sc $"%s/\r$//e|x" sync_date.sh
         sh sync_date.sh dgarlisi nuc11,nuc6  #sync nodes time
     cd ..

    ssh dgarlisi@nuc11 "cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_lte/solution_lte_ct &&
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/python3.6/config-3.6m-x86_64-linux-gnu &&
    python3 agent_tx.py > agent.out 2> agent.err < /dev/null &" &
    ssh dgarlisi@nuc6 "cd /groups/portable-ilabt-imec-be/wish/imec/wishful-github-manifest-7/final_showcase/network_lte/solution_lte_ct &&
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/python3.6/config-3.6m-x86_64-linux-gnu &&
    python3 agent_rx.py > agent.out 2> agent.err < /dev/null &" &
    sleep 2
    python3 controller_lte --config controller_cfg_nuc12.yaml --nodes node_info.txt
    ssh dgarlisi@nuc6 "killall -9 iperf & killall -9 python3 &  sleep 1 & killall -9 pdsch_ue "
    ssh dgarlisi@nuc11 "killall -9 iperf & killall -9 python3 &  sleep 1 & killall -9 pdsch_enodeb "
set +x
