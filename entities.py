import random as rand
import copy as copy
from enums import *
import math
from astar import *
from commands import *

class Passenger:
    def __init__(self, s, id, game):
        self.source = s
        self.dest = self.randDest(game)
        self.pay = self.calcPay()
        self.id = id

    def randDest(self, game):
        l = []
        for a in game.AIRPORTS:
            if a.code != self.source:
                l.append(a.code)
        if len(l)-1 == 0:
            return l[0]
        else:
            return l[rand.randint(0, len(l)-1)]

    def calcPay(self): 
        dist = math.dist(ALOOKUP.lookup[self.source][1], ALOOKUP.lookup[self.dest][1])
        return round(rand.randint(1,10) * dist)

class Airport:
    def __init__(self, code):
        self.code = code
        self.name = ALOOKUP.lookup[code][0]
        self.coords = ALOOKUP.lookup[code][1]
        self.planes = []
        self.passengers = []
        self.MAX_PASSENGERS = 5

    def landed(self, p_obj):
        self.planes.append(p_obj)

    def takeoff(self, p_obj):
        self.planes.remove(p_obj)

    def refreshPassengers(self, game):
        self.passengers = []
        for i in range(rand.randint(1, self.MAX_PASSENGERS)):
            self.passengers.append(Passenger(self.code, rand.randint(0,9999), game))
    
    def viewParkedPlanes(self, game):
        tmp = ""
        if len(self.planes) >= 1:
            for p in self.planes:
                for i,pobj in enumerate(game.PLANES):
                    if p.id == pobj.id:
                        if tmp == "":
                            tmp += pobj.serial
                        else:
                            tmp += ","+pobj.serial
        else:
            tmp = "None"
        return tmp


