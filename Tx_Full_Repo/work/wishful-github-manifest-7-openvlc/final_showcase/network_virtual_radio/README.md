Wishful FINAL SHOWCASE network_virtual_radio
==========================================

1. Connect to nuc5

        ssh nuc5

2. Move to final_showcase/network_virtual_radio folder:

        cd /root/wishful/final_showcase/network_virtual_radio
   
3. Execute the script to start the 3 GNURadio WiSHFUL agents + virtual radio controller:

        ./start_virtual_radio_network.sh start

4. Make sure the AD controller is running. If it is not running, the previous command will not print any message on screen.

5. Send a "START_LTE" or "START_NBIOT" command from the AD controller to the Virtual Radio Network controller.
     
6. Check if everything is OK. Output should contain a line as:
     ```
     ... TX is OK
     ... LTE RX is OK
     ... NB-IoT RX is OK
     ```
