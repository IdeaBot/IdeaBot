from reactions import reactioncommand as rc

import asyncio

class InvalidCommand(rc.ReactionAddCommand, rc.ReactionRemoveCommand):
    def matches(self, reaction, user):
        return True

    @asyncio.coroutine
    def action(self, reaction, user):
        #print(reaction.emoji) #debug
        pass
