import subprocess
import time
import sys


def findLine(str, search_str):
    return [x for x in str.splitlines() if search_str in x]

def check_stream():

   proc = subprocess.Popen(
      ["sudo", "timeout", "1", "tcpdump", "-i", "eth0", "dst port 1234"],
      stderr=subprocess.PIPE,
      stdout=subprocess.DEVNULL,
   )
   output = proc.stderr.read().decode("ASCII")
   num_rx_packets = findLine(output,"filter")[0].split(" ")[0]
   return num_rx_packets

print(check_stream())
