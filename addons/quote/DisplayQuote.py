from libs import reaction as reactioncommand
from libs import embed
import asyncio

class Reaction(reactioncommand.ReactionAddCommand):
    '''Re-posts a previous message in the same channel

**Usage**
React to the message you want to be quoted with the quote emoji
(The emoji is server-defined; ask your fellow server members for the correct emoji)'''
    def action(self, reaction, user):
        em = embed.create_embed(author={"name":reaction.message.author.display_name, "url":None, "icon_url":None},
            footer={"text": "#"+reaction.message.channel.name+" of "+reaction.message.server.name, "icon_url":None},
            description=reaction.message.content,
            colour=0xeeeeee)
        yield from self.send_message(reaction.message.channel, embed=em)
