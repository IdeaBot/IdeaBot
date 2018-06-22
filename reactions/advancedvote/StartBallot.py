from libs import reaction as reactioncommand

REACTIONS = [chr(x) for x in list(range(127462, 127462+26))] #all the regional indicators from 🇦 to 🇿
FIRST_REACTION_ORD = 127462
MODE = "mode"
VOTES = "votes"
NAME = "name"

class Reaction(reactioncommand.AdminReactionAddCommand, reactioncommand.WatchReactionCommand, reactioncommand.Multi):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vote_dict=self.public_namespace.vote_dict
        self.ballots=self.public_namespace.ballot
    def matches(self, reaction, user):
        return reaction.message.id in self.vote_dict
    def action(self, reaction, user, client):
        self.ballots[user.id]=reaction.message.id
        message = "Poll: **"+self.vote_dict[reaction.message.id][NAME]+"**\n"
        for i in range(len(self.vote_dict[reaction.message.id][VOTES].options)):
            message += REACTIONS[i]+" : "+self.vote_dict[reaction.message.id][VOTES].options[i]+"\n"
        message +="""
Please place your vote by reacting with your choice(s).
In the event that multiple choices are accepted, choices will be considered in chronological order (ie first reaction is first choice, second reaction is second choice, etc).
**No take-backsies.**"""
        msg = yield from client.send_message(user, message)
        self.always_watch_messages.add(msg)
