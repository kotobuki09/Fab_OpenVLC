# run os.system and caputre standard output to a string
import subprocess
#import numpy as np

proc = subprocess.Popen(["./prudebug-bbb/prudbgb"], stdout=subprocess.PIPE, shell=True)
(out, err) = proc.communicate()

#print(type(out))
#print(out)

rssi_list = str(out).split(",")
del rssi_list[0]
del rssi_list[-1]

rssi_list = [int(r) for r in rssi_list]
print(rssi_list)

#rssi_list.remove("\n")
import statistics as st
#print ("program output={}".format(rssi_list))
print(max(rssi_list))
print(min(rssi_list))
print(st.variance(rssi_list))
print(st.stdev(rssi_list))
# convert string into an array
#rssi_array = np.fromstring(s[1:-1], dtype=np.int, sep=', ')
