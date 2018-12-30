from libs import reaction as reactioncommand

class Reaction(reactioncommand.AdminReactionAddCommand):
    '''Retries a text command

**Usage**
React to the message you want to re-run with the retry emoji
(The emoji is server-defined; ask your fellow server members for the correct emoji)'''

    def matches(self, reaction, user):
        return user == reaction.message.author

    def action(self, reaction, user, client):
        yield from client.on_message(reaction.message)
