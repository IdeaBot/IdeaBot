from libs import reaction as reactioncommand
import asyncio

PIN = '📌'

class Reaction(reactioncommand.AdminReactionAddCommand):
    '''So you don't have to give users permissions to delete messages in order to let them pin messages

**Usage**
React to a message you want pinned with the `:pushpin:` emoji

The Pin command is probably restricted to certain users'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.emoji = None
    def matches(self, reaction, user):
        return reaction.emoji == PIN

    @asyncio.coroutine
    def action(self, reaction, user, client):
        if reaction.message.channel.permissions_for(reaction.message.server.me).manage_messages:
            yield from client.pin_message(reaction.message)
