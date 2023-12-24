"""
A hybrid TDMA CSMA MAC based on Atheros and ath9k wifi driver
"""
class HybridTDMACSMAMac():
    def __init__(self, no_slots_in_superframe, slot_duration_ns):
        #super(HybridTDMACSMAMac,self).__init__()
        self.name = "hybridTDMACSMA"
        self.desc = "works w/ ath9k"
        self.mNo_slots_in_superframe = no_slots_in_superframe
        self.mSlot_duration_ns = slot_duration_ns
        self.acs = []
        for ii in range(no_slots_in_superframe):
            self.acs.append(None)

    def getNumSlots(self):
        return self.mNo_slots_in_superframe

    def addAccessPolicy(self, slot_nr, ac):
        self.acs[slot_nr] = ac

    def getAccessPolicy(self, slot_nr):
        return self.acs[slot_nr]

    def getSlotDuration(self):
        return self.mSlot_duration_ns

    def printConfiguration(self):
        s = '['
        for ii in range(self.getNumSlots()):
            s = s + str(ii) + ': ' + self.getAccessPolicy(ii).printConfiguration() + "\n"
        s = s + ']'
        return s



"""
AccessPolicy for each slot
"""
class AccessPolicy(object):

    def __init__(self):
        self.entries = []

    def disableAll(self):
        self.entries = []

    def allowAll(self):
        self.entries = []
        self.entries.append(('FF:FF:FF:FF:FF:FF', 255))

    def addDestMacAndTosValues(self, dstHwAddr, *tosArgs):
        """add destination mac address and list of ToS fields
        :param dstHwAddr: destination mac address
        :param tosArgs: list of ToS values to be allowed here
        """
        tid_map = 0
        for ii in range(len(tosArgs)):
            # convert ToS into tid
            tos = tosArgs[ii]
            skb_prio = tos & 30 >> 1
            tid =skb_prio & 7
            tid_map = tid_map | 2**tid

        self.entries.append((dstHwAddr, tid_map))

    def getEntries(self):
        return self.entries

    def printConfiguration(self):
        s = ''
        for ii in range(len(self.entries)):
            s = str(self.entries[ii][0]) + "/" + str(self.entries[ii][1]) + "," + s
        return s