#!/bin/bash
#wifi=$(route -n | grep -e '192.168.12.1')
#if [ -z "route -n | grep -e '192.168.12.1'" ]; then
#	echo "no files found"
#	route del -net 192.168.10.0 gw 192.168.0.1 netmask 255.255.255.0 dev vlc0
#	route add -net 192.168.10.0 gw 192.168.12.1 netmask 255.255.255.0 dev ap0
#fi

if [ -n "$(route -n | grep -e '192.168.12.1'| head -c1 | wc -c) -ne 0)" ]; then
  echo "Switching into VLC link"
  route del -net 192.168.10.0 gw 192.168.12.1 netmask 255.255.255.0 dev ap0
  route add -net 192.168.10.0 gw 192.168.0.1 netmask 255.255.255.0 dev vlc0
else
  echo "The vlc connection is available"
fi

