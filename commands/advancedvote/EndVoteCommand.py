from libs import command, voting, embed, dataloader, savetome

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

class Command(command.DirectOnlyCommand, command.Multi):

    def __init__(self, vote_dict=None, **kwargs):
        super().__init__(**kwargs)
        self.vote_dict = self.public_namespace.vote_dict

    def matches(self, message):
        return re.search(r'\bend\s+["]([^"]+)["]+\s+\bvote', message.content, re.I) != None

    def action(self, message, send_func):
        args = re.search(r'\b(end)\s+["]([^"]+)["]+\s+\b(vote)', message.content, re.I)
        #group(1) is end, group(2) is vote name, group(3) is vote
        if args.group(2) in self.vote_dict:
            yield from send_func(message.channel, embed=embed.create_embed(title=self.vote_dict[args.group(2)][NAME], description=self.format_results(self.vote_dict[args.group(2)][VOTES].tallyVotes()), footer={"text":"Voting ended", "icon_url":None}, colour=0xee3333))
            del(self.vote_dict[args.group(2)])
        else:
            found=False
            for poll in self.vote_dict:
                if args.group(2) == self.vote_dict[poll][NAME]:
                    found=True
                    yield from send_func(message.channel, embed=embed.create_embed(title=self.vote_dict[poll][NAME], description=self.format_results(self.vote_dict[poll][VOTES].tallyVotes()), footer={"text":"Voting ended", "icon_url":None}, colour=0xee3333))
                    del(self.vote_dict[poll])
                    break
            if not found:
                yield from send_func(message.channel, "Invalid ID or name")

    def format_results(self, results, start="Vote Results: \n"):
        output = start[:]
        if len(results) != 0:
            for i in results:
                output += str(i[0])+": "+str(i[1])+"\n"
        else:
            output += "No Votes Recorded"
        return output
