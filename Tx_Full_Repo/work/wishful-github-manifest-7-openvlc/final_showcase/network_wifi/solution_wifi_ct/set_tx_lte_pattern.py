#!/usr/bin/python
import socket
import random
import json
import sys, getopt

def main(argv):
   tx_pattern= "1,1,1,1,1,1,1,1,1,1"
   try:
      opts, args = getopt.getopt(argv,"hiw:",["tx_pattern="])
   except getopt.GetoptError:
      print('set_lte_tx_pattern.py -w <tx_pattern>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('set_lte_tx_pattern.py -w <tx_pattern>')
         sys.exit()
      elif opt in ("-w", "--tx_pattern"):
         tx_pattern = arg
   UDP_IP = "127.0.0.1"
   UDP_PORT = 8888
   ue_id='1'

   print("UDP target IP:", UDP_IP)
   print("UDP target port:", UDP_PORT)

   snr=random.randint(-100,0)
   bler=random.randint(0,100)
   mjson={'ue_id':ue_id,'snr':snr,'bler':bler}
   MESSAGE = tx_pattern
   print(MESSAGE)

   sock = socket.socket(socket.AF_INET, # Internet
		     socket.SOCK_DGRAM) # UDP
   sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
   sock.close()

if __name__ == "__main__":
   main(sys.argv[1:])
