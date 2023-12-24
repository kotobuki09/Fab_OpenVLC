import os
import subprocess

#bandwidth="iperf -c 10.0.0.16 -u -p 10002 -t 1 -r -y C|cut -d',' -f9"
jitter="iperf -c 10.0.0.16 -u -p 10002 -t 2 -r -y C|cut -d',' -f9,10,13"
#dlost="iperf -c 10.0.0.16 -u -p 10002 -t 1 -r -y C|cut -d',' -f12"
#cmd=["iperf -c 10.0.0.16 -u -p 10002 -t 1"]


#proc = subprocess.Popen(cmd, encoding = 'utf-8', stdout=subprocess.PIPE, shell=True)
#o = proc.communicate()
#print(proc)

jitter=os.popen(jitter)
output=jitter.readlines()
#del output[0]
output=[x.replace('\n', '').strip() for x in output]
iwifi=output[2]
iwifi=iwifi.replace(',',' ')
#iwifi=wifi.split(" ")

#output=[int(i) for i in output[2]]
print(iwifi)
#print(iwifi[2])
#print('Bandwidth, Jitter, Percent_lost = %s'%output[2])
#print(type(iwifi))
#print("Max jitter = "+ str(jitter))
