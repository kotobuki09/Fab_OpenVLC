import logging
import time
import sys
import zmq.green as zmq
from gevent.lock import Semaphore
import wishful_framework as msgs
import dill #for pickling what standard pickle can’t cope with
try:
   import cPickle as pickle
except:
   import pickle

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class TransportChannel(object):
    def __init__(self, uplink=None, downlink=None):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))
        
        self.downlink = downlink
        self.uplink = uplink
        self.recv_callback = None

        self.context = zmq.Context()
        self.poller = zmq.Poller()

        self.ul_socket = self.context.socket(zmq.SUB) # one SUB socket for uplink communication over topics
        if sys.version_info.major >= 3:
            self.ul_socket.setsockopt_string(zmq.SUBSCRIBE,  "NEW_NODE")
            self.ul_socket.setsockopt_string(zmq.SUBSCRIBE,  "NODE_EXIT")
        else:
            self.ul_socket.setsockopt(zmq.SUBSCRIBE,  "NEW_NODE")
            self.ul_socket.setsockopt(zmq.SUBSCRIBE,  "NODE_EXIT")

        self.downlinkSocketLock = Semaphore(value=1)
        self.dl_socket = self.context.socket(zmq.PUB) # one PUB socket for downlink communication over topics

        #register UL socket in poller
        self.poller.register(self.ul_socket, zmq.POLLIN)


    def set_downlink(self, downlink):
        self.log.debug("Set Downlink: {}".format(downlink))
        self.downlink = downlink


    def set_uplink(self, uplink):
        self.log.debug("Set Uplink: {}".format(uplink))
        self.uplink = uplink


    def subscribe_to(self, topic):
        self.log.debug("Controller subscribes to topic: {}".format(topic))
        if sys.version_info.major >= 3:
            self.ul_socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        else:
            self.ul_socket.setsockopt(zmq.SUBSCRIBE, topic)
 

    def set_recv_callback(self, callback):
        self.recv_callback = callback


    def send_downlink_msg(self, msgContainer):
        msgContainer[0] = msgContainer[0].encode('utf-8')
        cmdDesc = msgContainer[1]
        msg = msgContainer[2]

        if cmdDesc.serialization_type == msgs.CmdDesc.PICKLE:
            try:
                msg = pickle.dumps(msg)
            except:
                msg = dill.dumps(msg)
        elif cmdDesc.serialization_type == msgs.CmdDesc.PROTOBUF:
            msg = msg.SerializeToString()

        msgContainer[1] = cmdDesc.SerializeToString()
        msgContainer[2] = msg

        self.downlinkSocketLock.acquire()
        try:
            self.dl_socket.send_multipart(msgContainer)
        finally:
            self.downlinkSocketLock.release()


    def start_receiving(self):
        socks = dict(self.poller.poll())
        if self.ul_socket in socks and socks[self.ul_socket] == zmq.POLLIN:
            try:
                msgContainer = self.ul_socket.recv_multipart(zmq.NOBLOCK)
            except zmq.ZMQError:
                raise zmq.ZMQError

            assert len(msgContainer) == 3, msgContainer

            dest = msgContainer[0]
            cmdDesc = msgs.CmdDesc()
            cmdDesc.ParseFromString(msgContainer[1])
            msg = msgContainer[2]
            if cmdDesc.serialization_type == msgs.CmdDesc.PICKLE:
                try:
                    msg = pickle.loads(msg)
                except:
                    msg = dill.loads(msg)

            msgContainer[0] = dest.decode('utf-8')
            msgContainer[1] = cmdDesc
            msgContainer[2] = msg
            self.recv_callback(msgContainer)


    def start(self):
        self.log.debug("Controller on DL-{}, UP-{}".format(self.downlink, self.uplink))
        self.dl_socket.bind(self.downlink)
        self.ul_socket.bind(self.uplink)


    def stop(self):
        self.ul_socket.setsockopt(zmq.LINGER, 0)
        self.dl_socket.setsockopt(zmq.LINGER, 0)
        self.ul_socket.close()
        self.dl_socket.close()
        self.context.term() 
