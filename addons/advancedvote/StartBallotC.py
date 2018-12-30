from libs import command, voting, embed, dataloader

import re, time

MODE = "mode"
VOTES = "votes"
NAME = "name"
REACTIONS = [chr(x) for x in list(range(127462, 127462+26))] #all the regional indicators from 🇦 to 🇿
VALID_MODES=["fptp", "stv", ""] #iterable
DEFAULT_MODE="fptp" #string
DEFAULT_NAME_GEN=time.time #function
DEFAULT_OPTIONS=["Yes", "No"] #list
DEFAULT_TRANSFERABLES=3 #int

class Command(command.DirectOnlyCommand):
    '''Allows individuals to case their ballot. I will DM you your ballot.

**Usage**
```@Idea vote in "<poll name>"```
Where
**`<poll name>`** is an open poll

**Example**
`@Idea vote in "Yomama is..."`

Alternately, react to the poll message with the ballot/vote emoji
(The emoji is server-defined; ask your fellow server members for the correct emoji)'''
    def __init__(self, vote_dict=dict(), ballots=dict(), **kwargs):
        super().__init__(**kwargs)
        self.vote_dict = self.public_namespace.vote_dict
        self.ballots = self.public_namespace.ballot

    def matches(self, message):
        args = re.search(r'\bvote\s+in\s+["]([^"]+)["]', message.content, re.I)
        if args == None:
            return False
        for i in self.vote_dict:
            if self.vote_dict[i][NAME] == args.group(1) or i == args.group(1):
                self.ballots[message.author.id]=i
                return True
        return False

    def action(self, message):
        reply = "Poll: **"+self.vote_dict[self.ballots[message.author.id]][NAME]+"**\n"
        for i in range(len(self.vote_dict[self.ballots[message.author.id]][VOTES].options)):
            reply += REACTIONS[i]+" : "+self.vote_dict[self.ballots[message.author.id]][VOTES].options[i]+"\n"
        reply +="""
Please place your vote by reacting with your choice(s).
In the event that multiple choices are accepted, choices will be considered in chronological order (ie first reaction is first choice, second reaction is second choice, etc).
**No take-backsies.**"""
        msg = yield from self.send_message(message.author, reply)
        self.always_watch_messages.add(msg)
