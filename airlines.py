import math
import time 
import random as rand
import os
import copy as copy
import pickle
from turtle import color
from queue import Queue
from enums import *
from store import Store
from leveler import *
from commands import *
from entities import *
from menu import *

os.system('color')

class Game:
    def __init__(self):
        self.playing = True
        self.PAGE = Page.default
        self.DontSave = False
        self.STARTING_CASH = 100
        self.CASH = self.STARTING_CASH
        self.store = Store()
        self.store.refreshPlaneMarket(True, self)
        self.Leveler = Leveler()
        self.Commands = Commands()

        self.maxweather = 7
        self.newcloudtimer = [15,15]   # current time to new cloud, 15 mins
        self.clouds = [Cloud()]

        self.a_view = 0     # current airport view
        self.p_view = 0     # current plane view

        self.PLANES = []
        self.AIRPORTS = []
        # for a in ALOOKUP:
        #     if a != "None":
        #         self.AIRPORTS.append(Airport(a, self))
        self.AIRPORTS.append(Airport("JFK"))
        self.AIRPORTS.append(Airport("LAX"))
        p = Plane(1, 1, 3, 500, "LAX", "C", True)
        p.assignSerial()
        self.PLANES.append(p)
        self.landPlane(p, notrack=True)

        self.StatTracker = StatTracker()
        self.StatTracker.AirportRevenue["JFK"] = 0
        self.StatTracker.AirportRevenue["LAX"] = 0
        self.StatTracker.PlaneTrips[p.id] = {}
        self.StatTracker.PlaneTrips[p.id]["Rank"] = p.rank
        self.StatTracker.PlaneTrips[p.id]["Trips"] = 0
        self.StatTracker.PlaneTrips[p.id]["Passengers"] = 0
        self.StatTracker.PlaneTrips[p.id]["CpM"] = 0

        self.MsgQueue = Queue()
        self.Msg = ''

        self.currentTime = time.time()
        self.SCREEN = Screen(self)

        self.flightpaths = False

        for a in self.AIRPORTS:
            a.refreshPassengers(self)


    def main(self):
        while self.playing:
            if not self.Commands.debugmode.action:
                os.system("cls")
            self.updateTime(time.time())
            self.pageRefresh()
            self.currentTime = time.time()
            if not self.MsgQueue.empty():
                msgitem = self.MsgQueue.get()
                self.Msg = f'{msgitem.type}{msgitem.msg}{msgitem.type}'
            else:
                self.Msg = ''
            self.SCREEN.print()
            c = input("Command: ")
            self.cmds(c)

    def cmds(self, ch):
        if ch == "Q" or ch == "quit" or ch == "Quit":
            if not self.DontSave:
                self.saveGame()
            self.playing = False
        else:
            self.Commands.runCmd(ch)

        if self.PAGE == Page.airports:
            if ch == "r" or ch == "R":
                for a in self.AIRPORTS:
                    a.refreshPassengers(self)
                self.MsgQueue.put(Message("Passengers Refreshed!", MessageType.IMPORTANT))
            elif len(ch) == 3 and (ch[0] == "l" or ch[0] == "L"):
                self.loadPassengerIntoPlane(ch)
            elif ch == "b" or ch == "B":
                self.PAGE = Page.default
                #self.MsgQueue.put("")
            elif ch == "x" or ch == "X":
                if self.a_view + 1 < len(self.AIRPORTS):
                    self.a_view += 1
                else:
                    self.a_view = 0
                #self.MsgQueue.put("")
            elif ch == "z" or ch == "Z":
                if self.a_view - 1 > -1:
                    self.a_view -= 1
                else:
                    self.a_view = len(self.AIRPORTS)-1
                #self.MsgQueue.put("")
        if self.PAGE == Page.planes:
            if len(ch) == 2 and (ch[0] == "R" or ch[0] == "r"):
                self.offLoadPassengerToAirport(ch)
            elif ch == "b" or ch == "B":
                self.PAGE = Page.default
                #self.MsgQueue.put("")
            elif ch == "x" or ch == "X":
                if self.p_view + 1 < len(self.PLANES):
                    self.p_view += 1
                else:
                    self.p_view = 0
            elif ch == "z" or ch == "Z":
                if self.p_view - 1 > -1:
                    self.p_view -= 1
                else:
                    self.p_view = len(self.PLANES)-1
            elif self.PLANES[self.p_view].status == PlaneState.need_dest:
                if len(ch) == 4 and (ch[0] == "D" or ch[0] == "d"):
                    self.setPlaneDest(ch, self.PLANES[self.p_view])
            elif self.PLANES[self.p_view].status == PlaneState.ready:
                if len(ch) == 1 and (ch == "F" or ch == "f"):
                    self.flyPlane(self.PLANES[self.p_view])
                elif len(ch) == 1 and (ch == "C" or ch == "c"):
                    self.PLANES[self.p_view].status = PlaneState.need_dest
                    self.PLANES[self.p_view].dest = "none"
                    self.MsgQueue.put(Message("Flight Canceled", MessageType.IMPORTANT))
        if self.PAGE == Page.store:
            if ch == "b" or ch == "B":
                self.PAGE = Page.default
                #self.MsgQueue.put("")
            elif ch == "c" or ch == "C":
                self.PAGE = Page.construct
            elif ch == "m" or ch == "M":
                self.PAGE = Page.market
        elif self.PAGE == Page.market:
            if ch == "b" or ch == "B":
                self.PAGE = Page.store
                #self.MsgQueue.put("")
            elif ch == "r":
                self.store.refreshPlaneMarket(False, self)
            elif len(ch) == 5 and (ch[0] == "P" or ch[0] == "p"):
                self.buyPlane(ch)
        elif self.PAGE == Page.construct:
            if ch == "b" or ch == "B":
                self.PAGE = Page.store
                #self.MsgQueue.put("")
            elif ch == "a" or ch == "A":
                self.unlockNewAirport()
        elif self.PAGE == Page.about:
            if ch == "b" or ch == "B":
                self.PAGE = Page.default
                #self.MsgQueue.put("")
        elif self.PAGE == Page.commands:
            if ch == "b" or ch == "B":
                self.PAGE = Page.default
                #self.MsgQueue.put("")
        elif self.PAGE == Page.stats:
            if ch == "b" or ch == "B":
                self.PAGE = Page.default
                #self.MsgQueue.put("")
            elif ch == "t" or ch == "T":
                if self.SCREEN.menu.StatViewPlaneView:
                    self.SCREEN.menu.StatViewPlaneView = False
                else:
                    self.SCREEN.menu.StatViewPlaneView = True
            elif ch == '?':
                self.MsgQueue.put(Message(self.StatTracker.getInfo(self.SCREEN.menu.StatViewPlaneView)))
        elif self.PAGE == Page.default:
            #self.MsgQueue.put("")
            if ch == "a" or ch == "A":
                self.PAGE = Page.airports
            elif ch == "p" or ch == "P":
                self.PAGE = Page.planes
            elif ch == "m" or ch == "M":
                self.PAGE = Page.store
            elif ch == "R":
                self.DontSave = True
                self.clearSave()
                self.playing = False
            elif ch == "O" or ch == "o":
                self.PAGE = Page.about
            elif ch == "C" or ch == "c":
                self.PAGE = Page.commands
            elif ch == "S" or ch == "s":
                self.PAGE = Page.stats
            elif ch == "L" or ch == "l":
                self.Leveler.addXP(1, self)
            
    def pageRefresh(self):
        if self.PAGE == Page.airports:
            self.SCREEN.menu.gotoAirports()
        elif self.PAGE == Page.planes:
            self.SCREEN.menu.gotoPlanes()
        elif self.PAGE == Page.store:
            self.SCREEN.menu.gotoStore()
        elif self.PAGE == Page.market:
            self.SCREEN.menu.gotoMarket()
        elif self.PAGE == Page.about:
            self.SCREEN.menu.gotoAbout()
        elif self.PAGE == Page.construct:
            self.SCREEN.menu.gotoConstructAirport(self)
        elif self.PAGE == Page.commands:
            self.SCREEN.menu.gotoCommands(self)
        elif self.PAGE == Page.stats:
            self.SCREEN.menu.gotoStatTracker()
        else:
            self.SCREEN.menu.gotoMain()

    def unlockNewAirport(self):
        if len(self.AIRPORTS) > len(self.store.airport_prices):
            cost = self.store.airport_prices[-1]
        else:
            cost = self.store.airport_prices[len(self.AIRPORTS)]
        if self.CASH - cost < 0:
            self.SCREEN.menu.airport_unlock = -1
        else:
            self.SCREEN.menu.airport_unlock = 1

    def setPlaneDest(self, c, p_obj):
        code = c[1] + c[2] + c[3]
        if code == p_obj.source:
            self.MsgQueue.put(Message("%sFailed%s: Plane is parked here!"%(ALERT_CODE,END_CODE),MessageType.ALERT))
        else:
            r = ALOOKUP.lookup[code]
            if r:
                p_obj.dest = code
                p_obj.status = PlaneState.ready
                self.MsgQueue.put(Message("Destination set for %s!" % ALOOKUP.lookup[code][0]))
                p_obj.trip_fuelcost = round(math.dist(ALOOKUP.lookup[p_obj.source][1], ALOOKUP.lookup[p_obj.dest][1]) * p_obj.fuel)
            else:
                self.MsgQueue.put(Message("%sFailed%s: Incorrect airport code"%(ALERT_CODE,END_CODE),MessageType.ALERT))

    def landPlane(self, p_obj, notrack=False):
        for a in self.AIRPORTS:
            if a.code == p_obj.source:
                a.landed(p_obj)
                if not notrack:
                    self.StatTracker.TotalFlights += 1

    def buyPlane(self, ch):
        ind = self.charToNum(ch[1]) - 1
        if ind >= 0 and ind < len(self.store.planes_available):
            plane_c = self.store.planes_available[ind]
            a_code = ch[2] + ch[3] + ch[4]
            airport_ind = self.findOwnedAirportByCode(a_code) 
            if airport_ind != -1:
                if self.CASH - plane_c.price >= 0:
                    if not plane_c.purchased:
                        np = Plane(plane_c.speed, plane_c.capacity, plane_c.fuel, plane_c.price, self.AIRPORTS[airport_ind].code, plane_c.rank, True)
                        if not np.assignSerial():
                            self.PLANES.append(np)
                            self.StatTracker.PlaneTrips[np.id]["Rank"] = np.rank
                            self.StatTracker.PlaneTrips[np.id]["Trips"] = 0
                            self.StatTracker.PlaneTrips[np.id]["Passengers"] = 0
                            self.StatTracker.PlaneTrips[np.id]["CpM"] = 0
                            self.landPlane(np)
                            plane_c.purchased = True
                            self.CASH -= plane_c.price
                            self.MsgQueue.put(Message("Purchased Plane[%s] for $%s! - Loc: %s" % (plane_c.id, plane_c.price, self.AIRPORTS[airport_ind].code),MessageType.IMPORTANT))
                        else:
                            self.MsgQueue.put(Message("%sFailed%s: No more space for planes!"%(ALERT_CODE,END_CODE),MessageType.ALERT))
                    else:
                        self.MsgQueue.put(Message("%sFailed%s: Plane is not purchasable!"%(ALERT_CODE,END_CODE),MessageType.ALERT))
                else:
                    self.MsgQueue.put(Message("%sFailed%s: Not enough cash"%(ALERT_CODE,END_CODE),MessageType.ALERT))
            else:
                self.MsgQueue.put(Message("%sFailed%s: Incorrect airport code"%(ALERT_CODE,END_CODE),MessageType.ALERT))
        else:
            self.MsgQueue.put(Message("%sFailed%s: Cannot buy Plane (%s)" % (ALERT_CODE,END_CODE,ind),MessageType.ALERT))

    def flyPlane(self, p_obj):
        # print(f'Dest: {ALOOKUP[p_obj.dest]}\nDist: {math.dist(ALOOKUP[p_obj.source][1], ALOOKUP[p_obj.dest][1])}\nFuel: {p_obj.fuel}')
        if self.CASH - p_obj.trip_fuelcost > 0:
            self.CASH -= p_obj.trip_fuelcost
            p_obj.takeoff(self)
            self.MsgQueue.put(Message("Plane [%s] cleared for takeoff!" % p_obj.id,MessageType.IMPORTANT))
            for a in self.AIRPORTS:
                if a.code == p_obj.source:
                    a.takeoff(p_obj)
        else:
            self.MsgQueue.put(Message("%sFailed%s: Fuel cost too expensive!"%(ALERT_CODE, END_CODE), MessageType.ALERT))

    def offLoadPassengerToAirport(self, ch):
        person_choice = ord(ch[1])-97
        if person_choice >= 0 and person_choice < len(self.PLANES[self.p_view].passengers):
            p_obj = self.PLANES[self.p_view].passengers[person_choice]
            if self.PLANES[self.p_view].status != PlaneState.fly:
                airport_ind = self.findOwnedAirportByCode(p_obj.source)
                if airport_ind != -1:
                    self.AIRPORTS[airport_ind].passengers.append(p_obj)
                    self.PLANES[self.p_view].passengers.remove(p_obj)
                    self.MsgQueue.put(Message("Passenger [%s] unloaded off Plane [%s] back to Airport [%s]" % (p_obj.id, self.PLANES[self.p_view].id, p_obj.source)))
                else:      
                    self.MsgQueue.put(Message("%sFailed%s: Could not find Airport [%s] to offload Passenger [%s] to" % (ALERT_CODE,END_CODE,p_obj.source, p_obj.id), MessageType.ALERT))
            else:
                self.MsgQueue.put(Message("%sFailed%s: Cannot throw passenger out of plane for fun!"%(ALERT_CODE,END_CODE), MessageType.ALERT))
        else:
            self.MsgQueue.put(Message("%sFailed%s: Could not find passenger!"%(ALERT_CODE,END_CODE), MessageType.ALERT))

    def CheckForRefreshPassengerList(self):
        if not len(self.AIRPORTS[self.a_view].passengers):
            self.AIRPORTS[self.a_view].refreshPassengers(self)
        
    def loadPassengerIntoPlane(self, ch):
        person_choice = ord(ch[1])-97
        if person_choice < len(self.AIRPORTS[self.a_view].passengers) and person_choice >= 0:
            p_obj = self.AIRPORTS[self.a_view].passengers[person_choice]
            pchoice = ch[2].upper()
            p_index = -1
            for i, pl in enumerate(self.PLANES):
                if pl.serial == pchoice:
                    p_index = i
            if not p_index == -1:
                if len(self.PLANES[p_index].passengers) < self.PLANES[p_index].capacity:
                    if p_obj.source == self.PLANES[p_index].source:
                        self.PLANES[p_index].passengers.append(p_obj)
                        self.AIRPORTS[self.a_view].passengers.remove(p_obj)
                        self.MsgQueue.put(Message(f"Passenger [{p_obj.id}] loaded into Plane {str(pchoice)} [{self.PLANES[p_index].id}]"))
                        self.CheckForRefreshPassengerList()
                    else:
                        self.MsgQueue.put(Message("%sFailed%s: Plane %s is not parked at %s!" % (ALERT_CODE,END_CODE,pchoice, p_obj.source),MessageType.ALERT))
                else:
                    self.MsgQueue.put(Message("%sFailed%s: Plane at max capacity!"%(ALERT_CODE,END_CODE), MessageType.ALERT))
            else:
                self.MsgQueue.put(Message("%sFailed%s: Plane %s does not exist!" % (ALERT_CODE,END_CODE,pchoice), MessageType.ALERT))
        else:
            self.MsgQueue.put(Message("%sFailed%s: Invalid passenger!"%(ALERT_CODE,END_CODE), MessageType.ALERT))

    def updateTime(self, new_time):
        sec_diff = new_time - self.currentTime
        # planes
        for p in self.PLANES:
            p.update(sec_diff, self)
        # weather
        death = []
        for d,c in enumerate(self.clouds):
            if not c.update(sec_diff, self.SCREEN.map):
                death.append(d)

        if death:
            cloudsave = []
            for d,c in enumerate(self.clouds):
                if not d in death:
                    cloudsave.append(c)
            self.clouds = cloudsave
        # subtract time away from game from timer
        # timer will be 0 or negative
        self.newcloudtimer[0] -= sec_diff/60
        while self.newcloudtimer[0] < self.newcloudtimer[1]:
            # try to generate a cloud, for every maxtimer unit of time
            # away from game, will attempt to generate a new cloud
            # done when timer is back above maxtimer
            self.newcloudtimer[0] += self.newcloudtimer[1]
            if self.newcloudtimer[0] <= 0 and self.maxweather > len(self.clouds):
                if rand.randint(1, 100) < 10:
                    self.clouds.append(Cloud())

        # check for plane death
        planesave = []
        for p in self.PLANES:
            for c in self.clouds:
                if not c.isPlaneDead(p.coords):
                    planesave.append(p)
        self.PLANES = planesave


    def saveGame(self):
        saver = Saver(self.CASH, self.PLANES, self.AIRPORTS, self.store.planes_available, self.currentTime, self.StatTracker, self.Leveler.xp, self.Leveler.level, self.Leveler.xpfornext, self.clouds)
        with open(SAVE_FILE_NAME, "wb") as outfile:
            pickle.dump(saver, outfile)
        print("DATA SAVED")

    def clearSave(self):
        if os.path.exists(SAVE_FILE_NAME):
            os.remove(SAVE_FILE_NAME)
            print("DATA DELETED")

    def charToIndex(self, c):
        return ord(c)-97
    
    def charToNum(self, c):
        return ord(c)-48

    def findOwnedAirportByCode(self, code):
        for a in range(len(self.AIRPORTS)):
            if self.AIRPORTS[a].code == code:
                return a
        return -1

    def loadGame(self):
        if os.path.exists(SAVE_FILE_NAME):
            print("LOADING")
            with open(SAVE_FILE_NAME, "rb") as infile:
                saver = pickle.load(infile)
                self.CASH = saver.CASH
                self.PLANES = saver.PLANES
                for p in self.PLANES:
                    if self.Commands.debugmode.action:
                        print(p.status)
                self.AIRPORTS = saver.AIRPORTS
                self.store.planes_available = saver.store_planes
                self.currentTime = saver.save_time
                self.StatTracker = saver.StatTracker
                self.Leveler.xp = saver.xp
                self.Leveler.level = saver.level
                self.Leveler.xpfornext = saver.xpfornext
                self.clouds = saver.clouds

g = Game()
g.loadGame()
g.main()