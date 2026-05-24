import time

import display
import menustate
import entities
import leveler
import logger
import enums

class User:
    def __init__(self):
        self.Planes = []
        self.Airports = []
        self.Leveler = leveler.Leveler()
        self.Cash = 0

    def start(self):
        self.add_airport(entities.Airport('JFK'))
        self.add_airport(entities.Airport('LAX'))
        p = entities.Plane(1, 1, 3, 500, "LAX", "C", True)
        p.assignSerial()
        self.Planes.append(p)
        self.land_plane(p, notrack=True)

    def add_airport(self, airport):
        self.Airports.append(airport)

    def land_plane(self, p, notrack=False):
        for a in self.Airports:
            if a.code == p.source:
                a.landed(p)
                if not notrack:
                    leveler.StatTracker.add_flight(1)

class Game:
    def __init__(self):
        self.playing = True
        self.currenttime = time.time()
        self.Display = display.Display()
        self.MenuManager = menustate.MenuManager()
        self.User = User()
        self.airport_view = 0
        self.plane_view = 0

    def start(self, stdscr):
        logger.Logger.init()
        self.Display.init(stdscr)
        self.MenuManager.init(self)
        self.User.start()
        self.main()

    def main(self):
        self.page_refresh()
        while self.playing:
            self.update_time(time.time())
            self.process_events()
            self.page_refresh()
            self.Display.print(self.MenuManager)

    def process_events(self):
        '''
        Gets an event (continuously polling)
        '''
        event = self.Display.read_input()
        if event == 'Q':
            self.playing = False
        elif event == '#':
            self.MenuManager.showborder = not self.MenuManager.showborder
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
        elif self.MenuManager.state == enums.MenuState.PLANE:
            if event == 'b':
                self.MenuManager.state = enums.MenuState.MAIN
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

    def update_time(self, new_time):
        sec_diff = new_time - self.currenttime
        for p in self.User.Planes:
            p.update(sec_diff, self)
        self.currenttime = time.time()
    
    def page_refresh(self):
        self.MenuManager.update()

