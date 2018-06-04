from libs import command

class Command(command.Multi, command.Dummy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.public_namespace.active_emoji_messages = dict() # dict associating messages to their reaction name, for assigning emojis
        self.public_namespace.active_perm_messages = dict() # dict associating users to their command/reaction name, for assigning perms
