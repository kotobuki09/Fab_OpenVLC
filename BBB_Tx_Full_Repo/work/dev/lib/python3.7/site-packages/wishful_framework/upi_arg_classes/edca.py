__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class EdcaQueueParameters(object):
    def __init__(self, aifs=1, cwmin=1, cwmax=1023, txop=0):
        self.setAifs(aifs)
        self.setCwMin(cwmin)
        self.setCwMax(cwmax)
        self.setTxOp(txop)
        pass

    def setAifs(self, value):
        if value < 0:
            value = 0
        if value > 255:
            value = 255

        self.mAifs = value
        pass
    
    def getAifs(self):
        return self.mAifs

    def setCwMin(self, value):
        if (value <= 1):
            value = 1
        if (1 < value <= 3):
            value = 3
        if (3 < value <= 7):
            value = 7
        if (7 < value <= 15):
            value = 15
        if (15 < value <= 31):
            value = 31
        if (31 < value <= 63):
            value = 63
        if (63 < value <= 127):
            value = 127
        if (127 < value <= 255):
            value = 255
        if (255 < value <= 511):
            value = 511
        if (511 < value):
            value = 1023           

        self.mCwMin = value
        pass

    def getCwMin(self):
        return self.mCwMin

    def setCwMax(self, value):
        if (value <= 1):
            value = 1
        if (1 < value <= 3):
            value = 3
        if (3 < value <= 7):
            value = 7
        if (7 < value <= 15):
            value = 15
        if (15 < value <= 31):
            value = 31
        if (31 < value <= 63):
            value = 63
        if (63 < value <= 127):
            value = 127
        if (127 < value <= 255):
            value = 255
        if (255 < value <= 511):
            value = 511
        if (511 < value):
            value = 1023   
        self.mCwMax = value
        pass

    def getCwMax(self):
        return self.mCwMax

    def setTxOp(self, value):
        if (value <= 0):
            value = 0
        if (value > 999):
            value = 999

        self.mTxOp = value
        pass

    def getTxOp(self):
        return self.mTxOp