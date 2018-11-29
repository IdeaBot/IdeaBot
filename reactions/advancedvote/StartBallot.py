from libs import reaction as reactioncommand

REACTIONS = [chr(x) for x in list(range(127462, 127462+26))] #all the regional indicators from 🇦 to 🇿
FIRST_REACTION_ORD = 127462
MODE = "mode"
VOTES = "votes"
NAME = "name"

class Reaction(reactioncommand.ReactionAddCommand):
    '''Allows individuals to case their ballot. I will DM you your ballot.

**Usage**
React to a poll started message with the ballot/vote emoji
(The emoji is server-defined; ask your fellow server members for the correct emoji) '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vote_dict=self.public_namespace.vote_dict
        self.ballots=self.public_namespace.ballot
    def matches(self, reaction, user):
        return reaction.message.id in self.vote_dict
    def action(self, reaction, user):
        self.ballots[user.id]=reaction.message.id
        message = "Poll: **"+self.vote_dict[reaction.message.id][NAME]+"**\n"
        for i in range(len(self.vote_dict[reaction.message.id][VOTES].options)):
            message += REACTIONS[i]+" : "+self.vote_dict[reaction.message.id][VOTES].options[i]+"\n"
        message +="""
Please place your vote by reacting with your choice(s).
In the event that multiple choices are accepted, choices will be considered in chronological order (ie first reaction is first choice, second reaction is second choice, etc).
**No take-backsies.**"""
        msg = yield from self.send_message(user, message)
        self.always_watch_messages.add(msg)
