#!/bin/bash          

#This is only client. You have to start two servers manually on second machine
#For TCP
# iperf -s -p 5001
# iperf -s -p 5002
#For UDP
# iperf -s -p 5001 -u
# iperf -s -p 5002 -u
#
# You can watch iptables and tc queues
# watch iptables -t mangle -vL
# watch -n 1 tc -s -d -r qdisc show dev wlan0


runTest=true
cleanQueue=true
useUdp=true

setIpTos=false

PfifoQueue=false
PrioQueueTwoBands=false

if $cleanQueue ; then
	#add and remove queue
	tc qdisc add dev wlan0 root handle 1: pfifo limit 1000
	tc qdisc del dev wlan0 root handle 1: pfifo limit 1000
fi

if $setIpTos ; then
	# for TCP: VO for 5001 and BE for 5002
	iptables -t mangle -A OUTPUT -p tcp --dport 5001 -j TOS --set-tos 225
	iptables -t mangle -A OUTPUT -p tcp --dport 5002 -j TOS --set-tos 65
	# for UDP: VO for 5001 and BE for 5002
	iptables -t mangle -A OUTPUT -p udp --dport 5001 -j TOS --set-tos 225
	iptables -t mangle -A OUTPUT -p udp --dport 5002 -j TOS --set-tos 65
fi


if $PfifoQueue ; then
	tc qdisc add dev wlan0 root handle 1: pfifo limit 1000
fi


if $PrioQueueTwoBands ; then
	#we have to create prio queue with at least3 bands
	tc qdisc add dev wlan0 root handle 1: prio bands 3
	tc qdisc add dev wlan0 parent 1:1 handle 10: pfifo limit 1000
	tc qdisc add dev wlan0 parent 1:2 handle 20: pfifo limit 1000
	tc qdisc add dev wlan0 parent 1:3 handle 30: pfifo limit 1000
	tc filter add dev wlan0 parent 1:0 protocol ip prio 10 u32 match ip tos 0xe1 0xff flowid 1:1
	tc filter add dev wlan0 parent 1:0 protocol ip prio 20 u32 match ip tos 0x21 0xff flowid 1:2
	tc filter add dev wlan0 parent 1:0 protocol ip prio 30 u32 match ip tos 0x41 0xff flowid 1:3
fi

if $runTest ; then
	if $useUdp ; then
		iperf -c 192.168.1.178 -p 5001 -t 30 -u -b 250M &
		iperf -c 192.168.1.178 -p 5002 -t 30 -u -b 250M
	else
		iperf -c 192.168.1.178 -p 5001 -t 30 &
		iperf -c 192.168.1.178 -p 5002 -t 30
	fi
fi


if $setIpTos ; then
	# for TCP: VO for 5001 and BE for 5002
	iptables -t mangle -D OUTPUT -p tcp --dport 5001 -j TOS --set-tos 225
	iptables -t mangle -D OUTPUT -p tcp --dport 5002 -j TOS --set-tos 65
	# for UDP: VO for 5001 and BE for 5002
	iptables -t mangle -D OUTPUT -p udp --dport 5001 -j TOS --set-tos 225
	iptables -t mangle -D OUTPUT -p udp --dport 5002 -j TOS --set-tos 65
fi


if $PfifoQueue ; then
	tc qdisc del dev wlan0 root handle 1: pfifo limit 1000
fi


if $PrioQueueTwoBands ; then
	tc qdisc del dev wlan0 root handle 1: prio bands 3
fi