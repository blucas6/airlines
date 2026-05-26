import time
import math
import curses

import config
import display
import menustate
import entities
import leveler
import logger
import enums
import messager
import utility

class User:
    def __init__(self):
        self.Planes = []
        self.Airports = []
        self.Leveler = leveler.Leveler()
        self.Cash = 100

    def start(self):
        messager.Messager.add_message(messager.MsgType.INFO, 'Welcome back!')
        self.add_airport(entities.Airport('JFK'))
        self.add_airport(entities.Airport('LAX'))
        p = entities.Plane(10, 1, 3, 500, 'JFK', 'C', True)
        p.assignSerial()
        self.Planes.append(p)
        self.land_plane(p, notrack=True)
        self.refresh_all_airports()

    def update_planes(self, secs):
        for p in self.Planes:
            p.update_plane(secs)

    def add_airport(self, airport):
        self.Airports.append(airport)

    def land_plane(self, p, notrack=False):
        for a in self.Airports:
            if a.code == p.source:
                a.landed(p)
                if not notrack:
                    leveler.StatTracker.add_flight(1)
    
    def refresh_all_airports(self):
        for a in self.Airports:
            a.refresh_passengers(self.Airports)

    def load_passenger_into_plane(self, airport, cmd):
        logger.Logger.log(f'Load Passenger: airport:{airport} cmd:{cmd}')
        psgindex = utility.upper_char_num(cmd[1])
        if psgindex >= len(airport.passengers) or psgindex < 0:
            messager.Messager.add_message(
                    messager.MsgType.ERROR,
                    f"Passenger '{cmd[1]}' is not at this airport!")
            return False
        passenger = airport.passengers[psgindex]
        planeindex = cmd[2].upper()
        if not planeindex in self.Planes:
            messager.Messager.add_message(
                    messager.MsgType.ERROR,
                    f"Plane '{cmd[2].upper()}' does not exist!")
            return False 
        plane = [p for p in self.Planes if p.serial == planeindex][0]
        if passenger.source != plane.source:
            messager.Messager.add_message(
                    messager.MsgType.ERROR,
                    f"Plane '{plane.serial}' is not at this airport!")
            return False
        if plane.is_full():
            messager.Messager.add_message(
                    messager.MsgType.ERROR,
                    f"Plane '{plane.serial}' is full!")
            return False
        plane.add_passenger(passenger)
        airport.remove_passenger(passenger, self.Airports)
        messager.Messager.add_message(
                messager.MsgType.SUCCESS,
                f"Loaded passenger '{passenger.id}' into plane '{plane.serial}'!")
        return True

    def off_load_passenger_to_airport(self, plane, cmd):
        logger.Logger.log(f'Remove Passenger: plane:{plane} cmd:{cmd}')
        psgindex = utility.upper_char_num(cmd[1])
        if psgindex >= 0 and psgindex < len(plane.passengers):
            passenger = plane.passengers[psgindex]
            if plane.status == entities.PlaneState.fly:
                messager.Messager.add_message(
                        messager.MsgType.ERROR,
                        'Cannot throw passenger out of plane for fun!')
                return False
            if passenger.source not in self.Airports:
                messager.Messager.add_message(
                        messager.MsgType.ERROR,
                        f"Could not find Airport '{passenger.source}' to offload passenger to!")
                return False
            for airport in self.Airports:
                if airport.code == passenger.source:
                    airport.add_passenger(passenger)
                    plane.remove_passenger(passenger)
                    messager.Messager.add_message(
                        messager.MsgType.SUCCESS,
                        f"Passenger '{passenger.id}' unloaded off Plane '{plane.serial}' " \
                        f"back to Airport '{airport.code}'")
                    return True
        return False
    
    def set_plane_destination(self, plane, cmd):
        logger.Logger.log(f'Set plane destination: plane:{plane} cmd:{cmd}')
        code = cmd[1:4]
        if code == plane.source:
            messager.Messager.add_message(
                    messager.MsgType.ERROR,
                    'Plane is parked here!')
            return False
        if code not in enums.AirportLookup:
            messager.Messager.add_message(
                    messager.MsgType.ERROR,
                    f"Unknown airport code '{code}' !")
            return False
        plane.dest = code
        plane.status = entities.PlaneState.ready
        pos1 = enums.AirportLookup[plane.source][1]
        pos2 = enums.AirportLookup[plane.dest][1]
        dist = math.dist(pos1, pos2)
        plane.trip_fuelcost = round(dist) * plane.fuel
        return True

    def start_flight(self, plane):
        if self.Cash - plane.trip_fuelcost < 0:
            messager.Messager.add_message(
                    messager.MsgType.ERROR,
                    f"Fuel cost too expensive!")
            return False
        self.Cash -= plane.trip_fuelcost
        plane.status = enums.PlaneState.fly
        plane.create_path()
        return True

