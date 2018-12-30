from libs import reaction as reactioncommand
import asyncio

YES_EMOJI = "✔️"
NO_EMOJI = "✖️"

class Reaction(reactioncommand.ReactionAddCommand):
    '''A Reaction command for simple voting on messages

**Usage**
React to the message you want to vote on with the upvote or downvote emoji
(The emojis are server-defined; ask your fellow server members for the correct emojis)'''
    def __init__(self, **kwargs):
        '''(RetryCommand, func, str, str, str, dict) -> None '''
        super().__init__(**kwargs)
        self.emoji = None
        self.vote_dict = self.public_namespace.vote_dict

    def matches(self, reaction, user):
        # return (reaction.emoji == self.matchemoji(self.yes_emoji)) or (reaction.emoji == self.matchemoji(self.no_emoji))
        return (self.are_same_emoji(self.public_namespace.no_emoji, reaction.emoji)) or (self.are_same_emoji(self.public_namespace.yes_emoji, reaction.emoji))

    @asyncio.coroutine
    def action(self, reaction, user):
        if reaction.message.id not in self.vote_dict:
            self.vote_dict[reaction.message.id] = dict()
        if user.id not in self.vote_dict[reaction.message.id] or self.vote_dict[reaction.message.id][user.id] == 0:
            if self.are_same_emoji(self.public_namespace.yes_emoji, reaction.emoji):
                self.vote_dict[reaction.message.id][user.id] = 1
            else:
                self.vote_dict[reaction.message.id][user.id] = -1
