from libs import reaction as reactioncommand

class Reaction(reactioncommand.AdminReactionAddCommand):
    '''A Reaction Command to give you a role when you react with the right emoji

    **Usage:**
    React to a message with emojis associated to roles with the appropriate emoji'''
    def matches(self, reaction, user):
        return reaction.message.id in self.role_messages and reaction.emoji in self.role_messages[reaction.message.id]
    def action(self, reaction, user, bot):
        yield from bot.add_roles(user, self.role_messages[reaction.message.id][reaction.emoji])
