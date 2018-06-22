from libs import reaction as reactioncommand
import asyncio

class Reaction(reactioncommand.AdminReactionAddCommand, reactioncommand.Multi):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vote_dict = self.public_namespace.vote_dict

    def action (self, reaction, user, client):
        yield from client.send_message(reaction.message.channel, "The tally is "+str(self.tally(reaction.message.id)))

    def tally(self, message_id):
        '''(discord.Message.id) -> int
        calculates the vote's tally'''
        if message_id not in self.vote_dict:
            return 0
        total = 0
        for i in self.vote_dict[message_id]:
            total += self.vote_dict[message_id][i]
        return total
