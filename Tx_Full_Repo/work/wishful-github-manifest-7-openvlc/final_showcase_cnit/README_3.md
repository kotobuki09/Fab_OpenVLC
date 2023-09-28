CNIT Wishful final showcase
============================




Deterministic Backoff
============================

### 1. involved nodes 
 #EXPERIMET NODES
    alix02,b43,10.8.8.102,2437,20,192.168.0.2,00:14:a4:62:c8:1a,A,AP,wlan0
    alix03,b43,10.8.8.103,2437,20,192.168.0.3,00:14:a5:e9:12:7c,B,STA,wlan0
    alix11,b43,10.8.8.111,2437,20,192.168.0.11,00:14:a4:62:c8:24,C,STA,wlan0
    alix14,b43,10.8.8.114,2437,20,192.168.0.14,00:14:a5:e9:0e:72,D,STA,wlan0
    alix15,b43,10.8.8.115,2437,20,192.168.0.15,00:14:a5:b3:da:be,E,STA,wlan0

rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh 10.8.9.14:~/wishful-github-manifest-7/


WEBUI
==================================================
    ssh 10.8.9.14
    cd wishful-github-manifest-7/final_showcase_cnit/webui/
    sudo pipenv shell bokeh serve --allow-websocket-origin="*:5006" gui_det
    bokeh serve --allow-websocket-origin="*:5006" gui_det
    http://127.0.0.1:5006/gui_det


CONTROLLER
==================================================
    ssh 10.8.9.14
    cd wishful-github-manifest-7/final_showcase_cnit/ad_controller
    python3 ./controller_v3


WiFI  TDMA 
==========================================

 #deploy directory on nodes
     ssh 10.8.9.13
     cd wishful-github-manifest-7/final_showcase_cnit/network_wifi/solution_wifi_ct/helper
     cd helper
     ex -sc $'%s/\r$//e|x' deploy_upis.sh
     sh deploy_upis.sh root alix02,alix03,alix07,alix11,alix14  #deploy framework on alixnodes
     sh deploy_upis.sh domenico 10.8.9.13

 #sync clock nodes
     ex -sc $'%s/\r$//e|x' sync_date.sh
     sh sync_date.sh root alix02,alix03,alix07,alix11,alix14  #sync nodes time
     cd ..

    
    ~~~~
    #start agent
    ~~~~   

    ssh root@alix02
    cd ~/wishful-github-manifest/final_showcase/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_ap.yaml
    
    ssh root@alix03
    ssh root@alix07
    ssh root@alix11
    ssh root@alix14 
    cd ~/wishful-github-manifest/final_showcase/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_sta_det.yaml

    
    
    ~~~~
    #start controller
    ~~~~
    ssh 10.8.9.13
    cd wishful-github-manifest-7/final_showcase_cnit/network_wifi/solution_wifi_ct/
    python3 controller_wifi_det --config controller_cfg_nuc1.yaml --nodes node_info_det.txt
    ~~~~




LTE / WiFi Cooperation
============================

### 1. involved nodes 
10.8.9.13 LTE TX 
10.8.9.14 LTE RX +AD controller + USRP channel acquire + webui
rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh 10.8.9.14:~/wishful-github-manifest-7/



WEBUI
==================================================
    ssh 10.8.9.14
    cd wishful-github-manifest-7/final_showcase_cnit/webui/
    sudo pipenv shell bokeh serve --allow-websocket-origin="*:5006" gui_coop
    bokeh serve --allow-websocket-origin="*:5006" gui_coop
    http://127.0.0.1:5006/gui_coop


CONTROLLER
==================================================
    ssh 10.8.9.14
    cd wishful-github-manifest-7/final_showcase_cnit/ad_controller
    python3 ./controller_v3


TE-U  TDMA 
==========================================
    ssh 10.8.9.13
    ssh nuc1
        cd wishful-github-manifest-7/final_showcase_cnit/network_lte/solution_lte_ct
        python3 agent_tx.py


    ssh 10.8.9.14
    ssh nuc2
        cd wishful-github-manifest-7/final_showcase_cnit/network_lte/solution_lte_ct
        python3 agent_rx.py

    CONTROLLER
    ssh 10.8.9.13
        cd wishful-github-manifest-7/final_showcase_cnit/network_lte/solution_lte_ct
        python3 controller_lte --config controller_cfg_nuc_ttilab.yaml --nodes node_info.txt


