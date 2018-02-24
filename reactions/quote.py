from reactions import reactioncommand
from libs import embed, dataloader
import asyncio

class SaveQuote(reactioncommand.ReactionAddCommand):
    '''Saves messages when they get the right reaction'''
    def __init__(self, saveloc="./", **kwargs):
        super().__init__(**kwargs)
        self.saveloc = saveloc

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

class DisplayQuote(reactioncommand.AdminReactionAddCommand):
    def action(self, reaction, user, client):
        em = embed.create_embed(author={"name":reaction.message.author.display_name, "url":None, "icon_url":None},
            footer={"text": "#"+reaction.message.channel.name+" of "+reaction.message.server.name, "icon_url":None},
            description=reaction.message.content,
            colour=0xeeeeee)
        yield from client.send_message(reaction.message.channel, embed=em)
