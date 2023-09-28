#!/bin/bash

set -x

case $1 in
    "stop")
        ssh kistm@nuc5 "killall -9 python2; killall -9 python3"
        ssh kistm@nuc7 "killall -9 python2; killall -9 python3"
        ssh kistm@nuc8 "killall -9 python2; killall -9 python3"
    ;;

    "restart")
        ssh kistm@nuc5 "killall -9 python2; killall -9 python3"
        ssh kistm@nuc7 "killall -9 python2; killall -9 python3"
        ssh kistm@nuc8 "killall -9 python2; killall -9 python3"
        ssh kistm@nuc7 "cd /root/gr-hydra/apps/wishful_control/ && ./wishful_simple_agent.py --config rx1_config.yaml > rx1.log &" & 
        ssh kistm@nuc8 "cd /root/gr-hydra/apps/wishful_control/ && ./wishful_simple_agent.py --config rx2_config.yaml > rx2.log &"  &
        ssh kistm@nuc5 "cd /root/gr-hydra/apps/wishful_control/ && ./wishful_simple_controller.py > control.log &"  &
        ssh kistm@nuc5 "cd /root/gr-hydra/apps/wishful_control/ && ./wishful_simple_agent.py --config tx_config.yaml > tx.log" &
        ;;

    "start")
        ssh kistm@nuc7 "cd /root/gr-hydra/apps/wishful_control/ && ./wishful_simple_agent.py --config rx1_config.yaml > rx1.log &" & 
        ssh kistm@nuc8 "cd /root/gr-hydra/apps/wishful_control/ && ./wishful_simple_agent.py --config rx2_config.yaml > rx2.log &"  &
        ssh kistm@nuc5 "cd /root/gr-hydra/apps/wishful_control/ && ./wishful_simple_agent.py --config tx_config.yaml > tx.log &" &

        pushd /root/gr-hydra/apps/wishful_control/ ; ./wishful_simple_controller.py
        

        ;;

    *)
        echo "Usage: $0 [stop|start|restart]"
    ;;

esac

