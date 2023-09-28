REACT howto on wilab2

#EMULAB experiment link (atlas)
 https://www.wilab2.ilabt.iminds.be/showexp.php3?pid=cognitiveradio&eid=atlas

#experiment nodes
 CONTROLLER
 nodezotach4,ath9k,10.11.16.39,5180,1,192.168.0.1,00:0e:8e:30:9e:ce,A

 NODES
 nodezotacb4,ath9k,10.11.16.33,5180,1,192.168.0.2,mac_address,B
 nodezotacd3,ath9k,10.11.16.24,5180,3,192.168.0.3,mac_address,C
 nodezotack4,ath9k,10.11.16.42,5180,1,192.168.0.6,mac_address,F
 nodezotach1,ath9k,10.11.16.7,5180,1,192.168.0.1,00:0e:8e:30:9e:ce,A
 nodezotach2,ath9k,10.11.16.17,5180,3,192.168.0.2,00:0e:8e:30:9e:dc,B
 nodezotach3,ath9k,10.11.16.28,5180,3,192.168.0.3,00:0e:8e:30:9d:ee,C
 nodezotacb3,ath9k,10.11.16.22,5180,3,192.168.0.4,00:0e:8e:30:9d:2d,D
 nodezotack3,ath9k,10.11.16.31,5180,3,192.168.0.5,00:0e:8e:30:9e:d8,E
 nodezotacc6,ath9k,10.11.16.53,5180,5,192.168.0.1,00:0e:8e:30:9c:af,A
 nodezotack6,ath9k,10.11.16.60,5180,8,192.168.0.3,00:0e:8e:30:9c:eb,C

 EXPERIMET NODES
 nodezotacd6,ath9k,10.11.16.54,5180,3,192.168.0.1,00:0e:8e:30:9c:ba,A
 nodezotacg6,ath9k,10.11.16.56,5180,3,192.168.0.2,00:0e:8e:30:9d:3c,B
 nodezotacj6,ath9k,10.11.16.59,5180,3,192.168.0.3,00:0e:8e:30:9c:ea,C
 nodezotacb1,ath9k,10.11.16.1,5180,3,192.168.0.4,00:0e:8e:30:9c:b3,D
 nodezotack1,ath9k,10.11.16.10,5180,3,192.168.0.5,00:0e:8e:30:9e:ea,E
 nodezotaci3,ath9k,10.11.16.29,5180,3,192.168.0.6,00:0e:8e:30:91:7b,F

#move files on wilab
 rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ./wishful-github-manifest-3/  -e ssh dgarlisi@ops.wilab2.ilabt.iminds.be:~/wishful-github-manifest-3/

#connect to nodes
 ssh dgarlisi@ops.wilab2.ilabt.iminds.be
  ssh dgarlisi@zotacd6
  ...
  ssh dgarlisi@zotach4

#move on experiment directory
 cd wishful-github-manifest-3/examples/react80211/

#sync clock nodes
 cd helper
 sh sync_date.sh dgarlisi zotacd6,zotacg6,zotacj6,zotacb1,zotack1,zotaci3
 cd ..

 NB: on wilab, we do not need deploy
  sh deploy_upis.sh dgarlisi zotacc6,zotacg6,zotack6

#setup nodes
 cd zotac-conf/scapy/ && sudo sh install_scapy.sh && cd ../../
 cd zotac-conf/athmodules/ && sudo sh install_module.sh && cd ../../

#start agent
 sudo python3 react_agent --config agent_cfg_wilab_ptestbed.yaml

#controller (39 --> CONTROLLER)
 sudo python3 react_controller --config controller_cfg_wilab2_zotach4.yaml --nodes node_info_wilab2_4hop.txt

#visualizer connect (39 --> CONTROLLER)
 ssh -L 8501:10.11.16.39:8501 dgarlisi@ops.wilab2.ilabt.iminds.be -v
 ssh -L 8500:10.11.16.39:8500 dgarlisi@ops.wilab2.ilabt.iminds.be -v

#visualizer
 python react_visualizer.py


