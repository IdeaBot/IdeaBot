from reactions import reactioncommand
import asyncio

vote_dict = dict() # global variables ftw. this is a dict of dicts; dict-ception

class VoteAddReaction(reactioncommand.ReactionAddCommand):
    def __init__(self, all_emojis_func, yes_emoji, no_emoji, perms=None):
        '''(RetryCommand, func, str, str, str, dict) -> None '''
        super().__init__(all_emojis_func, perms=perms)
        self.yes_emoji = yes_emoji
        self.no_emoji = no_emoji

    def matches(self, reaction, user):
        return (reaction.emoji == self.matchemoji(self.yes_emoji)) or (reaction.emoji == self.matchemoji(self.no_emoji))

    @asyncio.coroutine
    def action(self, reaction, user):
        if reaction.message.id not in vote_dict:
            vote_dict[reaction.message.id] = dict()
        if user.id not in vote_dict[reaction.message.id] or vote_dict[reaction.message.id][user.id] == 0:
            if reaction.emoji == self.matchemoji(self.yes_emoji):
                vote_dict[reaction.message.id][user.id] = 1
            else:
                vote_dict[reaction.message.id][user.id] = -1


class VoteRemoveReaction(reactioncommand.ReactionRemoveCommand):
    def __init__(self, all_emojis_func, yes_emoji, no_emoji, perms=None):
        '''(RetryCommand, func, str, str, str, dict) -> None '''
        super().__init__(all_emojis_func, perms=perms)
        self.yes_emoji = yes_emoji
        self.no_emoji = no_emoji

    def matches(self, reaction, user):
        return (reaction.emoji == self.matchemoji(self.yes_emoji)) or (reaction.emoji == self.matchemoji(self.no_emoji))

    @asyncio.coroutine
    def action(self, reaction, user):
        if reaction.message.id in vote_dict:
            vote_dict[reaction.message.id][user.id] = 0

def tally(message_id):
    '''(discord.Message.id) -> int
    calculates the vote's tally'''
    if message_id not in vote_dict:
        return 0
    total = 0
    for i in vote_dict[message_id]:
        total += vote_dict[message_id][i]
    return total

class VoteTallyReaction(reactioncommand.AdminReactionAddCommand):
    def __init__(self, all_emojis_func, emoji, perms=None):
        super().__init__(all_emojis_func, perms=perms)
        self.emoji = emoji

    def matches(self, reaction, user):
        return reaction.emoji == self.matchemoji(self.emoji)

    def action (self, reaction, user, client):
        yield from client.send_message(reaction.message.channel, "The tally is "+str(tally(reaction.message.id)))
