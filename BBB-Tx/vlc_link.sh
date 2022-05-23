#! /bin/bash
#route del -net 192.168.10.0 gw 192.168.12.1 netmask 255.255.255.0 dev ap0
#route add -net 192.168.10.0 gw 192.168.0.1 netmask 255.255.255.0 dev vlc0

start_time=$(date +%s%N)
# perform a task
if [ -n "$(route -n | grep -e '10.0.0.1')" ]; then
  #echo "Switching into VLC connection"
  route del -net 192.168.10.0 gw 10.0.0.1 netmask 255.255.255.0 dev wlan0
  route add -net 192.168.10.0 gw 192.168.0.1 netmask 255.255.255.0 dev vlc0
  end_time=$(date +%s%N)

  #elapsed time with second resolution
  elapsed=$(( (end_time - start_time )/1000000 ))

  #echo $start_time
  #echo $end_time
  echo $elapsed
else
  echo "The vlc connection is available"
fi
  #echo $elapsed