class Plane:
    def __init__(self, speed, capacity, fuel, price, st_port, rank, purchased):
        global ALOOKUP
        self.icon = ">"
        self.rank = rank
        self.id = rand.randint(0, 9999)
        self.serial = "?"
        self.coords = copy.deepcopy(ALOOKUP.lookup[st_port][1])

        self.speed = speed  # squares per hour
        self.capacity = capacity
        self.fuel = fuel
        self.price = price
        self.passengers = []
        self.direction = "r"
        self.source = st_port
        self.dest = "none"
        self.status = PlaneState.need_dest   # need dest / ready / takeoff / fly
        self.curr_flight_time = 0
        self.time_left = 0
        self.purchased = purchased

        self.path = []
        self.block_overflow = 0  # amount till next square
        self.path_step = 0

        self.trip_fuelcost = 0

    def assignSerial(self):
        global Plane_Serial
        Plane_Serial += 1
        if Plane_Serial > 65+27:
            return False
        self.serial = chr(Plane_Serial-1)
        return True

    def update(self, secs, game):
        # print("PLANE STATUS:", self.status)
        if self.status == PlaneState.fly:
            if not self.checkIfArrived(game):
                self.advancePlane(secs, game)
                self.updateTime(secs)
        if self.status == PlaneState.taking_off:
            self.status = PlaneState.fly

    def updateTime(self, secs):
        self.curr_flight_time += secs/60
        source = [ALOOKUP.lookup[self.source][1][0], ALOOKUP.lookup[self.source][1][1]]
        dest = [ALOOKUP.lookup[self.dest][1][0], ALOOKUP.lookup[self.dest][1][1]]
        dist = math.sqrt((source[0]-dest[0])*(source[0]-dest[0]) + (source[1]-dest[1])*(source[1]-dest[1]))
        self.time_left = dist/self.speed

    def checkIfArrived(self, game):
        if round(self.coords[0]) == ALOOKUP.lookup[self.dest][1][0] and round(self.coords[1]) == ALOOKUP.lookup[self.dest][1][1]:
            self.status = PlaneState.need_dest
            self.source = self.dest
            game.landPlane(self)
            self.dest = "none"
            self.time_left = 0
            self.path = []
            self.path_step = 0
            game.CASH += self.getRevenue()
            game.MsgQueue.put(Message("Plane %s has landed! Loc: %s Earned: $%s" % (self.id, self.source, self.getRevenue()), MessageType.IMPORTANT))
            game.StatTracker.TotalRevenue += self.getRevenue()
            for p in self.passengers:
                if p.dest == self.source:
                    game.StatTracker.AirportRevenue[p.dest] += p.pay
                    game.StatTracker.PlaneTrips[self.id]["Passengers"] += 1
                    game.Leveler.addXP(1, game)
            game.StatTracker.PlaneTrips[self.id]["Trips"] += 1
            game.StatTracker.PlaneTrips[self.id]["CpM"] += round(self.getRevenue() / self.curr_flight_time, 2)
            self.unloadPassengers()
            self.curr_flight_time = 0
            if game.Commands.debugmode:
                print("ARRIVED STATE:", self.status)
            return True
        return False

    def unloadPassengers(self):
        for p in self.passengers:
            if p.dest == self.source:
                self.passengers.remove(p)

    def getRevenue(self):
        tmppay = 0
        for p in self.passengers:
            if p.dest == self.source:
                tmppay += p.pay
        return tmppay

    def takeoff(self, game):
        self.updateIcon(self.findDirVector(ALOOKUP.lookup[self.source][1], ALOOKUP.lookup[self.dest][1]))
        self.status = PlaneState.taking_off
        self.createPath(game)
        self.updateTime(0)
    
    def createPath(self, game):
        st = (ALOOKUP.lookup[self.source][1][0], ALOOKUP.lookup[self.source][1][1])
        end = (ALOOKUP.lookup[self.dest][1][0], ALOOKUP.lookup[self.dest][1][1])
        if game.Commands.debugmode.action:
            print(st, end)
        p_coords = astar(st, end)
        if game.Commands.debugmode.action:
            print(p_coords)
        for i,p in enumerate(p_coords):
            if i != 0 and i != len(p_coords)-1:
                xdiff = p_coords[i+1][0] - p_coords[i-1][0]
                ydiff = p_coords[i+1][1] - p_coords[i-1][1]
                if xdiff == 0:
                    self.path.append([p, "|"])
                elif ydiff == 0:
                    self.path.append([p, "-"])
                elif (xdiff > 0 and ydiff > 0) or (xdiff < 0 and ydiff < 0):
                    self.path.append([p, "\\"])
                elif (xdiff > 0 and ydiff < 0) or (xdiff < 0 and ydiff > 0):
                    self.path.append([p, "/"])
            else:
                self.path.append([p, "+"])
        if game.Commands.debugmode.action:
            print(self.path)

    def advancePlane(self, secs, game):
        dist = (self.speed / 60 * secs) + self.block_overflow
        self.block_overflow = dist - math.floor(dist)
        if math.floor(dist) + self.path_step > len(self.path):
            self.path_step = len(self.path)-1
        else:
            self.path_step += math.floor(dist)
        self.coords = self.path[self.path_step][0]
        if game.Commands.debugmode.action:
            print("Plane[%s]: Step: %s, Overflow: %s, addtostep: %s" % (self.id, self.path_step, self.block_overflow, math.floor(dist)))

    def findDirVector(self, source, dest):
        mx = abs(source[0] - dest[0])
        my = abs(source[1] - dest[1])
        if my > mx:
            if dest[1] - source[1] < 0:
                return "up"
            else:
                return "down"
        else:
            if dest[0] - source[0] < 0:
                return "left"
            else:
                return "right"

    def updateIcon(self, dir):
        if dir == "up":
            self.icon = "^"
        elif dir == "right":
            self.icon = ">"
        elif dir == "down":
            self.icon = "v"
        elif dir == "left":
            self.icon = "<"
        else:
            self.icon = "!"

