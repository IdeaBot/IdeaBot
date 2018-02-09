from reactions import reactioncommand as rc

import asyncio

class InvalidCommand(rc.ReactionAddCommand, rc.ReactionRemoveCommand):
    def __init__(self, all_emojis_func=list, perms=None, **kwargs):
        super().__init__(all_emojis_func, perms=None, **kwargs)
    def matches(self, reaction, user):
        return True

    @asyncio.coroutine
    def action(self, reaction, user):
        #print(reaction.emoji) #debug
        pass
