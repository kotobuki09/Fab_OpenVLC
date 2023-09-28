Wishful FINAL SHOWCASE solution_lte_ct
============================

### network_lte how-to on portable testbed

    ssh dgarlisi@nuc12
        cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/ad_controller/
            python3 ./controller

    ssh dgarlisi@nuc12
        cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_lte/solution_lte_ct/
            ex -sc $"%s/\r$//e|x" start_lte_network.sh
            bash start_lte_network.sh

~~~~
#start USRP channel trace visualizer on web portal
~~~~

    ssh dgarlisi@nuc12
        cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal
            sudo bash run_usrp.sh 11

    http://172.16.16.12/WishfulWebPortal/only_usrp.html


 ## run separated command

 #deploy experiment files
    cd /mnt/d/ownCloud/wishful-framework-cnit/wishful-github-manifest-7/final_showcase/
    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh dgarlisi@172.16.16.11:/groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/

    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh 10.8.9.13:~/wishful-github-manifest-7/

 #CONTROLLER
    nuc12

 #EXPERIMET NODES
    nuc11,lte,172.16.16.11,2412,20,192.168.0.1,f4:4d:30:6c:63:a3,D,EB,eth0

 #deploy directory on nodes
 #sync clock nodes
    cd helper
     ex -sc $'%s/\r$//e|x' sync_date.sh
     sh sync_date.sh root alix04,alix05  #sync nodes time
     sh sync_date.sh dgarlisi nuc11,nuc6
     cd ..

 #Solution Global Controller
    python3 ./controller

 #Solution
    ~~~~
    #start agent
    ~~~~
    ssh root@alix03
    python3 agent --config agent_cfg_sta_mon.yaml
    ssh root@alix04
    python3 agent --config agent_cfg_ap.yaml
    ssh root@alix05
    python3 agent --config agent_cfg_sta.yaml
    
    ssh nuc11
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_lte/solution_lte_ct
    python3 agent_tx.py

    ssh nuc6
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_lte/solution_lte_ct
    python3 agent_rx.py

    python3 controller_lte --config controller_cfg_clapton.yaml --nodes node_info.txt
    python3 controller_lte --config controller_cfg_nuc12.yaml --nodes node_info.txt
    python3 controller_lte --config controller_cfg_nuc_ttilab.yaml --nodes node_info.txt


    ~~~~

 #Start LTE traffic
    ./srsLTE/build/srslte/examples/pdsch_enodeb -f 2462000000 -p 25 -w 1,1,1,1,1,1,1,0,0,0 -b f -g 78 -l 0.7 -m 4 -u 2000
    iperf -c 127.0.0.1 -p 2000 -i 1 -t 10000

 #Change LTE pattern
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_lte/solution_lte_ct
    python3 set_tx_lte_pattern.py -w 1010101010
    
 #Start LTE UE 
    ./srsLTE/build/srslte/examples/pdsch_ue -f 2437e6 -r 1234 -u 2001 -U 127.0.0.1 -H 127.0.0.1
    ./srsLTE/build/srslte/examples/pdsch_ue -f 2437e6 -r 1234 -u 2001 -U 127.0.0.1 -H 172.16.16.12
    iperf -s -p 2001 -i 1

 #webui
     sudo pip install pipenv
     sudo apt-get install software-properties-common
     sudo add-apt-repository ppa:deadsnakes/ppa
     sudo apt-get update
     sudo apt-get install python3.6
     sudo pip install bokeh
     sudo rm /usr/bin/python3
     sudo ln -s /usr/bin/python3.6 /usr/bin/python3

     
     #not needed
     pipenv install
     pipenv --python /usr/bin/python3.6
     
     
     ssh dgarlisi@172.16.17.2
     #start the virtual environment and the server
     move to directory
         cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/webui/
     start server
         sudo pipenv shell bokeh serve --allow-websocket-origin="*:5006" wishful
     visualize GUI in browser
         http://172.16.17.2:5006/wishful
         
         
      python2 /home/tub/final_showcase/webui/usrp-ss/gr-specmon/usrp_pwr_fft.py -u serial=3143091 -c 2425e6 -b 50e6 -a tcp://localhost:5507
      python2 /home/tub/final_showcase/webui/usrp-ss/gr-specmon/usrp_pwr_fft.py -u serial=3143028 -c 2475e6 -b 50e6 -a tcp://localhost:5508
      
     
  #library collection
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/python3.6/config-3.6m-x86_64-linux-gnu
    sudo ldconfig
    sudo cp -r  /usr/local/lib/python3.5/dist-packages/iptc /usr/local/lib/python3.6/dist-packages/
    sudo pip3 install python_iptables
    python3 agent_tx.py
    sudo pip3 install pyroute2



