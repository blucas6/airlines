import curses

import game 

if __name__ == '__main__':
    game = game.Game()
    curses.wrapper(game.start)

