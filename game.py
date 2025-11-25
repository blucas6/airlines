import time
import curses

import display
import menustate
import engine
import leveler

class Game:
    def __init__(self):
        self.playing = True
        self.currenttime = time.time()
        self.Display = display.Display()
        self.MenuManager = menustate.MenuManager(self)
        self.Planes = []
        self.Airports = []
        self.Leveler = leveler.Leveler()
        self.Cash = 0

    def start(self, stdscr: curses.window | None = None):
        self.Display.init(self.MenuManager.stack, stdscr)
        self.main()

    def main(self):
        self.page_refresh()
        while self.playing:
            self.update_time(time.time())
            self.process_events()
            self.page_refresh()
            self.Display.print()

    def process_events(self):
        '''
        Gets an event (continuously polling)
        '''
        event = self.Display.read_input()
        if event == 'q':
            self.playing = False
        elif event == 'p':
            self.MenuManager.showborder = not self.MenuManager.showborder

    def update_time(self, new_time):
        sec_diff = new_time - self.currenttime
        for p in self.Planes:
            p.update(sec_diff, self)
        self.currenttime = time.time()
    
    def page_refresh(self):
        self.MenuManager.update()
