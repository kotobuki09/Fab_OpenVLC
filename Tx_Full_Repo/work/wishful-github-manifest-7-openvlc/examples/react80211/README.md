Wishful REACT demo showcase
============================

### REACT how-to on w-ilab.t

### 0. Reserve and swap in the experiment
 EMULAB experiment link (atlas)
 https://www.wilab2.ilabt.iminds.be/showexp.php3?pid=cognitiveradio&eid=atlas
 
### 1. run the showcase 
 CONTROLLER
 nodezotach4,ath9k,10.11.16.39,5180,1,192.168.0.1,00:0e:8e:30:9e:ce,A
 
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
  sh sync_date.sh dgarlisi 10.11.16.17,10.11.16.7,10.11.16.2
  sh sync_date.sh dgarlisi zotacc6,zotacg6,zotack6,zotacb1,zotack1,zotaci3

 NB: on wilab, we do not need deploy
  sh deploy_upis.sh dgarlisi zotacc6,zotacg6,zotack6


#setup nodes
cd zotac-conf/scapy/ && sudo sh install_scapy.sh && cd ../../
cd zotac-conf/athmodules/ && sudo sh install_module.sh && cd ../../

#start agent
sudo python3 react_agent --config agent_cfg_wilab.yaml

#controller (39 --> CONTROLLER)
sudo python3 react_controller --config controller_cfg_wilab2.yaml --nodes node_info_wilab2_full.txt
sudo python3 react_controller --config controller_cfg_wilab2_zotach4.yaml --nodes node_info_wilab2_3chain.txt

#visualizer connect (39 --> CONTROLLER)
ssh -L 8401:10.11.16.39:8401 dgarlisi@ops.wilab2.ilabt.iminds.be -v
ssh -L 8400:10.11.16.39:8400 dgarlisi@ops.wilab2.ilabt.iminds.be -v

ssh -L 8400:127.0.0.1:8400 dgarlisi@nuc1 -v
ssh -L 8401:127.0.0.1:8401 dgarlisi@nuc1 -v
sudo openvpn --config ~/Desktop/portable-testbed/portableTestbed.ovpn

#visualizer
python react_visualizer.py
