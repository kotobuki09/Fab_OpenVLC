Wishful final showcase
============================

### Showcase Phases

Only 1 Administrative Domain present with multiple Wi-Fi deployments to enable the use of the Wi-Fi air time management type of showcases if needed. TUB.e
    Phase 1: LTE added as interferer, CNIT.d (if blank subframes are enabled) , TUB.b, IMEC.a
    Phase 2: (LTE WiSHFUL enabled added, LTE interferer removed) LTE added in 1st AD. (LTE-WIFI coexistence)  TUB.d , CNIT.d, (if collaboration challenge exist)
Phase 3: ADD 2nd Second AD.
    First AD IMEC ZB, 2nd AD TCD virtualized OFDM based networks (frequency separation ? cooperation on the 2.4 GHz band,  blacklisting) IMEC.a, TCD.b

![alt text](https://github.com/wishful-project/final_showcase/blob/master/final-showcase-architecture.jpg)

### Showcase Architecture

The repository is organized with a different directory for each solution, moreover there are three additional directories, solution_global controller, showcase_GUI and lib.


### How work the solution global controller

The paradigm of communication between a generic solution and the solution global controller has two different phases.
    Phase 1: The solutions use a request/reply format to register them on solution global controller ( the following information
    are required for the registration procedure: Name; monitorList; commandList; eventList;).
    Phase 2: The solutions use a request/reply format to send monitor information and event detected to the solution global controller.
    The solution global controller uses the PUB/SUB to send command to the solutions.

The solutions are registered in the solutionCompatibilityMatrix map, we add also eventually conflict between the solutions in order to
use this information in the main logic of the solution global controller. The main logic of the solution global controller waiting for
receiving a monitor/event report, the solution global controller checks the solution compatibility matrix, in order to understand eventually conflict,
and send update/command to solutions. Example: when it receives the report of detecting interference (LTE),
sends activation command to solution TDMA cross interference, if not conflict are detected.

![alt text](https://github.com/wishful-project/final_showcase/blob/master/solution-global-controller-main-logic.jpg)

### how-to showcase activation on portable testbed

### 1. involved nodes 
172.16.16.12 nuc12 --> AD controller + wifi controller + lte controller + USRP channel acquire + webui
172.16.16.11 nuc11 --> LTE ENB
172.16.16.6 nuc6   --> LTE UE

### 2. run the showcase 
Wishful final showcase start howto
============================

CONTROLLER
==================================================
    ssh dgarlisi@172.16.17.2
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/ad_controller
    python3 ./controller_v3

WEBUI
==================================================
    ssh dgarlisi@172.16.17.2
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/webui/
    sudo pipenv shell bokeh serve --allow-websocket-origin="*:5006" wishful
    http://172.16.17.2:5006/wishful

Warm-up phase - Overlapping BSS Management (OBSSM)
==================================================
    2. Start WiSHFUL controller on nuc9 (arg = IP address of AD controller):
        ssh piotr@172.16.16.9
        sudo su
		/home/piotr/wishful/final_showcase/wifi_warmup/scripts/start_controller0.sh 172.16.17.2

    3. Start AP0 WiSHFUL agent on nuc9:
        ssh piotr@172.16.16.9
        sudo su
		/home/piotr/wishful/final_showcase/wifi_warmup/scripts/start_ap0.sh

    4. Start STA0 WiSHFUL agent on nuc10:
		ssh piotr@172.16.16.10
		sudo su
		/home/piotr/wishful/final_showcase/wifi_warmup/scripts/start_sta0.sh

    5. Start WiSHFUL controller on nuc4 (arg = IP address of AD controller):
        ssh piotr@172.16.16.4
        sudo su
		/home/piotr/wishful/final_showcase/wifi_warmup/scripts/start_controller1.sh 172.16.17.2

    6. Start AP1 WiSHFUL agent on nuc4:
        ssh piotr@172.16.16.4
        sudo su
		/home/piotr/wishful/final_showcase/wifi_warmup/scripts/start_ap1.sh

    7. Start STA1 WiSHFUL agent on nuc2:
		ssh piotr@172.16.16.2
		/home/piotr/wishful/final_showcase/wifi_warmup/scripts/start_sta1.sh

ZigBee network
==================================================
    ssh dgarlisi@172.16.16.3
    cd /groups/portable-ilabt-imec-be/wish/imec/wishful/
    source ./dev/bin/activate
    cd final_showcase/network_zigbee
    python agent.py --config config/portable/agent_config.yaml
    
    ssh dgarlisi@172.16.16.3
    cd /groups/portable-ilabt-imec-be/wish/imec/wishful/
    source ./dev/bin/activate
    cd final_showcase/network_zigbee
    python global_controller.py --config config/portable --solution_controller 172.16.17.2

WiPLUS - LTE-U detector
==========================================
    1. Start WiPLUS detector controller on nuc1:
        ssh piotr@172.16.16.1
        sudo su
		/home/piotr/wishful/final_showcase/spectrum_monitoring_service/solution_interference_classifier/scripts/start_wiplus.sh 172.16.17.2

    2. Start LTE-U BS controller on nuc2:
        ssh piotr@172.16.16.2
        sudo su
        uhd_usrp_probe
		/home/piotr/wishful/final_showcase/spectrum_monitoring_service/solution_interference_classifier/scripts/start_lte_u_bs.sh 172.16.17.2

LTE-U  TDMA 
==========================================
    ssh dgarlisi@nuc12
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_lte/solution_lte_ct
    python3 controller_lte --config controller_cfg_nuc12.yaml --nodes node_info.txt

    ssh dgarlisi@nuc11
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_lte/solution_lte_ct
    python3 agent_tx.py

    ssh dgarlisi@nuc6
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_lte/solution_lte_ct
    python3 agent_rx.py

    
WiFI  TDMA 
==========================================
    """
     cd helper
     ex -sc $'%s/\r$//e|x' deploy_upis.sh
     sh deploy_upis.sh root alix04,alix05  #deploy framework on alixnodes
     ex -sc $'%s/\r$//e|x' sync_date.sh
     sh sync_date.sh root alix04,alix05  #sync nodes time
     cd ..
    """

    ssh dgarlisi@nuc12
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_wifi/solution_wifi_ct/
    python3 controller_wifi --config controller_cfg_nuc12.yaml --nodes node_info.txt

    ssh root@alix04
    cd ~/wishful-github-manifest/final_showcase/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_ap.yaml

    ssh root@alix05
    cd ~/wishful-github-manifest/final_showcase/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_sta.yaml
    
Wishful FINAL SHOWCASE network_virtual_radio
==========================================
    ssh kistm@172.16.16.5
    2. Move to final_showcase/network_virtual_radio folder:
            cd /root/wishful/final_showcase/network_virtual_radio
    3. Execute the script to start the 3 GNURadio WiSHFUL agents + virtual radio controller:
            ./start_virtual_radio_network.sh start
    4. Make sure the AD controller is running. If it is not running, the previous command will not print any message on screen.
    5. Send a "START_LTE" or "START_NBIOT" command from the AD controller to the Virtual Radio Network controller.
    

Monitor service - interference detection
==========================================
    ssh dgarlisi@nuc11
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/spectrum_monitoring_service/solution_interference_detection/
    sudo python3 controller --config controller_cfg_nuc11.yaml --nodes node_info.txt

USRP channel trace visualizer on web portal
==========================================
    ssh dgarlisi@nuc12
    cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal
    sudo bash run_usrp.sh 11

    http://172.16.16.12/WishfulWebPortal/only_usrp.html

generic command
==========================================
    sudo ntpdate -u it.pool.ntp.org
    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh dgarlisi@172.16.17.2:/groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/
    sudo ps aux | grep usrp |  awk '{print $2}' | xargs kill -9
    ssh-agent bash
    ssh-add .ssh/id_rsa
    DISPLAY=:0 terminator -l finalshowcasecnitad &
    DISPLAY=:0 terminator -l finalshowcasenode2 &


## Acknowledgement

The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).