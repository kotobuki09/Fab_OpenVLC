import time
import json
import struct

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class WiFiNetwork(object):
    """docstring for WiFiNetwork"""
    def __init__(self, netId, ctrName, netType, solutionList,
                 cmdList, monList):
        super(WiFiNetwork, self).__init__()
        self.netId = netId
        self.ctrName = ctrName
        self.netType = netType
        self.solutionList = solutionList
        self.cmdList = cmdList
        self.monList = monList

        self.activated = False

        self.channel = None
        self.frequency = None
        self.bandwidth = None
        self.lastChanSwitchTime = time.time()

        self.requestedTraffic = 0.0
        self.currentTraffic = 0.0
        self.performance = 0
        self.satisfied = True
        # throughput on each channel
        self.throughputCache = {}
        self.cacheSize = 5

        self.lastOptimizationTime = None
        self.measurementsRunning = False

    def reset_stats(self):
        self.lastOptimizationTime = None
        self.measurementsRunning = False
        self.satisfied = True
        # throughput on each channel
        self.throughputCache = {}
        self.cacheSize = 5

    def check_cache(self, channels):
        full = True
        for ch in channels:
            chanStats = self.throughputCache.get(ch, {})
            samples = chanStats.get("thrSamples", [])
            print(ch, samples, len(samples), self.cacheSize)
            if len(samples) < self.cacheSize:
                full = False

        return full

    def clean_thr_cache(self):
        self.throughputCache = {}

    def send_switch_channel_cmd(self, socket, newChannel):
        msg = {'type': 'publisherUpdate',
               'involvedController': [self.ctrName],
               'commandList': {'WiFi_Channel_Switching': {'SWITCH_CHANNEL': {"channel": newChannel}}
                               }
               }

        print("SENT Switch command: ", msg)
        key = b"generic"
        seq_s = struct.pack('!l', 0)
        body = json.dumps(msg).encode('utf-8')
        socket.send_multipart([key, seq_s, body])


