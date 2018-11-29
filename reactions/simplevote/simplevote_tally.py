from libs import reaction as reactioncommand
import asyncio

class Reaction(reactioncommand.ReactionAddCommand):
    '''A Reaction command for tallying votes on messages

**Usage**
React to the message you want to tally with the tally emoji
(The emoji is server-defined; ask your fellow server members for the correct emoji)'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vote_dict = self.public_namespace.vote_dict

    def action (self, reaction, user):
        yield from self.send_message(reaction.message.channel, "The tally is "+str(self.tally(reaction.message.id)))

    def tally(self, message_id):
        '''(discord.Message.id) -> int
        calculates the vote's tally'''
        if message_id not in self.vote_dict:
            return 0
        total = 0
        for i in self.vote_dict[message_id]:
            total += self.vote_dict[message_id][i]
        return total
