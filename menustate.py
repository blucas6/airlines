import datetime
import enum

import logger
import color
import enums
import config
import messager

class Window:
    def __init__(self, game, origin, rows, cols):
        self.Game = game
        self.origin = origin
        self.rows = rows
        self.cols = cols
        self.text = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.color = [[color.Color().white for _ in range(cols)] for _ in range(rows)]

    def update(self, *_):
        '''Clears the text array before it gets generated'''
        self.text = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.color = [[color.Color().white for _ in range(self.cols)] for _ in range(self.rows)]

    def add_border(self):
        for col in range(self.cols):
            self.text[0][col] = '-'
            self.text[-1][col] = '-'
        for row in range(self.rows):
            self.text[row][0] = '|'
            self.text[row][-1] = '|'

    def add_string(self, row, string, buffer=[]):
        if not buffer:
            buffer = self.text
        for ix,ch in enumerate(string):
            if row < len(buffer) and ix < len(buffer[row]):
                buffer[row][ix] = ch

class Map(Window):
    def __init__(self, game):
        rows = 30
        cols = 80
        self.map = [[' ' for _ in range(cols)] for _ in range(rows)]
        super().__init__(game, origin=[1,config.MAP_SIDELINE+1], rows=rows, cols=cols)
        with open('world.txt', 'r') as f:
            lines = f.readlines()
            rcount = 0
            for line in lines:
                if line[0] == '#':
                    continue
                self.add_string(rcount, line.replace('\n', ''), buffer=self.map)
                rcount += 1

    def update(self, state, *_):
        super().update()
        self.text = [row[:] for row in self.map]

        user = self.Game.User
        aview = self.Game.airport_view
        pview = self.Game.plane_view
        airport = user.Airports[aview]
        plane = user.Planes[pview]

        # add airports
        for a in user.Airports:
            pos = a.coords
            if (pos[0] >= 0 and pos[0] < len(self.text) and
                pos[1] >= 0 and pos[1] < len(self.text[0])):
                self.text[pos[0]][pos[1]] = '+'
                self.color[pos[0]][pos[1]] = color.Color().yellow
        # add highlight
        if state == enums.MenuState.AIRPORT:
            pt = airport.coords
            self.color[pt[0]][pt[1]] = color.Color().bg_grey_fg_yellow
            '''
            for r in range(-1,2,1):
                for c in range(-1,2,1):
                    self.text[r+a_obj.coords[0]][c+a_obj.coords[1]] = '*'
                    self.color[r+a_obj.coords[0]][c+a_obj.coords[1]] = color.Color().bright_yellow
                    '''
        # add flight paths
        if plane.path:
            for path in plane.path:
                pt = path[0]
                glyph = path[1]
                self.text[pt[0]][pt[1]] = glyph
                self.color[pt[0]][pt[1]] = color.Color().grey
        # add planes
        for p in user.Planes:
            if p.status == enums.PlaneState.fly:
                if p.rank == 'A':
                    pcolor = color.Color().red
                elif p.rank == 'B':
                    pcolor = color.Color().green
                elif p.rank == 'C':
                    pcolor = color.Color().blue
                self.color[p.coords[0]][p.coords[1]] = pcolor
                self.text[p.coords[0]][p.coords[1]] = p.icon

class CommandMenu(Window):
    def __init__(self, game):
        origin = [game.Display.Engine.termrows-2,1]
        super().__init__(game, origin=origin, rows=1, cols=config.MAP_SIDELINE)
        self.cmd = ''
        self.Game = game

    def update(self, state, command, commandmode, *_):
        super().update()
        self.origin = [self.Game.Display.Engine.termrows-2,1]
        cmd = ''
        if commandmode:
            cmd = command
            for ix in range(self.cols):
                self.color[0][ix] = color.Color().bg_white_fg_black
        else:
            for ix in range(self.cols):
                self.color[0][ix] = color.Color().white
        self.add_string(0, f' Command: {cmd}')

class MessageMenu(Window):
    def __init__(self, game):
        cols = game.Display.Engine.termcols-1
        super().__init__(game, origin=[0,1], rows=1, cols=cols)
        self.current_msg = None
        self.current_color = color.Color().white

    def update(self, state, command, commandmode, player_ack):
        super().update()
        self.cols = self.Game.Display.Engine.termcols-1
        if player_ack:
            self.current_msg = None
        if self.current_msg == None:
            newmsg = messager.Messager.get_message()
            if newmsg:
                self.current_msg = newmsg
                if self.current_msg.msgtype == messager.MsgType.ERROR:
                    self.current_color = color.Color().red
                elif self.current_msg.msgtype == messager.MsgType.WARNING:
                    self.current_color = color.Color().yellow
                elif self.current_msg.msgtype == messager.MsgType.INFO:
                    self.current_color = color.Color().white
                elif self.current_msg.msgtype == messager.MsgType.DEBUG:
                    self.current_color = color.Color().blue
                elif self.current_msg.msgtype == messager.MsgType.SUCCESS:
                    self.current_color = color.Color().green
        if self.current_msg != None:
            if len(messager.Messager.queue) > 0:
                more = ' -- more --'
            else:
                more = ''
            self.add_string(0, self.current_msg.msg + more)
            self.color[0] = [self.current_color for _ in range(self.cols)]

