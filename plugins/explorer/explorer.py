from libs import plugin, dataloader, embed, savetome
import discord, random

DATAPATH='datafilepath'
PATHDATAPATH = 'playerdatapath'

class Plugin(plugin.OnMessagePlugin):
    '''A simple demo application of the potential of plugins.

This is like an old text-based adventure, where you move from room to room by
choosing the direction to move (or in this case, the direction of the portal
to enter). Hopefully, in the future, this game will actually be interesting.

To enable explorer in a channel, do:
```@Idea explore this channel``` '''
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
    INVENTORY = 'inventory'

    # recognized types
    UPLOC = 'up'
    DOWNLOC = 'down'
    LEFTLOC = 'left'
    RIGHTLOC = 'right'

    MOVE_ENDING = "\n \n Which portal do you want to go through?"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fuck_off=False
        self.load_data(self.config[DATAPATH], self.config[PATHDATAPATH])

    async def action(self, message):
        if not self.fuck_off:
            if message.channel.id in self.public_namespace.exploring_channels:
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
        self.playerdata[player_id][self.INVENTORY] = Inventory(user=player_id)

    def move(self, player_id, type=None):
        if type == None:
            type = random.choice(list(self.locations))
        self.playerdata[player_id][self.LOCATION] = self.locations[type][random.choice(list(self.locations[type]))]

    def load_data(self, datafilepath, playerdatafilepath):
        # load locations
        self.datafile = dataloader.datafile(datafilepath)
        self.locations=dict()
        for type in self.datafile.content:
            self.locations[type]=dict()
            for location in self.datafile.content[type]:
                self.locations[type][location]=Location(**self.datafile.content[type][location])

        # load playerdata
        self.playerdatafile = dataloader.loadfile_safe(playerdatafilepath)
        if not isinstance(self.playerdatafile.content, dict):
            self.playerdatafile.content = dict()
        self.playerdata = dict()
        for player_id in self.playerdatafile.content:
            self.playerdata[player_id] = dict()
            if self.LOCATION in self.playerdatafile.content[player_id]:
                self.playerdata[player_id][self.LOCATION] = Location(**self.playerdatafile.content[player_id][self.LOCATION])
            else:
                self.playerdata[player_id][self.LOCATION] = Location()

            if self.INVENTORY in self.playerdatafile.content[player_id]:
                self.playerdata[player_id][self.INVENTORY] = Inventory(**self.playerdatafile.content[player_id][self.INVENTORY])
            else:
                self.playerdata[player_id][self.INVENTORY] = Inventory(player_id)


    def save_data(self):
        # save locations
        for type in self.locations:
            for location in self.locations[type]:
                self.datafile.content[type][location] = self.locations[type][location].__dict__

        # save playerdata
        for player_id in self.playerdata:
            self.playerdatafile.content[player_id] = dict()
            self.playerdatafile.content[player_id][self.LOCATION] = self.playerdata[player_id][self.LOCATION].__dict__
            self.playerdatafile.content[player_id][self.INVENTORY] = self.playerdata[player_id][self.INVENTORY].__dict__

        # save to file
        self.datafile.save()
        self.playerdatafile.save()

class Location():
    def __init__(self, name=None, description=None, item=None):
        '''(Location, str, str) -> Location'''

        if description==None:
            self.description = "You enter into a room with the default description"
        else:
            self.description=description

        if name == None:
            self.name = plugin.DEFAULT
        else:
            self.name = name

        if item == None or item == "":
            self.item=None
        else:
            self.item=item

class Inventory():
    def __init__(self, items=list(), user=None):
        '''(Inventory, list, str) -> Inventory '''

        if user!=None:
            self.items=list(items)
            self.user = user
        else:
            user = '0'*18
            self.items=list()
