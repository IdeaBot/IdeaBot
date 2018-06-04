from libs import reaction as reactioncommand

class Reaction(reactioncommand.AdminReactionAddCommand):

    def matches(self, reaction, user):
        return user == reaction.message.author
        # (None or False) = False ; this prevents returning a NoneType when expecting a bool

    def action(self, reaction, user, client):
        yield from client.on_message(reaction.message)
