Wishful FINAL SHOWCASE Interference detection
============================

### network WiFi how-to on portable testbed

    ssh dgarlisi@nuc12
        cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/ad_controller/
            python3 ./controller

    ssh dgarlisi@nuc11
        cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/spectrum_monitoring_service/solution_interference_detection/
               sudo python3 controller --config controller_cfg_nuc11.yaml --nodes node_info.txt


    ~~~~
    #start USRP channel trace visualizer on web portal
    ~~~~
    ssh dgarlisi@nuc12
        cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal
            sudo bash run_usrp.sh 6

    http://172.16.16.12/WishfulWebPortal/only_usrp.html
    
#deploy experiment files
    cd /mnt/d/ownCloud/wishful-framework-cnit/wishful-github-manifest-7/final_showcase/
    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh dgarlisi@172.16.16.11:/groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/

    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh 10.8.9.13:~/wishful-github-manifest-7/

    
    #Start CNIT_MONITOR_SERVICE  (SHELL 4) (need AD controller activated):

    ssh dgarlisi@nuc11
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/spectrum_monitoring_service/solution_interference_detection/
    sudo python3 controller --config controller_cfg_nuc11.yaml --nodes node_info.txt
    
    
    sudo pip3 install sklearn
    sudo pip3 install scipy
    
    
    sudo su
    
    echo "0x8048" > /sys/kernel/debug/ieee80211/phy0/ath9k/regidx
    echo "0x42000000" >  /sys/kernel/debug/ieee80211/phy0/ath9k/regval
    echo "0x8048" > /sys/kernel/debug/ieee80211/phy2/ath9k_htc/regidx
    echo "0x42000000" >  /sys/kernel/debug/ieee80211/phy2/ath9k_htc/regval
    echo "0x8048" > /sys/kernel/debug/ieee80211/phy1/ath9k/regidx
    echo "0x42000000" >  /sys/kernel/debug/ieee80211/phy1/ath9k/regval
