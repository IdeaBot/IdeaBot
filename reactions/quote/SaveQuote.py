from libs import reaction as reactioncommand
from libs import embed, dataloader
import asyncio

SAVE_LOC = 'saveloc'

class Reaction(reactioncommand.ReactionAddCommand, reactioncommand.Config):
    '''Saves messages when they get the right reaction'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.saveloc = self.config.content["DEFAULT"][SAVE_LOC]

    @asyncio.coroutine
    def action(self, reaction, user):
        messageData = dataloader.newdatafile(self.saveloc+"/"+reaction.message.id+".txt")
        messageData.content = [str({
            "author":reaction.message.author.display_name,
            "channel":reaction.message.channel.name,
            "server":reaction.message.server.name,
            "content":reaction.message.content,
            "id": {
                "author":reaction.message.author.id,
                "channel":reaction.message.channel.id,
                "server":reaction.message.server.id,
                "message":reaction.message.id}})]
        messageData.save()
