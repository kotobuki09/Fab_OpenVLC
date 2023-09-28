Wishful FINAL SHOWCASE Network WiFi
============================

### network WiFi how-to on portable testbed

    ssh dgarlisi@nuc12
        cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/ad_controller/
            python3 ./controller

    ssh dgarlisi@nuc12
        cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_wifi/solution_wifi_ct/
            ex -sc $"%s/\r$//e|x" start_wifi_network.sh
            bash start_wifi_network.sh

    ~~~~
    #start USRP channel trace visualizer on web portal
    ~~~~
    ssh dgarlisi@nuc12
        cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal
            sudo bash run_usrp.sh 6

    http://172.16.16.12/WishfulWebPortal/only_usrp.html


## run separated command
 #deploy experiment files
    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh dgarlisi@172.16.16.11:/groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/

 #CONTROLLER
    nuc12

 #EXPERIMET NODES
    alix04,b43,172.16.16.31,2437,20,192.168.0.4,00:14:a5:e9:0c:74,A,AP,wlan0
    alix05,b43,172.16.16.32,2437,20,192.168.0.5,00:14:a4:62:c8:21,B,STA,wlan0

 #deploy directory on nodes
 #sync clock nodes
     cd helper
     ex -sc $'%s/\r$//e|x' deploy_upis.sh
     sh deploy_upis.sh root alix04,alix05  #deploy framework on alixnodes
     ex -sc $'%s/\r$//e|x' sync_date.sh
     sh sync_date.sh root alix04,alix05  #sync nodes time
     cd ..

 #Solution Global Controller
    python3 ./controller

 #Solution
    ssh dgarlisi@nuc12
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_wifi/solution_wifi_ct/
    python3 controller_wifi --config controller_cfg_nuc12.yaml --nodes node_info.txt

    ~~~~
    #start agent
    ~~~~
    ssh root@alix04
    cd ~/wishful-github-manifest/final_showcase/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_ap.yaml

    ssh root@alix05
    cd ~/wishful-github-manifest/final_showcase/network_wifi/solution_wifi_ct
    python3 agent --config agent_cfg_sta.yaml

    ~~~~


 #Start LTE traffic
    iperf -c 127.0.0.1 -p 2000 -i 1 -t 10000

 #Change LTE pattern
    python set_tx_lte_pattern.py -w "1,0,0,1,1,1,1,1,0,0"
        ('UDP target IP:', '127.0.0.1')
        ('UDP target port:', 8888)
        1,0,0,1,1,1,1,1,0,0


~~~~
#start USRP
~~~~
ON USRP : http://10.8.8.22/login.html (ttilab)

ssh clapton
cd ~/work/usrp_acquire/python-usrp-tracker-v2/pyUsrpTracker
sudo sh run_usrp.sh 6
http://10.8.9.3/crewdemo/plots/usrp.png

ON ZIGBEE : http://10.8.8.22/login.html (ttilab)


##hosts file
172.16.16.31    alix04
172.16.16.32    alix05
