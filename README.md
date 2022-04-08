# Fab_OpenVLC
 Simple Control Unit for OpenVLC
 
 ![Fab_032022](https://user-images.githubusercontent.com/34347264/157910137-6f7f791e-4902-4057-868a-5b31315243ff.png)

![MobaXterm_r3aSd3Miqa](https://user-images.githubusercontent.com/34347264/157898274-9802bb1f-b001-4f71-b3f0-d30647b6240f.png)

https://glowing-hardcover-41b.notion.site/OpenVLC-PRU-f7f70c9ccc974c2abeacf5913e39f0b8

#Intruction:

Go to the controller directory:
    
    fab vlc1 setup_wifi_ap

    fab vlc2 setup_wifi_sta

    fab vlc1 setup_vlc_tx

    fab vlc2 setup_vlc_rx

Fab somehow doensn't work when related to changing interface: You need to create virtual interface by ssh directly to BBB
#BBB1-virtual interface 10:0 (Tx)

    sudo ip link add eth10 type dummy

    sudo ifconfig eth10 hw ether 00:22:22:ff:ff:ff

    sudo ip addr add 192.168.10.1/24 brd + dev eth10 label eth10:0

#BBB2-virtual interface 10:0 (Rx)

    sudo ip link add eth10 type dummy

    sudo ifconfig eth10 hw ether 00:22:22:ff:ff:f0

    sudo ip addr add 192.168.10.2/24 brd + dev eth10 label eth10:0


#Start Iperf (wifi, vlc, vitual link)

    fab vlc1 start_iperf_client:wifi
    fab vlc2 start_iperf_server:wifi

    fab vlc1 start_iperf_client:vlc
    fab vlc2 start_iperf_server:vlc

    fab vlc1 start_iperf_client
    fab vlc2 start_iperf_server

#Activate wifi link
    
    fab vlc1 wifi_link

#Activate vlc link
    
    fab vlc1 vlc_link

#Enable the schedule_controller

    fab vlc1 schedule_controller


#For getting RSSI value
    
	sudo ./prubgb > 2048sample. raw # Get the sample out

then used the python script to draw the output

 ![Noncom](https://raw.githubusercontent.com/kotobuki09/Fab_OpenVLC/main/openVLC_RSSI_analyzer/IDLE%20vs%20IPERF%20RSSI%20TEST1.png?token=GHSAT0AAAAAABOOP7LNHBDZQ5F4M2HITHMQYSFRGFA)
 
  ![400Kcom](https://raw.githubusercontent.com/kotobuki09/Fab_OpenVLC/main/openVLC_RSSI_analyzer/IDLE%20vs%20IPERF%20RSSI%20TEST2.png?token=GHSAT0AAAAAABOOP7LN4FKIBREWLLTMTUYOYSFRK3A)
  
    		
	
1) Current network: wifi or VLC available (interface vlc0 - up or wlan0- up) (default vlc0)

	network = vlc0
	
	if (ifconfig vlc1 = False & ifconfig wlan0 =True)
	
		then network = wlan0
	

2)  

If network = vlc0:

	how to read RSSI value from the prubgb
	
	if (RSSI max_value >= 1061 & min_value <= 989)
	
		then (switch to wifi)
		
	else
	
		remain
else()

	if (wlan0 down ) #bitrate < 100 Kb/s 
	
		then (switch to VLC)
		
	else
	
		remain
				
Read the value from node+fabric

Read channel info wifi channel:

	fab vlc2 wchannel
	
Read info from iperf application

Start iperf server:

	iperf -u -s -B 10.0.0.16 -p 10002
	
then

	fab vlc1 iwifi


	
