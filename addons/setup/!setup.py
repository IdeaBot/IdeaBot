from libs import command, dataloader

COMMANDERS = 'commanders'
OWNER = "owner"
MAINTAINERS = "maintainers"
DEFAULT_OWNER_ID = "106537989684887552" #NGnius's discord ID ~~pls don't hack me~~
REACTIONS = 'reactions'
COMMANDS = 'commands'
PACKAGES = 'packages'
PLUGINS = 'plugins'

class Command(command.Dummy, command.Config):
    '''Dummy command please ignore'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.public_namespace.active_emoji_messages = dict() # dict associating messages to their reaction name, for assigning emojis
        self.public_namespace.active_perm_messages = dict() # dict associating users to their command/reaction name, for assigning perms
        try:
            self.public_namespace.commandersfile = dataloader.datafile(self.config[COMMANDERS])
        except FileNotFoundError:
            print("The %s file is either missing or corrupted; unable to load" %self.config[COMMANDERS])
            self.public_namespace.commandersfile = dataloader.newdatafile(self.config[COMMANDERS])
        if not isinstance(self.public_namespace.commandersfile.content, dict):
            self.public_namespace.commandersfile.content = {REACTIONS:dict(), COMMANDS:dict(), PACKAGES:dict()}
        self.public_namespace.commandersfile.save() # create & save file, in case it didn't exist before
        # commanders is a 3-dimensional dictionary; command_type -> command_name -> {'owner':user_id, 'maintainers':[list of user_ids]}
        self.public_namespace.commanders = self.public_namespace.commandersfile.content
        self.public_namespace.OWNER = OWNER
        self.public_namespace.MAINTAINERS = MAINTAINERS
        self.public_namespace.DEFAULT_OWNER_ID = DEFAULT_OWNER_ID
        self.public_namespace.REACTIONS = REACTIONS
        self.public_namespace.COMMANDS = COMMANDS
        self.public_namespace.PACKAGES = PACKAGES
        self.public_namespace.PLUGINS = PLUGINS
        self.public_namespace.is_commander = self.is_commander

    def shutdown(self):
        super().shutdown()
        self.public_namespace.commandersfile.content = self.public_namespace.commanders
        self.public_namespace.commandersfile.save()

    def is_commander(self, id, name, type):
        return (id == self.public_namespace.commanders[type][name][self.public_namespace.OWNER] or id in self.public_namespace.commanders[type][name][self.public_namespace.MAINTAINERS])
