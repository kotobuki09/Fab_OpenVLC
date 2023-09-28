Warm-up phase - Overlapping BSS Management (OBSSM)
==================================================

Start WiSHFUL Controller and Agents
-----------------------------------

0. Login as root to following nodes (passwd: root):

		ssh root@172.16.16.2
		ssh root@172.16.16.4
		ssh root@172.16.16.9
		ssh root@172.16.16.10

1. Start AD WiSHFUL controller on nuc9:

		/home/piotr/wishful/final_showcase/wifi_warmup/scripts/start_ad.sh

2. Start WiSHFUL controller on nuc9 (arg = IP address of AD controller):

		/home/piotr/wishful/final_showcase/wifi_warmup/scripts/start_controller0.sh 172.16.16.9

3. Start AP0 WiSHFUL agent on nuc9:

		sudo -s
		/home/piotr/wishful/final_showcase/wifi_warmup/scripts/start_ap0.sh

4. Start STA0 WiSHFUL agent on nuc10:
		
		sudo -s
		/home/piotr/wishful/final_showcase/wifi_warmup/scripts/start_sta0.sh

5. Start WiSHFUL controller on nuc4 (arg = IP address of AD controller):

		/home/piotr/wishful/final_showcase/wifi_warmup/scripts/start_controller1.sh 172.16.16.9

6. Start AP1 WiSHFUL agent on nuc4:

		sudo -s
		/home/piotr/wishful/final_showcase/wifi_warmup/scripts/start_ap1.sh

7. Start STA1 WiSHFUL agent on nuc2:
		
		sudo -s
		/home/piotr/wishful/final_showcase/wifi_warmup/scripts/start_sta1.sh


AD controller commands
----------------------

1. After starting all WiSHFUL controllers and agents, the following networks should be registered in AD contoller:

* WIFI_A1
* WIFI_A2

2. Both networks expose the following commands:

* ACTIVATE - start network (i.e. all APs and STAs are setup)
* DEACTIVATE - stop network (i.e. all APs and STAs are switched off)
* TRAFFIC_SET_OFF - disable iperf traffic from AP to STA
* TRAFFIC_SET_LOW - set low traffic from AP to STA (i.e. 1 Mbps)
* TRAFFIC_SET_MEDIUM - set medium traffic from AP to STA (i.e. 20 Mbps)
* TRAFFIC_SET_HIGH - set medium traffic from AP to STA (i.e. 100 Mbps)
* TRAFFIC - set traffic from AP to STA, type (LOW/MEDIUM/HIGH) is given as argument
* SWITCH_CHANNEL - switch channel of WiFi BSS, new channel is given as argument
