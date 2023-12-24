   # Simple UDP client to push some nonsense data

from socket import *
import time

# put the IP address to UDP to here: safer not to use DNS
HOST = '192.168.0.2'

# put a valid port number here - 7 is echo server, usually disabled these days
# but we won't be expecting an answer anyway
PORT = 7

# put something to send here
DATA = "Hi"

# put time to delay here - is in seconds, so 5 * 60 = once per 5 minutes
# the expression will have Python calc the seconds for us
SLEEP_TIME = 5

while 1:
# we recreate, close and free up socket every time
# this is more robust if the time delay is large
udpSock = socket(AF_INET, SOCK_DGRAM)
print "Sending data <%s>" % DATA
udpSock.sendto(DATA,(HOST,PORT))
udpSock.close()

time.sleep(SLEEP_TIME)

 
 

