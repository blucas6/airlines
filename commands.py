
class Command:
    def __init__(self, name, info, start):
        self.name = name
        self.info = info
        self.action = start

    def toggle(self):
        if self.action:
            self.action = False
        else:
            self.action = True

class Commands:
    def __init__(self):
        self.debugmode = Command('/debug', 'Toggle debug mode', False)
        self.fpaths = Command('/fpaths', 'Toggle show flight paths', False)
        self.weather = Command('/weather', 'Toggle cloud information', False)

    def runCmd(self, cmd):
        if cmd == '/debug':
            self.debugmode.toggle()
        elif cmd == '/fpaths':
            self.fpaths.toggle()
        elif cmd == '/weather':
            self.weather.toggle()

class MessageType:
    DEFAULT = ""
    IMPORTANT = "-"
    ALERT = "**"

class Message:
    def __init__(self, msg='', t=MessageType.DEFAULT):
        self.msg = msg
        self.type = t