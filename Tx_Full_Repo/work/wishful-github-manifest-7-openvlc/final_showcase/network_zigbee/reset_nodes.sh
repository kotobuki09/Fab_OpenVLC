sudo killall python3 python
for node in `ls /dev/ttyUSB*`
do
	echo "$node"
	/groups/portable-ilabt-imec-be/wish/imec/wishful/agent_modules/contiki/communication_wrappers/bin/cc2538-bsl.py -p $node -a 0x00202000

done
