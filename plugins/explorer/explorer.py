from libs import plugin, dataloader, embed, savetome
import discord, random

DATAPATH='datafilepath'

class Plugin(plugin.Multi, plugin.OnMessagePlugin):
    # movement words
    UP = ["w", "up", "north"]
    DOWN = ["s", "down", "south"]
    LEFT = ["a", "left", "west"] # better than right
    RIGHT = ["d", "right", "east"]

    # constants, for loading & saving data
    ROOMS = 'rooms'
    TYPE = 'type'
    PLAYERDATA = 'playerdata'
    LOCATION = 'location'

    # recognized types
    UPLOC = 'up'
    DOWNLOC = 'down'
    LEFTLOC = 'left'
    RIGHTLOC = 'right'

    MOVE_ENDING = "\n \n Which portal do you want to go through?"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fuck_off=False
        self.load_data(self.config[DATAPATH])

    async def action(self, message):
        if not self.fuck_off:
            self.fuck_off=True
            did_something = False
            message_lower = message.content.lower()
            if message_lower in self.UP:
                if message.author.id in self.playerdata:
                    self.move(message.author.id, type=self.UPLOC)
                    # await self.send_message(message.channel, 'You move UP')
                else:
                    self.new_game(message.author.id, type=self.UPLOC)
                    # await self.send_message(message.channel, 'new game')
                did_something = True
            elif message_lower in self.DOWN:
                if message.author.id in self.playerdata:
                    self.move(message.author.id, type=self.DOWNLOC)
                    # await self.send_message(message.channel, 'You move DOWN')
                else:
                    self.new_game(message.author.id, type=self.DOWNLOC)
                    # await self.send_message(message.channel, 'new game')
                did_something = True
            elif message_lower in self.LEFT:
                if message.author.id in self.playerdata:
                    self.move(message.author.id, type=self.LEFTLOC)
                    # await self.send_message(message.channel, 'You move LEFT')
                else:
                    self.new_game(message.author.id, type=self.LEFTLOC)
                    # await self.send_message(message.channel, 'new game')
                did_something = True
            elif message_lower in self.RIGHT:
                if message.author.id in self.playerdata:
                    self.move(message.author.id, type=self.RIGHTLOC)
                    # await self.send_message(message.channel, 'You move RIGHT')
                else:
                    self.new_game(message.author.id, type=self.RIGHTLOC)
                    # await self.send_message(message.channel, 'new game')
                did_something = True
            if did_something:
                await self.send_message(message.channel, self.playerdata[message.author.id][self.LOCATION].description+self.MOVE_ENDING)
                self.save_data()
            self.fuck_off=False

    def shutdown(self):
        self.save_data()

    def new_game(self, player_id, type=None):
        self.playerdata[player_id] = dict()
        if type == None:
            type = random.choice(list(self.locations))
        self.playerdata[player_id][self.LOCATION] = self.locations[type][random.choice(list(self.locations[type]))]

    def move(self, player_id, type=None):
        if type == None:
            type = random.choice(list(self.locations))
        self.playerdata[player_id][self.LOCATION] = self.locations[type][random.choice(list(self.locations[type]))]

    def load_data(self, filename):
        self.datafile = dataloader.datafile(filename)

        # load locations
        self.locations=dict()
        for type in self.datafile.content[self.LOCATION]:
            self.locations[type]=dict()
            for location in self.datafile.content[self.LOCATION][type]:
                self.locations[type][location]=Location(**self.datafile.content[self.LOCATION][type][location])

        # load playerdata
        self.playerdata = dict()
        for player_id in self.datafile.content[self.PLAYERDATA]:
            self.playerdata[player_id] = dict()
            self.playerdata[player_id][self.LOCATION] = Location(**self.datafile.content[self.PLAYERDATA][player_id][self.LOCATION])


    def save_data(self):
        # save locations
        for type in self.locations:
            for location in self.locations[type]:
                self.datafile.content[self.LOCATION][type][location] = self.locations[type][location].__dict__

        # save playerdata
        for player_id in self.playerdata:
            self.datafile.content[self.PLAYERDATA][player_id] = dict()
            self.datafile.content[self.PLAYERDATA][player_id][self.LOCATION] = self.playerdata[player_id][self.LOCATION].__dict__

        # save to file
        self.datafile.save()

class Location():
    def __init__(self, name=None, description=None):
        '''(Location, str, str) -> Location'''

        if description==None:
            self.description = "You enter into a room with the default description"
        else:
            self.description=description
        if name == None:
            self.name = plugin.DEFAULT
        self.name = name
