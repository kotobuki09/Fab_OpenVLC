#!/bin/bash
#wifi=$(route -n | grep -e '192.168.12.1')
#if [ -z "route -n | grep -e '192.168.12.1'" ]; then
#	echo "no files found"
#	route del -net 192.168.10.0 gw 192.168.0.1 netmask 255.255.255.0 dev vlc0
#	route add -net 192.168.10.0 gw 192.168.12.1 netmask 255.255.255.0 dev ap0
#fi

if [ -z "$(route -n | grep -e '192.168.12.1'| head -c1 | wc -c) -ne 0)" ]; then
  echo "Switching into WiFi connection"
  route del -net 192.168.10.0 gw 192.168.0.1 netmask 255.255.255.0 dev vlc0
  route add -net 192.168.10.0 gw 192.168.12.1 netmask 255.255.255.0 dev ap0
else
  echo "The WiFi connection is available"
fi