WiFI  TDMA 
==========================================

 #EXPERIMET NODES
    alix02,b43,10.8.8.102,2437,20,192.168.0.2,00:14:a4:62:c8:1a,A,AP,wlan0
    alix03,b43,10.8.8.103,2437,20,192.168.0.3,00:14:a5:e9:12:7c,B,STA,wlan0
    alix11,b43,10.8.8.111,2437,20,192.168.0.11,00:14:a4:62:c8:24,C,STA,wlan0
    alix14,b43,10.8.8.114,2437,20,192.168.0.14,00:14:a5:e9:0e:72,D,STA,wlan0
    alix15,b43,10.8.8.115,2437,20,192.168.0.15,00:14:a5:b3:da:be,E,STA,wlan0

 #deploy directory on nodes
 #sync clock nodes
     ssh 10.8.9.13
     cd wishful-github-manifest-7/final_showcase_cnit/network_wifi/solution_wifi_ct/helper
     cd helper
     ex -sc $'%s/\r$//e|x' deploy_upis.sh
     sh deploy_upis.sh root alix02,alix03,alix07,alix11,alix14  #deploy framework on alixnodes
     sh deploy_upis.sh domenico 10.8.9.13
     
     ex -sc $'%s/\r$//e|x' sync_date.sh
     sh sync_date.sh root alix02,alix03,alix07,alix11,alix14  #sync nodes time
     cd ..

    """
     cd helper
     ex -sc $'%s/\r$//e|x' deploy_upis.sh
     sh deploy_upis.sh root alix04,alix05  #deploy framework on alixnodes
     ex -sc $'%s/\r$//e|x' sync_date.sh
     sh sync_date.sh root alix04,alix05  #sync nodes time
     cd ..
    """


    """
     cd helper
     ex -sc $'%s/\r$//e|x' deploy_upis.sh
     sh deploy_upis.sh root alix02,alix03,alix07,alix11,alix14  #deploy framework on alixnodes
     ex -sc $'%s/\r$//e|x' sync_date.sh
     sh sync_date.sh root alix02,alix03,alix07,alix11,alix14  #sync nodes time
     cd ..
    """
    
    ~~~~
    #start agent
    ~~~~   
    ssh root@alix02
    cd ~/wishful-github-manifest/final_showcase_cnit/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_ap.yaml
    
    ssh root@alix14
    cd ~/wishful-github-manifest/final_showcase_cnit/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_sta.yaml
    ~~~~

    ssh root@alix02
    cd ~/wishful-github-manifest/final_showcase/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_ap.yaml
    
    ssh root@alix03
    ssh root@alix07
    ssh root@alix11
    ssh root@alix14 
    cd ~/wishful-github-manifest/final_showcase/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_sta_det.yaml

    
    
    ~~~~
    #start controller
    ~~~~
    ssh 10.8.9.13
    cd wishful-github-manifest-7/final_showcase_cnit/network_wifi/solution_wifi_ct/
    python3 controller_wifi_det --config controller_cfg_nuc1.yaml --nodes node_info_det.txt
    ~~~~

    ~~~~
    ssh 10.8.9.13
    cd wishful-github-manifest-7/final_showcase_cnit/network_wifi/solution_wifi_ct/helper
    python3 controller_wifi --config controller_cfg_nuc1.yaml --nodes node_info.txt


    ssh dgarlisi@nuc12
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_wifi/solution_wifi_ct/
    python3 controller_wifi --config controller_cfg_nuc12.yaml --nodes node_info.txt

    ssh root@alix04
    cd ~/wishful-github-manifest/final_showcase/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_ap.yaml

    ssh root@alix05
    cd ~/wishful-github-manifest/final_showcase/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_sta.yaml
    
    
    
   
    
Monitor service - interference detection
==========================================
     cd helper
     ex -sc $'%s/\r$//e|x' deploy_upis.sh
     sh deploy_upis.sh root alix12  #deploy framework on alixnodes
     ex -sc $'%s/\r$//e|x' sync_date.sh
     sh sync_date.sh root alix12  #sync nodes time
     cd ..


    ssh dgarlisi@nuc11
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/spectrum_monitoring_service/solution_interference_detection/
    sudo python3 controller --config controller_cfg_nuc11.yaml --nodes node_info.txt
    
    
    ssh root@alix12
    cd ~/wishful-github-manifest/final_showcase_cnit/spectrum_monitoring_service/solution_interference_detection
    sudo python3 agent --config agent_cfg_sta_mon.yaml
    
    ssh 10.8.9.13
    cd ~/wishful-github-manifest-7/final_showcase_cnit/spectrum_monitoring_service/solution_interference_detection
    python3 controller_error --config controller_cfg_nuc1.yaml --nodes node_info.txt
    
    ssh root@alix12
    cd ~/wishful-github-manifest/final_showcase_cnit/spectrum_monitoring_service/solution_interference_detection/helper
    sudo python b43-fwdump-ann
    
    

USRP channel trace visualizer on web portal
==========================================
    ssh dgarlisi@nuc12
    cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal
    sudo bash run_usrp.sh 11

    http://172.16.16.12/WishfulWebPortal/only_usrp.html
    http://127.0.0.1:8001/WishfulWebPortal/only_usrp.html
    
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