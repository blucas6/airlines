from commands import *

class Leveler():
    def __init__(self):
        self.level = 1
        self.xp = 0
        self.xpfornext = 1
    
    def levelup(self, game):
        self.xp -= self.xpfornext
        self.level += 1
        self.xpfornext *= 2
        game.MsgQueue.put(Message("Leveled up! New Level -> %s"%(self.level), MessageType.IMPORTANT))
    
    def addXP(self, xp, game):
        self.xp += xp
        while self.xp >= self.xpfornext:
            self.levelup(game)

class StatTracker():
    def __init__(self):
        self.TotalFlights = 0
        self.TotalRevenue = 0
        self.AirportRevenue = {}    # { airportcode: total generated revenue }
        self.PlaneTrips = {}        # { plane ID: {Rank: plane rank, Trips: total trips taken, Passengers: total passengers flown, CpM: cash generated per flight minute} }
    
    def getInfo(self, isforplanes):
        if isforplanes:
            return 'Info: T=Total Trips, P=Total Passengers, CpM=Cash generated per flight Minute'
        else:
            return 'Info: Total generated revenue per airport'

class Saver:
    def __init__(self, cash, plane_l, airport_l, store_planes_l, current_time, stat_tracker, xp, level, xpfornext, cloudlist):
        self.CASH = cash
        self.PLANES = plane_l
        self.AIRPORTS = airport_l
        self.store_planes = store_planes_l
        self.save_time = current_time
        self.StatTracker = stat_tracker
        self.xp = xp
        self.level = level
        self.xpfornext = xpfornext
        self.clouds = cloudlist