class Game:
    def __init__(self):
        self.playing = True
        self.currenttime = time.time()
        self.Display = display.Display()
        self.MenuManager = menustate.MenuManager()
        self.User = User()
        self.airport_view = 0
        self.plane_view = 0
        self.seconds_diff = 0

    def start(self, stdscr):
        logger.Logger.init()
        self.Display.init(stdscr)
        self.MenuManager.init(self)
        self.User.start()
        #
        self.User.load_passenger_into_plane(self.User.Airports[0], 'LAA')
        self.User.set_plane_destination(self.User.Planes[0], 'DLAX')
        #
        self.main()

    def main(self):
        self.page_refresh(None)
        while self.playing:
            self.update_time()
            event = self.process_events()
            self.page_refresh(event)
            self.Display.print(self.MenuManager)

    def process_events(self):
        '''
        Gets an event (continuously polling)
        '''
        event = self.Display.read_input()
        if event == 'q':
            self.playing = False
        elif event == '1':
            self.MenuManager.showborder = not self.MenuManager.showborder
        elif event == '\n' or self.MenuManager.commandmode:
            if not self.MenuManager.commandmode and event == '\n':
                self.MenuManager.commandmode = True
            elif event == '\n':
                self.MenuManager.commandmode = False
                self.execute_command(self.MenuManager.command)
                self.MenuManager.command = ''
            elif event != None:
                if ord(event) == curses.KEY_BACKSPACE:
                    self.MenuManager.command = self.MenuManager.command[:-1]
                elif ord(event) == 27:
                    self.MenuManager.commandmode = False
                    self.MenuManager.command = ''
                else:
                    self.MenuManager.command += event
        elif self.MenuManager.state == enums.MenuState.MAIN:
            if event == 'a':
                self.MenuManager.state = enums.MenuState.AIRPORT
            elif event == 'p':
                self.MenuManager.state = enums.MenuState.PLANE
        elif self.MenuManager.state == enums.MenuState.AIRPORT:
            if event == 'b':
                self.MenuManager.state = enums.MenuState.MAIN
            elif event == '<':
                if self.airport_view - 1 >= 0:
                    self.airport_view -= 1
                else:
                    self.airport_view = len(self.User.Airports)-1
            elif event == '>':
                if self.airport_view + 1 < len(self.User.Airports):
                    self.airport_view += 1
                else:
                    self.airport_view = 0
            elif event == 'r':
                self.User.refresh_all_airports()
        elif self.MenuManager.state == enums.MenuState.PLANE:
            plane = self.User.Planes[self.plane_view]
            if event == 'b':
                self.MenuManager.state = enums.MenuState.MAIN
            elif event == 'f' and plane.status == enums.PlaneState.ready:
                self.User.start_flight(plane)
            elif event == '<':
                if self.plane_view- 1 >= 0:
                    self.plane_view -= 1
                else:
                    self.plane_view = len(self.User.Planes)-1
            elif event == '>':
                if self.plane_view + 1 < len(self.User.Planes):
                    self.plane_view += 1
                else:
                    self.plane_view = 0
        return event

    def update_time(self):
        self.seconds_diff += time.time() - self.currenttime
        if self.seconds_diff > config.GAME_TICK:
            self.User.update_planes(self.seconds_diff)
            self.seconds_diff = 0
        self.currenttime = time.time()
    
    def page_refresh(self, event):
        player_ack = False
        if event != None:
            player_ack = True
        self.MenuManager.update(player_ack)

    def execute_command(self, cmd):
        cmd = cmd.upper()
        if self.MenuManager.state == enums.MenuState.AIRPORT:
            airport = self.User.Airports[self.airport_view]
            if len(cmd) == 3 and cmd[0] == 'L':
                self.User.load_passenger_into_plane(airport, cmd)
        elif self.MenuManager.state == enums.MenuState.PLANE:
            plane = self.User.Planes[self.plane_view]
            if len(cmd) == 2 and cmd[0] == 'R':
                self.User.off_load_passenger_to_airport(plane, cmd)
            elif len(cmd) == 4 and cmd[0] == 'D':
                self.User.set_plane_destination(plane, cmd)




