import subprocess
import time
import sys


def findLine(str, search_str):
    return [x for x in str.splitlines() if search_str in x]

def check_stream():

   ipaddress = '10.0.0.1'  # guess who
   proc = subprocess.Popen(
      #['ping', '-c', '3', ipaddress],
      ["sudo", "timeout", "1", "ping", ipaddress],
      stderr=subprocess.DEVNULL,
      stdout=subprocess.PIPE,
   )
      #["sudo", "timeout", "1", "tcpdump", "-i", "eno1", "dst port 1234"])
   output = proc.stderr.read().decode("ASCII")
   for line in output:
     print("qui...")
     line_array = line.split(" ")
     print(line_array)
   #num_rx_packets = findLine(output,"filter")[0].split(" ")[0]
   #return num_rx_packets

check_stream()
