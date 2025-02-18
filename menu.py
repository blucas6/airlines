from enums import *
import datetime as dt
from world import Map
import random as rand
from commands import *
from entities import *

class Title:
    def __init__(self):
        self.offr = 1
        self.offc = 2
        self.w = 40-1
        self.h = 9
        self.main = []
        for r in range(self.h):
            self.main.append([])
        self.main[0] = r"  __    __   ____                "
        self.main[1] = r" / _\  (  ) (  _ \               "
        self.main[2] = r"/    \  )(   )   /               "
        self.main[3] = r"\_/\_/ (__) (__\_)               "
        self.main[4] = r" __     __   __ _   ____   ____  "
        self.main[5] = r"(  )   (  ) (  ( \ (  __) / ___) "
        self.main[6] = r"/ (_/\  )(  /    /  ) _)  \___ \ "
        self.main[7] = r"\____/ (__) \_)__) (____) (____/ "
        self.main[8] = r"---------------------------------"

class Menu:
    def __init__(self, g):
        self.game = g
        self.offc = 2
        self.offr = 10
        self.w = 40
        self.h = CONSOLE_R-1
        self.main = []

        self.reset()
        self.gotoMain()

        self.PAL = Pallette()

        self.airport_unlock = 0     # -1: failed, 0: buy option, 1: successful buy
        self.StatViewPlaneView = True

    def reset(self):
        self.main = []
        for r in range(self.h):
            self.main.append([])

    def gotoAbout(self):
        self.reset()
        self.main[0] = "       -={About}=-"
        self.main[1] = ""
        self.main[2] = " Created by Benjamin Lucas"
        self.main[3] = "          2022"
        self.main[4] = ""
        self.main[5] = ""

    def gotoMain(self):
        levelbar = 10
        currxp = round((self.game.Leveler.xp / self.game.Leveler.xpfornext)*levelbar)*'#'
        nextxp = round(levelbar - len(currxp))*' '
        self.reset()
        self.main[0] = "     -={Main Menu}=-"
        self.main[1] = " [Universal Time: %s:%s:%s]" % (dt.datetime.now().hour, dt.datetime.now().minute, dt.datetime.now().second)
        self.main[2] = " Cash: $%s Airports: %s Planes: %s" % (str(self.game.CASH), str(len(self.game.AIRPORTS)), str(len(self.game.PLANES)))
        self.main[3] = " Lv:%s [%s%s] next: %s" % (str(self.game.Leveler.level), currxp, nextxp, str(self.game.Leveler.xpfornext-self.game.Leveler.xp))
        self.main[5] =  "  %sA: View Airports"%OPTION_MENU_CODE
        self.main[6] =  "  %sP: View Planes"%OPTION_MENU_CODE
        self.main[7] =  "  %sM: Market"%OPTION_MENU_CODE
        self.main[8] =  "  %sC: Commands"%OPTION_MENU_CODE
        self.main[9] =  "  %sS: Stats"%OPTION_MENU_CODE
        self.main[10] = "  %sR: Restart Game"%OPTION_MENU_CODE
        self.main[11] = "  %sQ: Quit and Save"%OPTION_MENU_CODE
        self.main[15] = "  %sO: About"%OPTION_MENU_CODE

    def gotoCommands(self, game):
        self.reset()
        self.main[0] = "     -={Commands}=-"
        start = 1
        for i,cmd in enumerate(list(vars(game.Commands))):
            val = getattr(game.Commands, cmd)
            self.main[i+start] = f"[{OPTION_MENU_CODE}{val.name}]: {val.info.strip()}"

    def gotoStore(self):
        self.reset()
        self.main[0] = "     -={Store}=-"
        self.main[1] = ""
        self.main[2] = "  %sC: Construct New Airport"%OPTION_MENU_CODE
        self.main[3] = "  %sM: Plane Market"%OPTION_MENU_CODE
    
    def gotoConstructAirport(self, game):
        self.reset()
        keys = list(ALOOKUP.lookup.keys())
        keys.remove('None')
        if game.Commands.debugmode:
            print(keys)
        tmp = keys
        for k in keys:
            for a_obj in self.game.AIRPORTS:
                if game.Commands.debugmode:
                    print(k, a_obj.code)
                if a_obj.code == k:
                    tmp.remove(k)
        keys = tmp            
        if game.Commands.debugmode:
            print(keys)
        choice = rand.randint(0, len(keys))
        cost = self.game.store.airport_prices[len(self.game.AIRPORTS)]
        if self.game.CASH - cost > 0:
            self.game.CASH -= cost
        self.main[0] = "   -={Construct Airport}=-"
        self.main[1] = " Cash: $%s   Airports: %s" % (self.game.CASH, len(self.game.AIRPORTS))
        self.main[2] = ""
        if self.airport_unlock == 0 or self.airport_unlock == -1:
            self.main[3] =      " New Contract:"
            self.main[4] =      "    Current Cost - $%s" % (cost)
            self.main[5] =      "    %sA to Accept"%OPTION_MENU_CODE
            if self.airport_unlock == -1:
                self.game.MsgQueue.put(Message("Not enough cash!", MessageType.ALERT))
        elif self.airport_unlock == 1:
            self.main[3] = " New Contract: ACCEPTED"
            self.main[4] = "    Unlocked location: %s" % (ALOOKUP.lookup[keys[choice]][0])
            self.main[5] = "    Code: %s" % (keys[choice])
            self.main[6] = "    Paid: %s" % (cost)
            self.game.AIRPORTS.append(Airport(keys[choice]))
            self.game.StatTracker.AirportRevenue[keys[choice]] = 0
            self.airport_unlock = False
    
    def gotoStatTracker(self):
        self.reset()
        self.main[0] = "     -={Stats}=-"
        self.main[1] = " Total Flights: %s     (%s?): Show info" % (self.game.StatTracker.TotalFlights, OPTION_MENU_CODE)
        self.main[2] = " Total Revenue: $%s"%self.game.StatTracker.TotalRevenue
        if self.StatViewPlaneView:
            print(self.game.StatTracker.PlaneTrips.items())
            self.main[3] = " Planes Acquired: (%sT for Airports)"%OPTION_MENU_CODE
            for i, item in enumerate(self.game.StatTracker.PlaneTrips.items()):
                print(i, item)
                self.main[i+4] = "   [%s]: Rank %s T:%s P:%s CpM:%s" % (item[0], item[1]["Rank"], item[1]["Trips"], item[1]["Passengers"], item[1]["CpM"])
        else:
            self.main[3] = " Airports Acquired: (%sT for Planes)"%OPTION_MENU_CODE
            for i, item in enumerate(self.game.StatTracker.AirportRevenue.items()):
                self.main[i+4] = "   [%s]: $%s"%(item[0], item[1])

    def gotoMarket(self):
        self.reset()
        self.main[0] = "     -={Plane Market}=-"
        self.main[1] = " Cash: $%s    (Refresh (%sR): $%s)" % (self.game.CASH, OPTION_MENU_CODE, REFRESH_PLANE_MARKET_PRICE)
        self.main[2] = " Planes: %s   (Purchase (%sP): ex. p1JFK)" % (len(self.game.PLANES), OPTION_MENU_CODE)
        self.main[3] = ""
        for p in range(len(self.game.store.planes_available)):
            p_obj = self.game.store.planes_available[p]
            if not p_obj.purchased:
                self.main[p*4+4] = f" ({p+1}) Plane[{p_obj.id}]: Class [{p_obj.rank}] - ${p_obj.price}"
                self.main[p*4+5] = "       Speed: %s" % p_obj.speed
                self.main[p*4+6] = "       Capacity: %s" % p_obj.capacity
                self.main[p*4+7] = "       Fuel: %s" % p_obj.fuel
            else:
                self.main[p*4+4] = f" ({p+1}) Plane[{p_obj.id}]: Class [{p_obj.rank}] - BOUGHT"
                self.main[p*4+5] = "       Speed: %s" % p_obj.speed
                self.main[p*4+6] = "       Capacity: %s" % p_obj.capacity
                self.main[p*4+7] = "       Fuel: %s" % p_obj.fuel

    def gotoAirports(self):
        self.reset()
        a_obj = self.game.AIRPORTS[self.game.a_view]
        self.main[0] = "     -={Airports}=-"
        self.main[1] = "   <- Z: Scroll :X ->"
        self.main[2] = "Location %s out of %s:" % ((self.game.a_view+1), len(self.game.AIRPORTS))
        self.main[3] = " Name: %s" % a_obj.name
        self.main[4] = " Code: %s" % a_obj.code
        self.main[5] = " Planes Parked: [%s]" % a_obj.viewParkedPlanes(self.game)
        self.main[6] = "Choose Psgr to %sLoad (ex. 'LaA'):"%OPTION_MENU_CODE
        for i,p in enumerate(a_obj.passengers):
            self.main[7+i] = f"({OPTION_MENU_CODE}{chr(i+97)}) Psgr [{p.id}] - Dest: {p.dest}  Pay: ${p.pay}"
    
    def gotoPlanes(self):
        self.reset()
        p_obj = self.game.PLANES[self.game.p_view]
        self.main[0] = "     -={Planes}=-"
        self.main[1] = "   <- Z: Scroll :X ->"
        self.main[2] = " Aircraft %s out of %s:" % ((self.game.p_view+1), len(self.game.PLANES))
        self.main[3] = f"  Plane: {p_obj.serial} [{p_obj.id}]  Speed: {p_obj.speed}"
        self.main[4] = "  Located: %s" % p_obj.source
        if p_obj.dest == "none":
            self.main[5] = "  Destination: NONE"
        elif p_obj.status == PlaneState.fly:
            self.main[5] = "  Dest: %s" % ALOOKUP.lookup[p_obj.dest][0]
        else:
            self.main[5] = "  Dest: %s (%sC to Cancel)" % (ALOOKUP.lookup[p_obj.dest][0],OPTION_MENU_CODE)
        if p_obj.status == PlaneState.fly:
            self.main[6] = "  Status: IN FLIGHT - %s(%s) mins" % (round(p_obj.curr_flight_time,1), round(p_obj.time_left,1))
        elif p_obj.status == PlaneState.need_dest:
            self.main[6] = "  Status: Parked (Set %sDest ex. DJFK)"%OPTION_MENU_CODE
        elif p_obj.status == PlaneState.ready:
            self.main[6] = "  Status: Parked (%sF to start flight)"%OPTION_MENU_CODE
        self.main[7] = "  Capacity: [%s/%s]" % (len(p_obj.passengers), p_obj.capacity)
        if p_obj.status == PlaneState.need_dest:
            self.main[8] = "  Fuel: %s"%p_obj.fuel 
        else:
            self.main[8] = "  Fuel Cost: $%s" % p_obj.trip_fuelcost
        self.main[9] = "Passenger List (%sRemove ex. 'Ra'):"%OPTION_MENU_CODE
        for i,p in enumerate(p_obj.passengers):
            self.main[10+i] = f"({OPTION_MENU_CODE}{chr(i+97)}) Psgr [{p.id}] - Dest: {p.dest}  Pay: ${p.pay}"

