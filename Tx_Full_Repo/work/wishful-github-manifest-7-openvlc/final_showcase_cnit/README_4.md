CNIT Wishful final showcase
============================

rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh 10.8.9.14:~/wishful-github-manifest-7/
rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh dgarlisi@172.16.17.2:/groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/
rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh dgarlisi@172.16.16.12:/groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/
rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh dgarlisi@172.16.16.11:/groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/


Deterministic Backoff
============================

### 1. involved nodes 
 #EXPERIMET NODES
    alix04,b43,172.16.16.31,2437,20,192.168.0.4,00:14:a5:e9:0c:74,A,AP,wlan0
    alix05,b43,172.16.16.32,2437,20,192.168.0.5,00:14:a4:62:c8:21,B,STA,wlan0
    alixb4,b43,172.16.16.33,2437,20,192.168.0.6,00:19:7e:b3:d0:29,C,STA,wlan0
    alixb3,b43,172.16.16.34,2437,20,192.168.0.7,00:19:7e:b3:d0:29,D,STA,wlan0
    alix10,b43,172.16.16.36,2437,20,192.168.0.9,00:16:cf:3f:f6:3f,E,STA,wlan0


WEBUI
==================================================
    ssh dgarlisi@172.16.17.2
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase_cnit/webui/
    sudo pipenv shell bokeh serve --allow-websocket-origin="*:5006" gui_det
    bokeh serve --allow-websocket-origin="*:5006" gui_det
    http://172.16.17.2:5006/gui_det


CONTROLLER
==================================================
    ssh dgarlisi@172.16.17.2
    cd wishful-github-manifest-7/final_showcase_cnit/ad_controller
    python3 ./controller_v3


WiFI  TDMA 
==========================================
    ssh dgarlisi@nuc12
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase_cnit/network_wifi/solution_wifi_ct/helper
     #deploy directory on nodes
     cd helper
     ex -sc $'%s/\r$//e|x' deploy_upis.sh
     sh deploy_upis.sh root alix04,alix05,alixb4,alixb3,alix10  #deploy framework on alixnodes
     sh deploy_upis.sh root alix04,alix05,alixb4,alixb3,172.16.16.36  #deploy framework on alixnodes
     
     
     #sync clock nodes
     ex -sc $'%s/\r$//e|x' sync_date.sh
     sh sync_date.sh root alix04,alix05,alixb4,alixb3,alix10  #sync nodes time
     sh sync_date.sh root alix04,alix05,alixb4,alixb3,172.16.16.36  #sync nodes time
     cd ..

  
    ~~~~
    #start agent
    ~~~~   

    ssh root@alix04
    cd ~/wishful-github-manifest/final_showcase_cnit/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_ap.yaml
    
    ssh root@alix05
    ssh root@alixb4
    ssh root@alixb3
    ssh root@alixb6 
    cd ~/wishful-github-manifest/final_showcase_cnit/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_sta_det.yaml

        
    ~~~~
    #start controller
    ~~~~
    ssh dgarlisi@nuc12
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase_cnit/network_wifi/solution_wifi_ct/
    python3 controller_wifi_det --config controller_cfg_nuc12.yaml --nodes node_info_det_pt.txt
    ~~~~



LTE / WiFi Cooperation
============================

### 1. involved nodes 
10.8.9.13 LTE TX 
10.8.9.14 LTE RX +AD controller + USRP channel acquire + webui
rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh 10.8.9.14:~/wishful-github-manifest-7/



WEBUI
==================================================
    ssh dgarlisi@172.16.17.2
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase_cnit/webui/
    sudo pipenv shell bokeh serve --allow-websocket-origin="*:5006" gui_coop
    bokeh serve --allow-websocket-origin="*:5006" gui_coop
    http://172.16.17.2:5006/gui_coop

CONTROLLER
==================================================
    ssh dgarlisi@172.16.17.2
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase_cnit/ad_controller
    python3 ./controller_v3

LTE-U  TDMA 
==========================================
    ssh dgarlisi@nuc12
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase_cnit/network_lte/solution_lte_ct
    python3 controller_lte --config controller_cfg_nuc12.yaml --nodes node_info.txt

    ssh dgarlisi@nuc11
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase_cnit/network_lte/solution_lte_ct
    python3 agent_tx.py

    ssh dgarlisi@nuc6
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase_cnit/network_lte/solution_lte_ct
    python3 agent_rx.py

