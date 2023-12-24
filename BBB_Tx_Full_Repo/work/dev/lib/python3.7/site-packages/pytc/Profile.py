__author__ = 'P.Gawlowicz'

class Profile(object):
    """Usage: ... netem [ limit PACKETS ]
           [ delay TIME [ JITTER [CORRELATION]]]
           [ distribution {uniform|normal|pareto|paretonormal} ]
           [ drop PERCENT [CORRELATION]]
           [ corrupt PERCENT [CORRELATION]]
           [ duplicate PERCENT [CORRELATION]]
           [ reorder PRECENT [CORRELATION] [ gap DISTANCE ]])
    """

    UNIFORM="uniform"
    NORMAL="normal"
    PARETO="pareto"
    PARETONORMAL="paretonormal"

    def __init__(self, name):
        self.name = name
        self.plimit = 1000
        self.blimit = 10000
        self.rate = 1000
        self.burst = 10*1024
        self.delay = {}
        self.delay["TIME"] = 0
        self.delay["JITTER"] = 0
        self.delay["CORRELATION"] = 0
        self.distribution = self.UNIFORM
        self.loss = {}
        self.loss["PERCENT"] = 0
        self.loss["CORRELATION"] = 0
        self.corruption = {}
        self.corruption["PERCENT"] = 0
        self.corruption["CORRELATION"] = 0
        self.duplication = {}
        self.duplication["PERCENT"] = 0
        self.duplication["CORRELATION"] = 0
        self.reorder = {}
        self.reorder["PERCENT"] = 0
        self.reorder["CORRELATION"] = 0
        self.reorder["GAP"] = 0

    def save(self, filename):
        pass

    def load(self, filename):
        pass

    def setPacketLimit(self, limit=1000):
        self.plimit = limit
        pass
        
    def getPacketLimit(self):
        return self.plimit

    def setByteLimit(self, limit=10000):
        self.blimit = limit
        pass
        
    def getByteLimit(self):
        return self.blimit


    def setRate(self, rate=1000):
        self.rate = rate
        pass
 
    def setBurst(self, burst=10*1024):
        self.burst = burst
        pass

    def getRate(self):
        return self.rate

    def setDelay(self, delay=0, jitter=0, correlation=0, distribution=UNIFORM):
        self.delay["TIME"] = delay
        self.delay["JITTER"] = jitter
        self.delay["CORRELATION"] = correlation
        self.distribution = distribution
        pass
        
    def getDelay(self):
        time = self.delay["TIME"] = 0
        jitter = self.delay["JITTER"] = 0
        corr = self.delay["CORRELATION"] = 0
        dist = self.distribution = self.UNIFORM
        ret = [time, jitter, corr, dist]
        return ret     

    def setLoss(self, percent=0, correlation=0):
        self.loss["PERCENT"] = percent
        self.loss["CORRELATION"] = correlation
        pass
        
    def getLoss(self):
        percent = self.loss["PERCENT"]
        correlation = self.loss["CORRELATION"]
        ret = [percent, correlation]
        return ret

    def setCorruption(self, percent=0, correlation=0):
        self.corruption["PERCENT"] = percent
        self.corruption["CORRELATION"] = correlation
        pass
        
    def getCorruption(self):
        percent = self.corruption["PERCENT"]
        correlation = self.corruption["CORRELATION"]
        ret = [percent, correlation]
        return ret

    def setDuplication(self, percent=0, correlation=0):
        self.duplication["PERCENT"] = percent
        self.duplication["CORRELATION"] = correlation
        pass
        
    def getDuplication(self):
        percent = self.duplication["PERCENT"]
        correlation = self.duplication["CORRELATION"]
        ret = [percent, correlation]
        return ret

    def setReorder(self, percent=0, correlation=0, gap=0):
        self.reorder["PERCENT"] = percent
        self.reorder["CORRELATION"] = correlation
        self.reorder["GAP"] = gap
        pass
        
    def getReorder(self):
        percent = self.reorder["PERCENT"]
        correlation = self.reorder["CORRELATION"]
        gap = self.reorder["GAP"]
        ret = [percent, correlation, gap]
        return ret

class Profile2gWeak(Profile):
    def __init__(self):
        super(Profile2gWeak,self).__init__("Profile2gWeak")
        self.rate = 420
        self.delay["TIME"] = 100

class Profile3gGood(Profile):
    def __init__(self):
        super(Profile3gGood,self).__init__("Profile3gGood")
        self.rate = 4200
        self.delay["TIME"] = 80