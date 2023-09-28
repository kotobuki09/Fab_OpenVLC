import json
import zmq
import threading
from lib.kvsimple import KVMsg

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2017, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz@tkn.tu-berlin.de"


class GlobalSolutionControllerProxy(object):
    """docstring for GlobalSolutionControllerProxy"""

    def __init__(self, ip_address="127.0.0.1", requestPort=7001, subPort=7000):
        super(GlobalSolutionControllerProxy, self).__init__()

        self.controllerName = None
        self.networkName = None
        self.networkType = None
        self.solutionName = []
        self.commandList = []
        self.eventList = []
        self.commands = {}
        self.monitorList = {}

        self.ctx = zmq.Context()
        # Prepare our REQ/REP socket
        self.requestSocket = self.ctx.socket(zmq.DEALER)
        self.requestSocket.linger = 0
        url = "tcp://" + ip_address + ":" + str(requestPort)
        self.requestSocket.connect(url)
        # Prepare our SUBSCRIVER socket
        self.subSocket = self.ctx.socket(zmq.SUB)
        self.subSocket.linger = 0
        self.subSocket.setsockopt(zmq.SUBSCRIBE, b'')
        url = "tcp://" + ip_address + ":" + str(subPort)
        self.subSocket.connect(url)
        self.cmdRxThread = None

    def set_solution_attributes(self, controllerName, networkType, solutionName, commands, monitorList):
        """
        Set attribute of the solution
        """
        # Activation    Event
        # De - activation
        # Event     List    of  monitoring  parameters
        # List  of  control knobs / parameters
        self.controllerName = controllerName
        self.networkType = networkType
        self.solutionName = solutionName
        self.commands = commands
        self.commandList = sorted(list(commands.keys()))
        self.monitorList = monitorList

    def register_solution(self):
        """
        Register solution to solution global controller
        """
        # Activation    Event
        # De - activation
        # Event     List    of  monitoring  parameters
        # List  of  control knobs / parameters

        # create the json format message
        # old json format
        # msg = {"type": "registerRequest",
        #        "solution": self.solutionName,
        #        "commandList": self.commandList,
        #        "eventList": self.eventList,
        #        "monitorList": self.monitorList}
        # new json format
        msg = {"type": "registerRequest",
               "networkController": self.controllerName,
               "networkType": self.networkType,
               "solution": self.solutionName,
               "commandList": self.commandList,
               "monitorList": self.monitorList}

        sequence = 1
        kvmsg = KVMsg(sequence)
        kvmsg.key = b"generic"
        kvmsg.body = json.dumps(msg).encode('utf-8')
        # send the message
        kvmsg.send(self.requestSocket)

        # process the registerRespons
        try:
            kvmsg_reply = KVMsg.recv(self.requestSocket)
        except Exception:
            return False

        body = kvmsg_reply.body
        parsed_json = json.loads(body.decode("utf-8"))
        if "type" in parsed_json:
            mtype = parsed_json["type"]
            if mtype == "registerResponse":
                print("Received registration registerResponse")
                return True
        return False

    def command_subscriber(self):
        while True:
            try:
                #print("Wait for command")
                kvmsg = KVMsg.recv(self.subSocket)
                # update message {'involvedSolutions': 'WIFI', 'type': 'publisherUpdate', 'commandList': 'START_WIFI'}
                # {'involvedController': ['WIFI'], 'commandList': {'WIFI_CT': {'START_WIFI': {'2437': True}}}, 'type': 'publisherUpdate'}
                mdict = kvmsg.body.decode('utf-8')
                mdict = json.loads(mdict)
                #print("received command : " + str(mdict))
                # {'type': 'publisherUpdate', 'commandList': {'WIFI_CT': {'START_WIFI': {'2437': True}}}, 'involvedController': ['WIFI']}
                involvedController = mdict.get("involvedController", [])
                if self.controllerName in involvedController:
                    commandListSolutions = mdict.get("commandList", {})
                    # print(commandListSolutions) # 'WIFI_CT': {'START_WIFI': {'2437': True}} # {'LTE_CT': {'ENABLE_LTE_2_SUBFRAME': {}}}

                    # print(self.solutionName[0])
                    commandList = commandListSolutions.get(self.solutionName[0], None)
                    print("commandList", commandList)
                    if bool(commandList):
                        commandList = commandListSolutions.get(self.solutionName[0], {})
                        print(commandList)
                        for command_name, command_parameter in commandList.items():
                            print("Execute command {} with parameters {}".format(command_name, command_parameter))
                            function = self.commands[command_name]

                            executed = False
                            try:
                                function(command_parameter)
                                executed = True
                            except Exception as ex:
                                print(ex)
                                pass

                            if not executed:
                                function()

            except KeyboardInterrupt:
                return
            except Exception as ex:
                print("Exception on command_subscriber loop: {}".format(ex))
                break  # Interrupted

    def start_command_listener(self):
        """
        Start service for COMMAND/UPDATE from global solution controller
        """
        self.cmdRxThread = threading.Thread(target=self.command_subscriber)
        self.cmdRxThread.daemon = True
        self.cmdRxThread.start()

    def send_monitor_report(self, mon_type, net_type, value):
        """
        Send monitor information to the solution global controller
        """
        msg = {
            'type': 'monitorReport',
            'networkController': self.controllerName,
            'monitorType': mon_type,
            'networkType': net_type,
            'monitorValue': value
        }
        sequence = 0
        kvmsg = KVMsg(sequence)
        kvmsg.key = b"generic"
        kvmsg.body = json.dumps(msg).encode('utf-8')
        kvmsg.send(self.requestSocket)


    def send_monitor_report_generic(self, network_name, mon_type, net_type, value):
        """
        Send monitor information to the solution global controller
        """
        msg = {
            'type': 'monitorReport',
            'networkController': network_name,
            'monitorType': mon_type,
            'networkType': net_type,
            'monitorValue': value
        }
        sequence = 0
        kvmsg = KVMsg(sequence)
        kvmsg.key = b"generic"
        kvmsg.body = json.dumps(msg).encode('utf-8')
        kvmsg.send(self.requestSocket)


    def send_event(self, eventType):
        """
        Send monitor event detected to the solution global controller
        """
        msg = {'type': 'eventReport',
               'solution': self.solutionName,
               'eventType': eventType,
               }
        sequence = 0
        kvmsg = KVMsg(sequence)
        kvmsg.key = b"generic"
        kvmsg.body = json.dumps(msg).encode('utf-8')
        kvmsg.send(self.requestSocket)
