from reactions import reactioncommand

class RetryCommand(reactioncommand.AdminReactionAddCommand):
    def __init__(self, emoji, all_emojis_func, perms=None, **kwargs):
        '''(RetryCommand, str, discord.Emoji, dict) -> None '''
        super().__init__(all_emojis_func, perms, **kwargs)
        self.emoji = emoji

    def matches(self, reaction, user):
        return reaction.emoji == (self.matchemoji(self.emoji) or False) and user == reaction.message.author
        # (None or False) = False ; this prevents returning a NoneType when expecting a bool

    def action(self, reaction, user, client):
        yield from client.on_message(reaction.message)