class ObssManager(object):
    """ObssManager"""
    def __init__(self):
        super(ObssManager, self).__init__()
        self.networks = []
        self.wifiNetworks = {}
        self.pubSocket = None
        self.minChanSwitchInterval = 10
        self.avaiableChannels = [1, 6, 11]

        self.channelToFreq = {1: 2412,
                              2: 2417,
                              3: 2422,
                              4: 2427,
                              5: 2432,
                              6: 2437,
                              7: 2442,
                              8: 2447,
                              9: 2452,
                              10: 2457,
                              11: 2462,
                              12: 2467,
                              13: 2472,
                              14: 2484,
                              }

        self.freqToChannel = {v: k for k, v in self.channelToFreq.items()}

    def set_pub_socket(self, pubSocket):
        self.pubSocket = pubSocket

    def get_active_networks(self,):
        activeNets = []
        for name, net in self.wifiNetworks.items():
            if net.activated and net.requestedTraffic:
                activeNets.append(net)

        return activeNets

    def _perform_optimization(self):
        activeNets = self.get_active_networks()
        activeNetNumber = len(activeNets)
        print("Number of active networks: ", activeNetNumber)
        for n in activeNets:
            print("---Net: ", n.ctrName,
                  " Channel: ", n.channel,
                  " Traffic: ",
                  " Requested: ", n.requestedTraffic,
                  " Current: ", n.currentTraffic)

        if activeNetNumber == 0:
            # do nothing
            return

        # check if active networks are satisfied with current traffic
        for n in activeNets:
            if n.currentTraffic >= 0.8 * n.requestedTraffic:
                n.satisfied = True
            else:
                n.satisfied = False

        if activeNetNumber == 1:
            net0 = activeNets[0]

            now = time.time()
            if net0.lastOptimizationTime is None or now - net0.lastOptimizationTime > 60:
                # start checking channels
                net0.lastOptimizationTime = now
                net0.clean_thr_cache()
                net0.measurementsRunning = True

            # if no measurements return
            if not net0.measurementsRunning:
                return

            # if we have all samples
            if net0.check_cache(self.avaiableChannels):
                net0.measurementsRunning = False
                # select best channel
                thrList = []

                for ch in self.avaiableChannels:
                    channelStats = net0.throughputCache.get(ch, {})
                    thrSamples = channelStats.get("thrSamples", [])
                    # remove last as it may contain results from next channel
                    del thrSamples[-1]
                    meanThr = sum(thrSamples) / len(thrSamples)
                    thrList.append(meanThr)

                print("Mean Thr ", thrList)
                bestThr = max(thrList)
                bestChanIdx = thrList.index(bestThr)
                bestChan = self.avaiableChannels[bestChanIdx]
                print("Best channel ", bestChan)
                net0.send_switch_channel_cmd(self.pubSocket, bestChan)
                net0.channel = bestChan
                net0.lastChanSwitchTime = now
                net0.clean_thr_cache()

            # if we have samples for current channel-> switch channel
            if net0.check_cache([net0.channel]):
                newChannelIdx = self.avaiableChannels.index(net0.channel) + 1
                if newChannelIdx >= len(self.avaiableChannels):
                    newChannelIdx = 0

                newChannel = self.avaiableChannels[newChannelIdx]
                now = time.time()
                # if now-net0.lastChanSwitchTime > self.minChanSwitchInterval:
                net0.send_switch_channel_cmd(self.pubSocket, newChannel)
                net0.channel = newChannel
                net0.lastChanSwitchTime = now

        elif activeNetNumber == 2:
            # manage networks
            net0 = activeNets[0]
            net1 = activeNets[1]

            now = time.time()
            if net0.lastOptimizationTime is None or now - net0.lastOptimizationTime > 60:
                # start checking channels
                net0.lastOptimizationTime = now
                net0.clean_thr_cache()
                net0.measurementsRunning = True
                net1.lastOptimizationTime = now
                net1.clean_thr_cache()
                net1.measurementsRunning = True

            # if no measurements return
            if not net0.measurementsRunning or not net1.measurementsRunning:
                return

            # if we have all samples
            if net0.check_cache(self.avaiableChannels) and net1.check_cache(self.avaiableChannels):
                net0.measurementsRunning = False
                net1.measurementsRunning = False

                # select best channel
                thrList0 = []
                thrList1 = []

                for ch in self.avaiableChannels:
                    channelStats = net0.throughputCache.get(ch, {})
                    thrSamples = channelStats.get("thrSamples", [])
                    # remove last as it may contain results from next channel
                    del thrSamples[-1]
                    meanThr = sum(thrSamples) / len(thrSamples)
                    thrList0.append(meanThr)

                for ch in self.avaiableChannels:
                    channelStats = net1.throughputCache.get(ch, {})
                    thrSamples = channelStats.get("thrSamples", [])
                    # remove last as it may contain results from next channel
                    del thrSamples[-1]
                    meanThr = sum(thrSamples) / len(thrSamples)
                    thrList1.append(meanThr)

                print("Mean Thr 0 ", thrList0)
                bestThr0 = max(thrList0)
                bestChanIdx0 = thrList0.index(bestThr0)
                bestChan0 = self.avaiableChannels[bestChanIdx0]

                print("Mean Thr 1 ", thrList1)
                bestThr1 = max(thrList1)
                bestChanIdx1 = thrList1.index(bestThr1)
                bestChan1 = self.avaiableChannels[bestChanIdx1]

                if bestChan0 == bestChan1:
                    # get second best for worse network
                    if bestThr0 > bestThr1:
                        del thrList1[bestChanIdx1]
                        mchannels = [1, 6, 11]
                        del mchannels[bestChanIdx1]
                        bestThr1 = max(thrList1)
                        bestChanIdx1 = thrList1.index(bestThr1)
                        bestChan1 = mchannels[bestChanIdx1]
                    else:
                        del thrList0[bestChanIdx0]
                        mchannels = [1, 6, 11]
                        del mchannels[bestChanIdx0]
                        bestThr0 = max(thrList0)
                        bestChanIdx0 = thrList0.index(bestThr0)
                        bestChan0 = mchannels[bestChanIdx0]

                print("Best channel0 ", bestChan0)
                net0.send_switch_channel_cmd(self.pubSocket, bestChan0)
                net0.channel = bestChan0
                net0.lastChanSwitchTime = now
                net0.clean_thr_cache()

                print("Best channel1 ", bestChan1)
                net1.send_switch_channel_cmd(self.pubSocket, bestChan1)
                net1.channel = bestChan1
                net1.lastChanSwitchTime = now
                net1.clean_thr_cache()

            # if we have samples for current channel-> switch channel
            if net0.check_cache([net0.channel]) and net1.check_cache([net1.channel]):
                newChannelIdx0 = self.avaiableChannels.index(net0.channel) + 1
                if newChannelIdx0 >= len(self.avaiableChannels):
                    newChannelIdx0 = 0

                newChannelIdx1 = newChannelIdx0 + 1
                if newChannelIdx1 >= len(self.avaiableChannels):
                    newChannelIdx1 = 0

                newChannel = self.avaiableChannels[newChannelIdx0]
                now = time.time()
                net0.send_switch_channel_cmd(self.pubSocket, newChannel)
                net0.channel = newChannel
                net0.lastChanSwitchTime = now

                newChannel = self.avaiableChannels[newChannelIdx1]
                now = time.time()
                net1.send_switch_channel_cmd(self.pubSocket, newChannel)
                net1.channel = newChannel
                net1.lastChanSwitchTime = now

    def add_network(self, network):
        self.networks.append(network)
        wifiNetwork = WiFiNetwork(network.id, network.name,
                                  network.networkType,
                                  network.solution,
                                  network.commandList,
                                  network.monitorList)

        self.wifiNetworks[network.name] = wifiNetwork

        print("ObssManager: Managed WiFi networks")
        for name, net in self.wifiNetworks.items():
            print(net.netId, net.ctrName)

    def notify_command_msg(self, cmdMsg):
        print("ObssManager: Received Command Message")
        # print(cmdMsg)

        ctrName = cmdMsg["involvedController"][0]
        network = self.wifiNetworks.get(ctrName, None)
        if network is None:
            return

        cmdList = cmdMsg["commandList"]
        cmds = cmdList["WiFi_Channel_Switching"]

        for name, net in self.wifiNetworks.items():
            net.reset_stats()

        for commandName, commandParameters in cmds.items():
            print("ObssManager: Received Command Message: ", commandName)

            trafficSize = None

            if commandName == "ACTIVATE":
                network.activated = True
            elif commandName == "DEACTIVATE":
                network.activated = False
            elif commandName == "SWITCH_CHANNEL":
                pass

            # traffic commands
            elif commandName == "TRAFFIC":
                trafficSize = commandParameters["TYPE"]
            elif commandName == "TRAFFIC_SET_OFF":
                trafficSize = "OFF"
            elif commandName == "TRAFFIC_SET_LOW":
                trafficSize = "LOW"
            elif commandName == "TRAFFIC_SET_MEDIUM":
                trafficSize = "MEDIUM"
            elif commandName == "TRAFFIC_SET_HIGH":
                trafficSize = "HIGH"

            if trafficSize:
                requestedTraffic = 0
                if trafficSize == "OFF":
                    requestedTraffic = 0
                elif trafficSize == "LOW":
                    requestedTraffic = 1
                elif trafficSize == "MEDIUM":
                    requestedTraffic = 20
                elif trafficSize == "HIGH":
                    requestedTraffic = 100

                network.requestedTraffic = requestedTraffic
                # stay on the channel for a while
                # to measure the performance
                network.lastChanSwitchTime = time.time()

    def notify_channel_usage(self, channelUsageMsg):
        print("ObssManager: Received Channel Usage Report")
        # print(channelUsageMsg)

        ctrName = channelUsageMsg["networkController"]
        network = self.wifiNetworks.get(ctrName, None)
        if network is None:
            return

        values = channelUsageMsg["monitorValue"]
        freqUsage = values["frequencies"]
        channelUsage = values["channels"]

        oldChannel = network.channel
        try:
            network.channel = channelUsage[0]
            network.frequency = list(freqUsage.keys())[0]
            network.bandwidth = list(freqUsage.values())[0]
        except Exception:
            network.channel = None
            network.frequency = None
            network.bandwidth = None

        if oldChannel is None and network.channel is not None:
            # stay on the channel for a while
            network.lastChanSwitchTime = time.time()

    def notify_interference_report(self, interferenceReport):
        print("ObssManager: Received Interference Report")
        # print(interferenceReport)

    def notify_performance_report(self, perfomanceReport):
        print("ObssManager: Received Performance Report")
        # print(perfomanceReport)

        ctrName = perfomanceReport["networkController"]
        network = self.wifiNetworks.get(ctrName, None)
        if network is None:
            return

        values = perfomanceReport["monitorValue"]
        performance = values["PER"]
        throughput = values["THR"]

        network.performance = performance
        network.currentTraffic = throughput

        if network.channel is None:
            # wait for first channel usage report
            return

        # cache performance
        channelStats = network.throughputCache.get(network.channel, {})
        thrSamples = channelStats.get("thrSamples", [])
        thrSamples.append(throughput)
        mean = sum(thrSamples) / len(thrSamples)
        network.throughputCache[network.channel] = {"timestamp": time.time(),
                                                    "thrSamples": thrSamples,
                                                    "mean": mean}

        self._perform_optimization()
