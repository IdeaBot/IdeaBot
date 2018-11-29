from libs import reaction as reactioncommand

REACTIONS = [chr(x) for x in list(range(127462, 127462+26))] #all the regional indicators from 🇦 to 🇿
FIRST_REACTION_ORD = 127462
MODE = "mode"
VOTES = "votes"
NAME = "name"

class Reaction(reactioncommand.ReactionAddCommand):
    '''Casts your vote

**Usage**
React to the ballot message I sent you with the appropriate regional indicator(s) '''
    def __init__(self, **kwargs):
        self.emoji = None
        super().__init__(**kwargs)
        self.vote_dict=self.public_namespace.vote_dict
        self.ballots=self.public_namespace.ballot
    def matches(self, reaction, user):
        return (reaction.emoji in REACTIONS) and (user.id in self.ballots) and (self.ballots[user.id] in self.vote_dict) and (ord(reaction.emoji)-FIRST_REACTION_ORD < len(self.vote_dict[self.ballots[user.id]][VOTES].options)) and (ord(reaction.emoji)>=FIRST_REACTION_ORD) and (reaction.message.server == None)

    def action(self, reaction, user):
        registered = self.vote_dict[self.ballots[user.id]][VOTES].addChoice(user.id, self.vote_dict[self.ballots[user.id]][VOTES].options[ord(reaction.emoji)-FIRST_REACTION_ORD])
        if registered:
            yield from self.send_message(reaction.message.channel, "Your choice "+str(reaction.emoji)+" for "+self.vote_dict[self.ballots[user.id]][NAME]+" has been recorded")
            if self.vote_dict[self.ballots[user.id]][MODE]=="stv" and self.vote_dict[self.ballots[user.id]][VOTES].votes[user.id].count(None)>0:
                yield from self.send_message(reaction.message.channel, "You have "+str(self.vote_dict[self.ballots[user.id]][VOTES].votes[user.id].count(None))+" votes remaining")
            else:
                yield from self.send_message(reaction.message.channel, "Thanks for voting!")
