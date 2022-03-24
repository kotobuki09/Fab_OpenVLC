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
    
    