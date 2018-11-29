from libs import reaction as reactioncommand

class Reaction(reactioncommand.AdminReactionRemoveCommand):
    '''Removes the appropriate role when you react with the right emoji

    **Usage:**
    Remove your reaction to a role message'''
    def __init__(self, *args, **kwargs):
        self.emoji=None
        super().__init__(*args, **kwargs)
    def matches(self, reaction, user):
        if not isinstance(reaction.emoji, str):
            key=reaction.emoji.id
        else: key=reaction.emoji
        return reaction.message.id in self.role_messages and key in self.role_messages[reaction.message.id]
    def action(self, reaction, user, bot):
        if not isinstance(reaction.emoji, str):
            key = reaction.emoji.id
        else: key=reaction.emoji
        yield from bot.remove_roles(user, self.role_messages[reaction.message.id][key])
