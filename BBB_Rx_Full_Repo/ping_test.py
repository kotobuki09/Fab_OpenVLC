import subprocess
import time
import sys


def findLine(str, search_str):
    return [x for x in str.splitlines() if search_str in x]

def check_stream():

   ipaddress = '10.0.0.1'  # guess who
   proc = subprocess.Popen(
      #['ping', '-c', '3', ipaddress],
      ["timeout", "1", "ping", ipaddress],
      stderr=subprocess.DEVNULL,
      stdout=subprocess.PIPE,
   )
      #["sudo", "timeout", "1", "tcpdump", "-i", "eno1", "dst port 1234"])
   output = proc.stdout.read().decode("ASCII")
   

   for line in output.splitlines():
     line_array = line.split(" ")
     for value in line_array:
       print(value)
       if "time=" in value:
          print("found")
          print(value)
#     print(line_array)
   #num_rx_packets = findLine(output,"filter")[0].split(" ")[0]
   #return num_rx_packets

check_stream()
