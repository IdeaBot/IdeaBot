from libs import reaction as reactioncommand
from libs import embed
import asyncio

class Reaction(reactioncommand.ReactionAddCommand):
    def action(self, reaction, user):
        em = embed.create_embed(author={"name":reaction.message.author.display_name, "url":None, "icon_url":None},
            footer={"text": "#"+reaction.message.channel.name+" of "+reaction.message.server.name, "icon_url":None},
            description=reaction.message.content,
            colour=0xeeeeee)
        yield from self.send_message(reaction.message.channel, embed=em)
