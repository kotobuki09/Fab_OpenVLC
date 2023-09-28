#
# Test client for passing schedules to the userland C++ mac processor
#
import zmq

#  Prepare our context and sockets
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
#socket.connect("ipc:///tmp/testtt")

mac_slotting_conf_str = '1,98:fc:11:dd:95:a9,0#2,98:fc:11:dd:95:a9,0#3,98:fc:11:dd:95:a9,0#4,98:fc:11:dd:95:a9,0'
#socket.send(b"Hello")
socket.send(mac_slotting_conf_str)
message = socket.recv()
print("Received reply from HMAC: %s" % message)
