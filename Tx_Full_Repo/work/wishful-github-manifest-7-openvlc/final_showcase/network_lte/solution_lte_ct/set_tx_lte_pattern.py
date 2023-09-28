#!/usr/bin/python
import socket
import random
import json
import sys, getopt

def printHelp():
   print('set_lte_tx_pattern.py -w <tx_pattern>')
   print("<tx_pattern> must have the following structure xxxxxxxxxx (x is 0 or 1)")
   print("<tx_pattern> e.g. 1010101010")


def main(argv):
   tx_pattern= "1,1,1,1,1,1,1,1,1,1"
   eternal_option = False

   try:
      opts, args = getopt.getopt(argv,"hiw:",["tx_pattern="])
   except getopt.GetoptError:
      printHelp()
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         printHelp()
         sys.exit()
      elif opt in ("-w", "--tx_pattern"):
         option_pattern = arg
         if len(option_pattern)==10:
            if option_pattern[0] == '1' or option_pattern[0] == '0':
               tx_pattern = option_pattern[0]
            else:
               print("option must have the following structure xxxxxxxxxx (x is 0 or 1)")
               print("-------------------------------------------------------------------")
               printHelp()
               sys.exit()

            for ii in range(1,10):
               if option_pattern[ii] == '1' or option_pattern[ii]== '0':
                  tx_pattern = tx_pattern + ',' + option_pattern[ii]
               else:
                  print("option must have the following structure xxxxxxxxxx (x is 0 or 1)")
                  print("-------------------------------------------------------------------")
                  printHelp()
                  sys.exit()
         else:
            print("option must been 10 length characters")
            print("-------------------------------------------------------------------")
            printHelp()
            sys.exit()

      else:
         print("option is required")
         print("-------------------------------------------------------------------")
         printHelp()
         sys.exit()

   # UDP_IP = "127.0.0.1"
   # UDP_PORT = 8888
   # ue_id = '1'
   # snr=random.randint(-100,0)
   # bler=random.randint(0,100)
   # mjson={'ue_id':ue_id,'snr':snr,'bler':bler}

   UDP_IP = "172.16.16.11"
   #UDP_IP = "10.8.9.13"
   UDP_PORT = 8888

   MESSAGE = tx_pattern
   print("tx_pattern: ", MESSAGE)
   print("UDP target IP: ", UDP_IP)
   print("UDP target port: ", UDP_PORT)

   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
   sock.close()

   print("LTE pattern succesful configured")


if __name__ == "__main__":
   main(sys.argv[1:])