class Cloud:
    def __init__(self):
        self.mrows = 5
        self.mcols = 10
        self.rows = rand.randint(3,self.mrows)
        self.cols = rand.randint(3,self.mcols)
        self.area = []
        self.info = []
        self.pos = [rand.randint(0,MAP_R-1), rand.randint(0,MAP_C-1)]
        self.realpos = [0,0]     # keep track of overflow
        self.icon = '#'
        self.direction = rand.randint(0,359)
        self.speed = 3
        self.lifecycle = 60*24  # 1 day
        self.newCloud()

    def isPlaneDead(self, pos):
        for r,row in enumerate(self.area):
            for c,col in enumerate(row):
                if col == 1 and self.pos[0]+r == pos[0] and self.pos[1]+c == pos[1]:
                    return True
        return False

    def newCloud(self):
        for r in range(self.rows):
            cloudr = []
            infor = []
            for c in range(self.cols):
                if not ((c==0 or c==self.cols-1) and (r==0 or r== self.rows-1)) and rand.randint(1,2) % 2 == 0:
                    cloudr.append(1)
                else:
                    cloudr.append(0)
                # if r == 0 or c == 0 or r == self.rows-1 or c == self.cols-1:
                #     infor.append('.')
                # else:
                infor.append('')
            # infor.append('')    # one more col
            self.area.append(cloudr)
            self.info.append(infor)
        # # one more row
        # infor = []
        # for c in range(self.cols+1):
        #     infor.append('')
        # self.info.append(infor)

        center = [round((self.rows-1)/2), round((self.cols-1)/2)]
        centeradd = []
        if self.direction > 337.5 or self.direction < 22.5:
            symbol = '|'
            centeradd = [1, 0]
        elif self.direction >= 22.5 and self.direction <= 67.5:
            symbol = '\\'
            centeradd = [1, 1]
        elif self.direction > 67.5 and self.direction < 112.5:
            symbol = '-'
            centeradd = [0, 1]
        elif self.direction >= 112.5 and self.direction <= 157.5:
            symbol = '/'
            centeradd = [-1, 1]
        elif self.direction > 157.5 and self.direction < 202.5:
            symbol = '|'
            centeradd = [-1, 0]
        elif self.direction >= 202.5 and self.direction <= 247.5:
            symbol = '\\'
            centeradd = [-1, -1]
        elif self.direction > 247.5 and self.direction <= 292.5:
            symbol = '-'
            centeradd = [0, -1]
        elif self.direction >= 292.5 and self.direction <= 337.5:
            symbol = '/'
            centeradd = [1, -1]
        else:
            symbol = '?'
        self.info[center[0]][center[1]] = symbol
        self.info[center[0]+centeradd[0]][center[1]+centeradd[1]] = '*'
    
    def roundAndSaveOverflow(self, rp, p):
        if p > round(p):
            rp = p - round(p)
        else:
            rp = round(p) - p
        return rp, round(p)
    
    def update(self, secs, map):
        # print(self.realpos, self.pos)
        m = self.speed * (secs / 60)
        mx = m * MAP_R / MAP_C  # normalize columns vs rows
        dircol = math.sin(math.radians(self.direction))
        dirrow = math.cos(math.radians(self.direction))
        self.pos[0] += self.realpos[0] + m * dirrow
        self.pos[1] += self.realpos[1] + mx * dircol
        self.pos[0] = map.rowToMap(self.pos[0])
        self.pos[1] = map.colToMap(self.pos[1])
        self.realpos[0] = self.pos[0] - round(self.pos[0])
        self.realpos[1] = self.pos[1] - round(self.pos[1])
        self.pos[0] = round(self.pos[0])
        self.pos[1] = round(self.pos[1])
        # print(secs, self.realpos, self.pos, m, mx, self.direction, dirrow, dircol)

        if self.lifecycle - 1 <= 0:
            return False
        else:
            return True

