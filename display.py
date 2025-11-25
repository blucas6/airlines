import curses

import engine
import color
import logger

class Display:
    '''Utility class to display screens with an engine class'''
    def __init__(self):
        self.termrows = 0
        '''Total terminal rows'''
        self.termcols = 0
        '''Total terminal columns'''
        self.screenbuffer: list[list[str]] = list
        '''2D buffer the size of the terminal for outputting to engine'''
        self.colorbuffer: list[list[str]] = list
        '''2D buffer the size of the terminal for outputting to engine'''
        self.unknownglyph = ' '
        '''Glyph to show unexplored area'''
        self.unknowncolor = None
        '''Color of unknown area'''
        self.stack = []

    def read_input(self):
        return self.Engine.read_input()

    def init(self, stack, stdscr: curses.window | None = None):
        '''Setup the buffers'''
        # initialize engine
        self.Engine = engine.Engine()
        self.Engine.init(stdscr)
        # create buffers
        self.termrows = self.Engine.termrows
        self.termcols = self.Engine.termcols
        self.clear_buffers()
        # colors must be accessed after engine has been initialized
        self.unknowncolor = color.Color().white
        self.stack = stack

    def clear_buffers(self):
        '''Creates empty buffers'''
        self.screenbuffer = [[' ' for _ in range(self.termcols-1)] 
                                    for _ in range(self.termrows-1)]
        self.colorbuffer = [
                [color.Color().white for _ in range(self.termcols-1)] 
                                    for _ in range(self.termrows-1)]

    def print(self):
        for window in self.stack:
            for r,row in enumerate(window.text):
                for c,col in enumerate(row):
                    dr = r + window.origin[0]
                    dc = c + window.origin[1]
                    if not self.bounds_check(self.screenbuffer, dr, dc):
                        continue
                    self.screenbuffer[dr][dc] = col
                    if not self.bounds_check(self.colorbuffer, dr, dc):
                        continue
                    self.colorbuffer[dr][dc] = color.Color().white
        if self.Engine.frame_ready():
            self.Engine.output(screenchars=self.screenbuffer,
                               screencolors=self.colorbuffer)

    def bounds_check(self, buffer, r, c):
        '''
        Checks if a position is valid within the screen buffer
        '''
        if (r > len(buffer)-1 or c > len(buffer[r])-1):
            return False
        return True

