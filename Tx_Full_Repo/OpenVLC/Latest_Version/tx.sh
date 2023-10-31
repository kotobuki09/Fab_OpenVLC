#!/bin/bash 
cd Driver/
sudo ./load_test.sh #Load OpenVLC driver 
cd .. 
cd PRU/TX 
sudo ./deploy.sh #Load OpenVLC firmware 
cd .. 
cd .. 
echo "1" | sudo tee /proc/sys/net/ipv4/ip_forward #Enable forwarding 
#sudo route add -net 192.168.1.0/24 gw 192.168.0.2 #Add  
#sudo ip route change default via 192.168.0.2 dev vlc0
#sudo route add -net 192.168.3.0/24 gw 192.168.0.2
#sudo route add -net 192.168.2.0/24 gw 192.168.0.2


sudo sysctl -w net.ipv4.conf.all.rp_filter=0 
echo "TX config" 
#sudo iperf -c 192.168.0.2 -u -b 400k -l 800 -p 10001 -t 100
