import enum

class MsgType(enum.Enum):
    ERROR = 0
    WARNING = 1
    INFO = 2
    SUCCESS = 3
    DEBUG = 4

class Message:
    def __init__(self, msgtype, msg):
        self.msgtype = msgtype
        self.msg = msg

class Messager:
    queue = []

    @staticmethod
    def add_message(msgtype, msg):
        Messager.queue.append(Message(msgtype, msg))

    @staticmethod
    def get_message():
        if Messager.queue:
            return Messager.queue.pop(0)
        else:
            return None
