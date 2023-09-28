WiPLUS - LTE-U detector
==========================================

Start WiSHFUL Controller and Agents
-----------------------------------

0. Login as root to following nodes (passwd: root):

		ssh root@172.16.16.1
		ssh root@172.16.16.2

1. Start WiPLUS detector controller on nuc1:

		sudo -s

		# After reboot modified ath9k driver has to be started:
		# IMPORTANT: do not install those modules, as it might cause problems with booting of NUC

		# Stop default driver
		/home/piotr/demo/myrmmod.sh

		# Start modified driver (takes around 15s)
		/home/piotr/demo/myinsmod.sh

		# Start WiPLUS detector
		/home/piotr/wishful/final_showcase/spectrum_monitoring_service/solution_interference_classifier/scripts/start_wiplus.sh 172.16.16.9

2. Start LTE-U BS controller on nuc2:

		sudo -s
		/home/piotr/wishful/final_showcase/spectrum_monitoring_service/solution_interference_classifier/scripts/start_lte_u_bs.sh 172.16.16.9

AD controller commands
----------------------

1. After starting all WiSHFUL controllers and agents, the following network should be registered in AD contoller:

* NON_WISHFUL_LTE_U
* WIPLUS_LTE_U_DETECTOR

2. The NON_WISHFUL_LTE_U network exposes the following commands:

* ACTIVATE - start srsLTE LTE-U BS, center frequency can be given as arg, default is 2412MHz (i.e. WiFI channel 1)
* DEACTIVATE - stop srsLTE LTE-U BS
* SET_FREQ - change center frequency of LTE-U BS

3. The WIPLUS_LTE_U_DETECTOR network does not exposes any commands, as it is always reporting its measurements.