class MainMenu(Window):
    def __init__(self, game):
        super().__init__(game, origin=[10,1], rows=20, cols=config.MAP_SIDELINE)
        self.levelbar = 10

    def update(self, state, *_):
        super().update()
        if state == enums.MenuState.MAIN:
            self.menu_main()
        elif state == enums.MenuState.AIRPORT:
            self.menu_airport()
        elif state == enums.MenuState.PLANE:
            self.menu_plane()

    def menu_main(self):
        leveler = self.Game.User.Leveler
        user = self.Game.User
        mytime = datetime.datetime.now().strftime('%H:%M:%S')
        cash = user.Cash
        airport_n = len(user.Airports)
        plane_n = len(user.Planes)
        level = leveler.level
        currxp = round(leveler.xp / leveler.xpfornext * self.levelbar) *'#'
        leftxp = round(self.levelbar - len(currxp)) * ' '
        nextxp = leveler.xpfornext - leveler.xp 

        self.add_string(0,  '    -={Main Menu}=- ')
        self.add_string(1,  '[Universal Time: %s]' % (mytime))
        self.add_string(2,  'Cash: $%s Airports: %s Planes: %s' %
                        (cash, airport_n, plane_n))
        self.add_string(3,  'Lv:%s [%s%s] next: %s' % 
                        (level, currxp, leftxp, nextxp))
        self.add_string(5,  'A: View Airports')
        self.add_string(6,  'P: View Planes')
        self.add_string(7,  'M: Market')
        self.add_string(8,  'C: Commands')
        self.add_string(9,  'S: Stats')
        self.add_string(10, 'R: Restart Game')
        self.add_string(11, 'Q: Quit and Save')
        self.add_string(12, 'O: About')

    def menu_airport(self):
        a_view = self.Game.airport_view
        user = self.Game.User
        airport = user.Airports[a_view]
        self.add_string(0, "     -={Airports}=-")
        self.add_string(1, "    <  : Scroll :  >")
        self.add_string(2, "Location %s out of %s:" % (a_view+1, len(user.Airports)))
        self.add_string(3, " Name: %s" % airport.name)
        self.add_string(4, " Code: %s" % airport.code)
        self.add_string(5, " Planes Parked: [%s]" % airport.view_parked_planes(self.Game))
        self.add_string(6, "Choose Psgr to Load (ex. 'LaA'):")
        for ix,p in enumerate(airport.passengers):
            self.add_string(7+ix, f"(%s) P[%s] Dest:%s - $%s" %
                    (chr(ix+97), str(p.id).zfill(4), p.dest.code, p.pay))

    def menu_plane(self):
        user = self.Game.User
        p_view = self.Game.plane_view
        plane = user.Planes[self.Game.plane_view]
        destination = "none"
        if plane.dest in enums.AirportLookup:
            destination = enums.AirportLookup[plane.dest][0]
        flighttime = round(plane.curr_flight_time,1)
        timeleft = round(plane.time_left)
        self.add_string(0, "     -={Planes}=-")
        self.add_string(1, "   <  : Scroll :  >")
        self.add_string(2, "Aircraft %s out of %s:" % (p_view+1, len(user.Planes)))
        self.add_string(3, " Plane: %s [%s]  Speed: %s" %
                        (plane.serial, plane.id, plane.speed))
        self.add_string(4, " Located: %s" % plane.source)
        if destination == "none":
            self.add_string(5, " Destination: NONE")
        elif plane.status == enums.PlaneState.fly:
            self.add_string(5, " Dest: %s" % destination)
        else:
            self.add_string(5, " Dest: %s (C to Cancel)" % destination)
        if plane.status == enums.PlaneState.fly:
            self.add_string(6, " Status: IN FLIGHT - %s(%s) mins" % (flighttime, timeleft))
        elif plane.status == enums.PlaneState.need_dest:
            self.add_string(6, " Status: Parked (Set dest ex. DJFK)")
        elif plane.status == enums.PlaneState.ready:
            self.add_string(6, " Status: Parked (F to start flight)")
        self.add_string(7, "  Capacity: [%s/%s]" % (len(plane.passengers), plane.capacity))
        if plane.status == enums.PlaneState.need_dest:
            self.add_string(8, " Fuel: %s" % plane.fuel )
        else:
            self.add_string(8, " Fuel Cost: $%s" % plane.trip_fuelcost)
        self.add_string(9, "Passenger List (Remove ex. 'Ra'):")
        for ix,p in enumerate(plane.passengers):
            self.add_string(10+ix, " (%s) P[%s] Dest:%s - $%s" %
                            (chr(ix+97), p.id, p.dest.code, p.pay))

class Title(Window):
    def __init__(self, game):
        super().__init__(game, origin=[1,1], rows=9, cols=config.MAP_SIDELINE)

    def update(self, *_):
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
    def __init__(self):
        self.stack = []
        self.showborder = False
        self.state = enums.MenuState.MAIN
        self.commandmode = False
        self.command = ''

    def init(self, game):
        self.stack = [Title(game), MainMenu(game), Map(game), CommandMenu(game), MessageMenu(game)]

    def update(self, player_ack=False):
        for window in self.stack:
            window.update(self.state, self.command, self.commandmode, player_ack)
            if self.showborder:
                window.add_border()