WiFI  TDMA 
==========================================

 #EXPERIMET NODES
    alix04,b43,172.16.16.31,2437,20,192.168.0.4,00:14:a5:e9:0c:74,A,AP,wlan0
    alix05,b43,172.16.16.32,2437,20,192.168.0.5,00:14:a4:62:c8:21,B,STA,wlan0
    
    ssh dgarlisi@nuc12
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase_cnit/network_wifi/solution_wifi_ct/
    python3 controller_wifi --config controller_cfg_nuc12.yaml --nodes node_info_pt.txt
     
     """
     cd helper
     #deploy directory on nodes
     ex -sc $'%s/\r$//e|x' deploy_upis.sh
     sh deploy_upis.sh root alix04,alix05  #deploy framework on alixnodes
     #sync clock nodes
     ex -sc $'%s/\r$//e|x' sync_date.sh
     sh sync_date.sh root alix04,alix05  #sync nodes time
     cd ..
     """

    ~~~~
    #start agent
    ~~~~   
    
    ssh root@alix04
    cd ~/wishful-github-manifest/final_showcase_cnit/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_ap.yaml

    ssh root@alix05
    cd ~/wishful-github-manifest/final_showcase_cnit/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_sta.yaml
    
   
    
Monitor service - interference detection
==========================================

    WiPLUS - LTE-U detector
    ==========================================
    ssh piotr@172.16.16.1
    sudo su
	/home/piotr/wishful/final_showcase/spectrum_monitoring_service/solution_interference_classifier/scripts/start_wiplus.sh 172.16.17.2

    Spectral Scan detector
    ==========================================
    ssh dgarlisi@nuc11
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase_cnit/spectrum_monitoring_service/solution_interference_detection/
    sudo python3 controller --config controller_cfg_nuc11.yaml --nodes node_info.txt

    Error sens
    ==========================================
     cd helper
     #deploy directory on nodes
     ex -sc $'%s/\r$//e|x' deploy_upis.sh
     sh deploy_upis.sh root 172.16.16.36  #deploy framework on alixnodes

    ssh dgarlisi@nuc11
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase_cnit/spectrum_monitoring_service/solution_interference_detection/
    python3 controller_error --config controller_cfg_nuc12.yaml --nodes node_info_pt.txt
    
    ssh root@172.16.16.36
    cd ~/wishful-github-manifest/final_showcase_cnit/spectrum_monitoring_service/solution_interference_detection
    sudo python3 agent --config agent_cfg_sta_mon.yaml
    
    ssh root@172.16.16.36
    cd ~/wishful-github-manifest/final_showcase_cnit/spectrum_monitoring_service/solution_interference_detection/helper
    sudo python b43-fwdump-ann
    
    
ZigBee network
==================================================
    ssh dgarlisi@172.16.16.5
    cd /groups/portable-ilabt-imec-be/wish/imec/wishful/
    source ./dev/bin/activate
    cd final_showcase/network_zigbee
    python agent.py --config config/portable/agent_config.yaml
    
    ssh dgarlisi@172.16.16.5
    cd /groups/portable-ilabt-imec-be/wish/imec/wishful/
    source ./dev/bin/activate
    cd final_showcase/network_zigbee
    python global_controller.py --config config/portable --solution_controller 172.16.17.2
        

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
    http://127.0.0.1:5006/wishful
    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh lab.tti.unipa.it:~/wishful-github-manifest-7/
    cp *.fw /mnt/d/ownCloud/wishful-framework-cnit/wishful-github-manifest-7/agent_modules/wifi_wmp/execution_engine/detfwwf/
    sudo ntpdate -u it.pool.ntp.org
    iwconfig wlan0 retry 0
    ssh-agent bash
    ssh-add .ssh/id_rsa
    DISPLAY=:0 terminator -l finalshowcasecnitad &
    DISPLAY=:0 terminator -l finalshowcasenode2 &
    DISPLAY=:0 terminator -l finalshowcasecnitdet &
    
    ps aux | grep controller_lte | awk '{print $2}' | xargs kill -9
    ps aux | grep controller_wifi | awk '{print $2}' | xargs kill -9
    ps aux | grep controller_wifi_det | awk '{print $2}' | xargs kill -9
    ps aux | grep pdsch_enodeb | awk '{print $2}' | xargs kill -9
    ps aux | grep iperf | awk '{print $2}' | xargs kill -9
    ps aux | grep bokeh | awk '{print $2}' | xargs kill -9
    
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_lte/solution_lte_ct
    python3 set_tx_lte_pattern.py -w 1010101010
    python3 set_tx_lte_pattern.py -w 1111111111

    tail -f wifi_thr_log.csv 
    iperf -s -i 1 -p 1234 -u  -f k  --reportstyle C > wifi_thr_log.csv
    
    sudo timedatectl set-timezone UTC
    sudo timedatectl set-timezone EST
    ssh -t 172.16.16.12 'cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal && sudo bash run_usrp.sh 11 &> /dev/null' &


## Acknowledgement

The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).