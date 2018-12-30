from libs import reaction as rc

import asyncio

class Reaction(rc.ReactionAddCommand, rc.ReactionRemoveCommand):
    '''Invalid reactions

**Usage**
Step 1: Find a message
Step 2: Think of your favourite emoji (that isn't used in a reaction command)
Step 3: React to the message with your emoji
(This reaction command does nothing)'''
    def matches(self, reaction, user):
        return True

    @asyncio.coroutine
    def action(self, reaction, user):
        #print(reaction.emoji) #debug
        pass
