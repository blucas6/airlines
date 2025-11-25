import datetime

import logger

class Window:
    def __init__(self, game, origin, rows, cols):
        self.game = game
        self.origin = origin
        self.rows = rows
        self.cols = cols
        self.text = [[' ' for _ in range(cols)] for _ in range(rows)]

    def update(self):
        '''Clears the text array before it gets generated'''
        self.text = [[' ' for _ in range(self.cols)]
                     for _ in range(self.rows)]

    def add_border(self):
        for col in range(self.cols):
            self.text[0][col] = '-'
            self.text[-1][col] = '-'
        for row in range(self.rows):
            self.text[row][0] = '|'
            self.text[row][-1] = '|'

    def add_string(self, row, string):
        for ix,ch in enumerate(string):
            self.text[row][ix] = ch

class Map(Window):
    def __init__(self, game):
        with open('world.txt', 'r') as f:
            lines = f.readlines()
            rcount = 0
            for line in lines:
                if line[0] == '#':
                    continue
                self.text[rcount] = line.replace('\n', '')
                    
        super().__init__(game, origin=[0,40], rows=0, cols=0)

class MainMenu(Window):
    def __init__(self, game):
        super().__init__(game, origin=[9,2], rows=20, cols=40)
        self.state = 'main'
        self.levelbar = 10

    def update(self):
        super().update()
        if self.state == 'main':
            self.menu_main()

    def menu_main(self):
        mytime = datetime.datetime.now().strftime('%H:%M:%S')
        cash = self.game.Cash
        airport_n = len(self.game.Airports)
        plane_n = len(self.game.Planes)
        leveler = self.game.Leveler
        level = leveler.level
        currxp = round(leveler.xp / leveler.xpfornext * self.levelbar) *'#'
        leftxp = round(self.levelbar - len(currxp)) * ' '
        nextxp = leveler.xpfornext - leveler.xp 

        self.add_string(0, '     -={Main Menu}=- ')
        self.add_string(1, ' [Universal Time: %s]' % (mytime))
        self.add_string(2, ' Cash: $%s Airports: %s Planes: %s' %
                        (cash, airport_n, plane_n))
        self.add_string(3, ' Lv:%s [%s%s] next: %s' % 
                        (level, currxp, leftxp, nextxp))
        self.add_string(5,  ' A: View Airports')
        self.add_string(6,  ' P: View Planes')
        self.add_string(7,  ' M: Market')
        self.add_string(8,  ' C: Commands')
        self.add_string(9,  ' S: Stats')
        self.add_string(10, ' R: Restart Game')
        self.add_string(11, ' Q: Quit and Save')
        self.add_string(12, ' O: About')

class Title(Window):
    def __init__(self, game):
        super().__init__(game, origin=[0,2], rows=9, cols=40)

    def update(self):
        super().update()
        self.add_string(0, r"  __    __   ____                ")
        self.add_string(1, r" / _\  (  ) (  _ \               ")
        self.add_string(2, r"/    \  )(   )   /               ")
        self.add_string(3, r"\_/\_/ (__) (__\_)               ")
        self.add_string(4, r" __     __   __ _   ____   ____  ")
        self.add_string(5, r"(  )   (  ) (  ( \ (  __) / ___) ")
        self.add_string(6, r"/ (_/\  )(  /    /  ) _)  \___ \ ")
        self.add_string(7, r"\____/ (__) \_)__) (____) (____/ ")
        self.add_string(8, r"---------------------------------")

class MenuManager:
    def __init__(self, game):
        self.stack = [Title(game), MainMenu(game)]
        self.showborder = False

    def update(self):
        for window in self.stack:
            window.update()
            if self.showborder:
                window.add_border()


