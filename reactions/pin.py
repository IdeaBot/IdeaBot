from reactions import reactioncommand
import asyncio

class PinReaction(reactioncommand.AdminReactionAddCommand):
    @asyncio.coroutine
    def action(self, reaction, user, client):
        if reaction.message.channel.permissions_for(reaction.message.server.me).manage_messages:
            yield from client.pin_message(reaction.message)
        else:
            print("Missing manage messages perms")