REACT howto on portable testbed
#ON LOCAL STATION
 #connect to vpn
 sudo openvpn --config ~/Desktop/portable-testbed/portableTestbed.ovpn

 #run jFED
 jFed-Experimenter

 #add key to testbed nodes
 sh add_key.sh /home/domenico/.jFed/login-certs/0c5afa9805e0a3ed93a7ed6f627c8163.pem dgarlisi nuc1,nuc2,nuc3,nuc4,nuc5,nuc6

 #connect to nodes
 ssh nuc1 (ssh dgarlisi@172.16.16.1)
 ssh nuc2
 ssh nuc3
 ssh nuc4
 ssh nuc5
 ssh nuc6

 EXPERIMET NODES
 172.16.16.1,ath9k,172.16.16.1,5180,10,192.168.0.1,00:0e:8e:3b:23:41,A
 172.16.16.2,ath9k,172.16.16.2,5180,10,192.168.0.2,00:0e:8e:3b:23:cb,B
 172.16.16.3,ath9k,172.16.16.3,5180,10,192.168.0.3,00:0e:8e:3b:2c:8c,C
 172.16.16.4,ath9k,172.16.16.4,5180,10,192.168.0.4,00:0e:8e:3b:23:c4,D
 172.16.16.5,ath9k,172.16.16.5,5180,10,192.168.0.5,00:0e:8e:3b:20:84,E
 172.16.16.6,ath9k,172.16.16.6,5180,10,192.168.0.6,00:0e:8e:3b:21:ca,F

 rsync -avz --delete  --exclude agent_modules/wifi_ath/hmac --exclude examples --exclude '*.tar.gz' --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ./wishful-github-manifest-3/  -e ssh nuc6:~/wishful-github-manifest-3/
 ssh nuc6 'mkdir /users/dgarlisi/wishful-github-manifest-3/examples'
 rsync -avz --delete  --exclude apu-conf/ath10k-firmware --exclude zotac-conf/ath10k-firmware --exclude '*.tar.gz' --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' ./wishful-github-manifest-3/examples/react80211/  -e ssh nuc6:~/wishful-github-manifest-3/examples/react80211/


 #connect to controller(nuc6)
 ssh nuc6

#ON CONTROLLER (nuc6)
 #test ssh connection from controller
 ssh nuc1; exit
 ssh nuc2; exit
 ssh nuc3; exit
 ssh nuc4; exit
 ssh nuc5; exit

 #move on experiment directory
 cd wishful-github-manifest-3/examples/react80211/ (helper)

 #sync clock nodes
 sh sync_date.sh dgarlisi nuc1,nuc2,nuc3,nuc4,nuc5
 sh deploy_upis.sh dgarlisi nuc1,nuc2,nuc3,nuc4,nuc5


#ON TESTBED NODES
 sudo vim /etc/default/crda
  add BE
 sudo ifconfig wlan0 down
 sudo ifconfig wlan0 up
 sudo ifconfig wlan0 down
 sudo iw reg get
 country 00:
     (2402 - 2472 @ 40), (3, 20)
     (2457 - 2482 @ 40), (3, 20), PASSIVE-SCAN, NO-IBSS
     (2474 - 2494 @ 20), (3, 20), NO-OFDM, PASSIVE-SCAN, NO-IBSS
     (5170 - 5250 @ 40), (3, 20), PASSIVE-SCAN, NO-IBSS
     (5735 - 5835 @ 40), (3, 20), PASSIVE-SCAN, NO-IBSS
 sudo iw reg set BE
 sudo ifconfig wlan0 down
 sudo ifconfig wlan0 up
 sudo iw reg get
 country BE:
     (2402 - 2482 @ 40), (N/A, 20)
     (5170 - 5250 @ 40), (N/A, 20)
     (5250 - 5330 @ 40), (N/A, 20), DFS
     (5490 - 5710 @ 40), (N/A, 27), DFS
     (57240 - 65880 @ 2160), (N/A, 40), NO-OUTDOOR
 sudo ifconfig wlan0 down
 sudo iwconfig wlan0 mode ad-hoc
 sudo iwconfig wlan0 channel 36
 sudo ifconfig wlan0 up
 iwconfig

 #move on experiment directory
 cd wishful-github-manifest-3/examples/react80211/

 #setup nodes
 cd zotac-conf/scapy/ && sudo sh install_scapy.sh && cd ../../

 #start agent
 sudo python3 react_agent --config agent_cfg_wilab_ptestbed.yaml

#ON CONTROLLER
 #controller (6 --> CONTROLLER)
 sudo python3 react_controller --config controller_cfg_ptestbed_nuc6.yaml --nodes node_info_ptestbed_3chain.txt
 sudo python3 react_controller --config controller_cfg_ptestbed_nuc6.yaml --nodes node_info_ptestbed_5chain.txt

#ON LOCAL STATION
 #visualizer connect (6 --> CONTROLLER)
 ssh -L 8600:127.0.0.1:8600 nuc6 -v
 ssh -L 8601:127.0.0.1:8601 nuc6 -v

 #visualizer
 python react_visualizer.py

