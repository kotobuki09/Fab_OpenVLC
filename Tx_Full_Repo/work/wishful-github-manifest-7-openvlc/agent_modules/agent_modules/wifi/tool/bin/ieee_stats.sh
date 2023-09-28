#! /bin/bash 
#phy_iface="phy0" 

phy_iface="$1"

labels=$(ls /sys/kernel/debug/ieee80211/${phy_iface}/statistics/) 
arr_label=($labels)

#busy=$(iw dev wlan0 survey dump | grep busy | awk '{print $4}' )
#arr_busy=($busy)
stats=$(cat /sys/kernel/debug/ieee80211/${phy_iface}/statistics/*)
arr_stats_start=($stats)


printf "{"
#printf "\"busy_time\" : %s, " "${arr_busy[1]}"
 for ((i=0;i<${#arr_label[@]} ;i++)) { 
  #diff=$(( ${arr_stats_stop[$i]} - ${arr_stats_start[$i]} ));
  diff=${arr_stats_start[$i]} 
  if [ $i -eq $(( ${#arr_label[@]} - 1 )) ]; then
	printf "\"%s\" : %s " "${arr_label[$i]}"  "$diff"
  else 
	printf "\"%s\" : %s, " "${arr_label[$i]}" "$diff"
  fi
}
printf "}" 

#ack_fail=$(( ${arr_stats_stop[0]} - ${arr_stats_start[0]} ))
#tx_completed=$(( ${arr_stats_stop[12]} - ${arr_stats_start[12]} ))
#rts_failed=$(( ${arr_stats_stop[2]} - ${arr_stats_start[2]} ))
#rts_success=$(( ${arr_stats_stop[3]} - ${arr_stats_start[3]} ))