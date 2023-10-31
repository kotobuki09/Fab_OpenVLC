# Fab OpenVLC
## Intelligent Management System for OpenVLC
 
 ![Fab_032022](https://user-images.githubusercontent.com/34347264/157910137-6f7f791e-4902-4057-868a-5b31315243ff.png)

![MobaXterm_r3aSd3Miqa](https://user-images.githubusercontent.com/34347264/157898274-9802bb1f-b001-4f71-b3f0-d30647b6240f.png)

https://glowing-hardcover-41b.notion.site/OpenVLC-PRU-f7f70c9ccc974c2abeacf5913e39f0b8

First we create this demo based on OpenVLC and using normal USB WiFi doungle for create WiFi network. 

You can follow this instruction to get familiar with how to creat openVLC connection.
Regard to WiFi dougle, there might need to be install different module based on your WiFi chipset. In our case, we use TP-Link USB dougle with Intel Chipset. If that is your case, you can use this driver to update in your system to make the dougle working in your system.
There are different driver that we can suggestion based on your USB chipset below:
    
1

2

3

Before start the demo, you need to 


We creating the Intelligent System based on Fabric framework that be able to gathering information from both network and act as brain to make different decison to make the hybrid system workin seemlessly and robustly as possible.

After completed all the setup related WiFi. you need to put different file into BBB Tx and BBB Rx to make the IMS work in both network.
.... ()

Now can activate for the whole system from center controller 

Go to IMS Center Controller Unit folder, and open the terminal in this folder 

And now you can create WiFi network:

#Intruction:

Go to the controller directory:
This command will be at controller terminal

Create WiFi network

BB1

    fab vlc1 setup_wifi_ap
BB2

	fab vlc2 setup_wifi_sta
BB1

    fab vlc1 setup_vlc_tx
BB2

    fab vlc2 setup_vlc_rx

These command will be create virtual interface in BBB so that we can modify routing and traffic easier and can act as independance devices connect to network.

Fab somehow doensn't work when related to changing interface: You need to create virtual interface by ssh directly to BBB
#BBB1-virtual interface 10:0 (Tx)

    sudo ip link add eth10 type dummy

    sudo ifconfig eth10 hw ether 00:22:22:ff:ff:ff

    sudo ip addr add 192.168.10.1/24 brd + dev eth10 label eth10:0

#BBB2-virtual interface 10:0 (Rx)

    sudo ip link add eth10 type dummy

    sudo ifconfig eth10 hw ether 00:22:22:ff:ff:f0

    sudo ip addr add 192.168.10.2/24 brd + dev eth10 label eth10:0

And now you can create iperf traffic that can be use to test the with all kind of experiment that you gonna get

#Start Iperf (wifi, vlc, virtual link)

Tx

    iperf -c 192.168.10.2 -u -b 1000M -l 800 -p 10001 -t 100000
Rx

    iperf -u -l 800 -s -i3 -B 192.168.10.2 -p 10001

These commend can use as force handover from controller to different link VLC or WiFi channel:

#Activate wifi link
    
    fab vlc1 wifi_link

#Activate vlc link
    
    fab vlc1 vlc_link

Now you can active the automous sensing and controller IHC with 

#Enable the demo2

    fab vlc1 schedule_controller


#For getting RSSI value
    
	sudo ./prubgb > 2048sample. raw # Get the sample out

then used the python script to draw the output


![Test2](https://github.com/kotobuki09/Fab_OpenVLC/blob/main/IDLE%20vs%20IPERF%20RSSI%20TEST2.png)


![New](https://github.com/kotobuki09/Fab_OpenVLC/blob/main/IDLE%20vs%20IPERF%20RSSI%203103.png)
	
1) Current network: 

    
	WiFIi or VLC available (interface vlc0 - up or wlan0- up) (default vlc0)
    
	network = vlc0
    
	if (ifconfig vlc1 = False & ifconfig wlan0 =True)
    
	then network = wlan0	

3)  

	
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

Clean all log file after 2 days in BBB:

	find /var/log -mindepth 1 -mtime +2 -delete
	
