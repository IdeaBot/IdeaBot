from libs import plugin, command

class Command(command.Dummy):
    '''Dummy command, please ignore'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.public_namespace.newRedditThread = plugin.Queue()
        self.public_namespace.newYTChannel = plugin.Queue()
        self.public_namespace.newTwitterChannel = plugin.Queue()
        self.public_namespace.newProBoardsForum = plugin.Queue()
        self.public_namespace.newGCal = plugin.Queue()