class Screen:
    def __init__(self, g):
        self.game = g
        self.W = CONSOLE_C
        self.H = CONSOLE_R-1
        self.main = []

        self.menu = Menu(g)
        self.map = Map()
        self.title = Title()

        self.PAL = Pallette()

        self.reset()
    
    def reset(self):
        self.main = []
        for r in range(self.H):
            row = []
            for c in range(self.W):
                if r == 0 or r == self.H-1:
                    row.append(self.PAL.bordercolor+"-"+Color.END)
                elif c == 0 or c == self.W-1:
                    row.append(self.PAL.bordercolor+"|"+Color.END)
                else:
                    row.append(" ")
            self.main.append(row)
    
    def print(self):
        bgcolor = Color.BG_BLACK
        fgcolor = self.PAL.menucolor
        self.reset()
        # add title
        for i, line in enumerate(self.title.main):
            for ch in range(len(line)):
                self.main[i+self.title.offr][ch+self.title.offc] = self.PAL.titlecolor + line[ch] + Color.END
        # add menu
        for index, line in enumerate(self.menu.main):
            menu_decrement = 0
            for ch in range(len(line)):
                if line[ch] == OPTION_MENU_CODE:
                    fgcolor = self.PAL.optioncolor
                    menu_decrement += 1
                else:                    
                    self.main[index+self.menu.offr][ch+self.menu.offc-menu_decrement] = fgcolor + line[ch] + Color.END
                    fgcolor = self.PAL.menucolor
        # add map
        for index, line in enumerate(self.map.main):
            for ch in range(len(line)):
                self.main[index+self.map.offr][ch+self.map.offc] = self.PAL.mapcolor + line[ch] + Color.END
        # add highlight
        if self.game.PAGE == Page.airports:
            for r in range(-1,2,1):
                for c in range(-1,2,1):
                    self.main[self.map.offr+r+self.game.AIRPORTS[self.game.a_view].coords[1]][self.map.offc+c+self.game.AIRPORTS[self.game.a_view].coords[0]] = self.PAL.highlightcolor+"*"+Color.END
        # # add weather
        if self.game.PAGE == Page.default:
            for cloud in self.game.clouds:
                for r,row in enumerate(cloud.area):
                    for c,col in enumerate(row):
                        px = self.map.rowToMap(cloud.pos[0]+r) + self.map.offr
                        py = self.map.colToMap(cloud.pos[1]+c) + self.map.offc
                        if col == 1:
                            self.main[px][py] = self.PAL.cloudcolor+cloud.icon+Color.END
                        elif self.game.Commands.weather.action:
                            self.main[px][py] = self.PAL.cloudcolor+'.'+Color.END
                if self.game.Commands.weather.action:
                    for r in range(len(cloud.info)):
                        for c in range(len(cloud.info[0])):
                            if cloud.info[r][c]:
                                self.main[self.map.rowToMap(cloud.pos[0]+r)+self.map.offr][self.map.colToMap(cloud.pos[1]+c)+self.map.offc] = self.PAL.cloudinfo+cloud.info[r][c]+Color.END
        # add airports
        for a in self.game.AIRPORTS:
            self.main[self.map.offr+a.coords[1]][self.map.offc+a.coords[0]] = self.PAL.airportcolor+"+"+Color.END
        # add plane path
        if self.game.PAGE == Page.planes or self.game.Commands.fpaths.action:
            p_obj = self.game.PLANES[self.game.p_view]
            if p_obj.path:
                for p in range(len(p_obj.path)):
                    self.main[self.map.offr+p_obj.path[p][0][1]][self.map.offc+p_obj.path[p][0][0]] = self.PAL.pathcolor+p_obj.path[p][1]+Color.END
        # add planes
        for p in self.game.PLANES:
            if p.status == PlaneState.fly:
                if p.rank == "A":
                    addcolor = self.PAL.planecolor_a
                elif p.rank == "B":
                    addcolor = self.PAL.planecolor_b
                else:
                    addcolor = self.PAL.planecolor_c
                self.main[round(self.map.offr+p.coords[1])][round(self.map.offc+p.coords[0])] = addcolor+p.icon+Color.END
        # print result cmd
        menu_decrement = 0
        addcolor = self.PAL.menucolor
        for i,c in enumerate(self.game.Msg):
            if c == ALERT_CODE:
                addcolor = self.PAL.alertcolor
                menu_decrement += 1
            elif c == END_CODE:
                addcolor = self.PAL.menucolor
                menu_decrement += 1
            else:
                self.main[self.H-2][i+1-menu_decrement] = addcolor+c
        # print main
        for r in range(self.H):
            for c in range(self.W):
                print(self.main[r][c], end="")

