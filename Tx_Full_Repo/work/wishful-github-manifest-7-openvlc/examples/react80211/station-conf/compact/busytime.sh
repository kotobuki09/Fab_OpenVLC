echo "BusyTime Tool is runnin..."
echo "press CTRL+C to close"
sleep_val=1;

busytime_prec=$(iw dev wlan0 survey dump | grep "busy time" | awk '{ print $4 }');
txtime_prec=$(iw dev wlan0 survey dump | grep "transmit time" | awk '{ print $4 }');
sleep $sleep_val
busytime=$(iw dev wlan0 survey dump | grep "busy time" | awk '{ print $4 }');
txtime=$(iw dev wlan0 survey dump | grep "transmit time" | awk '{ print $4 }');

while [ 1 ]; do
	array=(${busytime//:/ })
	array_prec=(${busytime_prec//:/ })
	array_tx=(${txtime//:/ })
	array_tx_prec=(${txtime_prec//:/ })
  	i=1
       #for i in "${!array[@]}"
       #do
	busy_diff=$(( ${array[i]}-${array_prec[i]} ));
	tx_diff=$(( ${array_tx[i]}-${array_tx_prec[i]} ));
	busy=$(( ${busy_diff} - ${tx_diff} ));
	echo "tx_diff=${tx_diff}"
	echo "busy_diff=${busy_diff}"
	echo "busy=${busy}"

	#echo "$i=>$(( (${array[i]}-${array_prec[i]} ) * 100 / 1000 ))"
	#echo "$i=>$(( (${busy} )* 100 / 1000 ))"

       #done
	i=1
	busytime_prec=$busytime;
       busytime=$(iw dev wlan0 survey dump | grep "busy time" | awk '{ print $4 }');
	txtime_prec=$txtime;
	txtime=$(iw dev wlan0 survey dump | grep "transmit time" | awk '{ print $4 }');

	sleep $sleep_val
done
