import curses

import engine
import color
import logger

class Display:
    '''Utility class to display screens with an engine class'''
    def __init__(self):
        self.screenbuffer: list[list[str]] = list
        '''2D buffer the size of the terminal for outputting to engine'''
        self.colorbuffer: list[list[str]] = list
        '''2D buffer the size of the terminal for outputting to engine'''
        self.unknownglyph = ' '
        '''Glyph to show unexplored area'''
        self.unknowncolor = None
        '''Color of unknown area'''

    def read_input(self):
        return self.Engine.read_input()

    def init(self, stdscr: curses.window):
        '''Setup the buffers'''
        # initialize engine
        self.Engine = engine.Engine(debug=True)
        self.Engine.init(stdscr)
        self.clear_buffers()
        # colors must be accessed after engine has been initialized
        self.unknowncolor = color.Color().magenta

    def clear_buffers(self):
        '''Creates empty buffers'''
        termrows = self.Engine.termrows
        termcols = self.Engine.termcols
        self.screenbuffer = [[' ' for _ in range(termcols-1)] 
                                    for _ in range(termrows-1)]
        self.colorbuffer = [
                [color.Color().white for _ in range(termcols-1)] 
                                    for _ in range(termrows-1)]

    def print(self, menumanager):
        self.clear_buffers()
        for window in menumanager.stack:
            for r,row in enumerate(window.text):
                for c,col in enumerate(row):
                    dr = r + window.origin[0]
                    dc = c + window.origin[1]
                    if not self.bounds_check(self.screenbuffer, dr, dc):
                        continue
                    self.screenbuffer[dr][dc] = col
                    if not self.bounds_check(self.colorbuffer, dr, dc):
                        continue
                    self.colorbuffer[dr][dc] = window.color[r][c]
                    #self.colorbuffer[dr][dc] = color.Color().white
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

