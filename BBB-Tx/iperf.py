import os
import time

#os.system('nohup iperf -c 192.168.10.2 -u -b 1000M -l 800 -p 10003 -t 100000 --daemon')
start_time = time.time()
os.system('nohup iperf -c 192.168.10.2 -u -b 1000M -l 800 -p 10003 -t 100000 --daemon')
stop_time = time.time() - start_time
print(stop_time)

