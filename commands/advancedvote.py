from commands import command
from libs import voting, embed

import re

MODE = "mode"
VOTES = "votes"
NAME = "name"

class StartVoteCommand(command.DirectOnlyCommand):

    def __init__(self, vote_dict=None, **kwargs):
        super().__init__(**kwargs)
        self.vote_dict = vote_dict

    def matches(self, message):
        messagelowercase = message.content.lower()
        return "start" in messagelowercase and "vote" in messagelowercase and re.search(r'\b(mode:?)?\s+\b([^\s]+)\s+\b(name:?)?\s+\b([^\s]+)\s+\b(options:?)?\s+\b([^\s]+)', message.content, re.I) != None

    def action(self, message, send_func):
        #this should add the name of the vote to vote_dict and initialise vote_dict[vote name]
        args = re.search(r'\b(mode:?)?\s+\b([^\s]+)\s+\b(name:?)?\s+\b([^\s]+)\s+\b(options:?)?\s+\b([^\s]+)', message.content, re.I)
        #group(1) is mode, group(2) is mode value, group(3) is name, group(4) is name value
        #group(5) is options, group(6) is options value (which will be split at commas)
        #TODO: clean this up and make it work better
        if args.group(4) not in self.vote_dict:
            temp_dict = dict()
            temp_dict[NAME] = args.group(4)
            temp_dict[MODE] = args.group(2).lower()
            if temp_dict[MODE] == "fptp" or temp_dict[MODE]=="":
                temp_dict[VOTES] = voting.FPTP(options=args.group(6).split(","))
            elif temp_dict[MODE] == "stv":
                temp_dict[VOTES] = voting.STV(options=args.group(6).split(","))
            embed_message = yield from send_func(message.channel, embed=embed.create_embed(title=temp_dict[NAME], description="Options: "+str(temp_dict[VOTES].options)+"\nMode: "+temp_dict[MODE], footer={"text":"Voting started", "icon_url":None}, colour=0x33ee33))
            self.vote_dict[embed_message.id]=dict(temp_dict)

        else:
            yield from send_func(message.channel, "Name conflict - please choose a different name")

class EndVoteCommand(command.DirectOnlyCommand):

    def __init__(self, vote_dict=None, **kwargs):
        super().__init__(**kwargs)
        self.vote_dict = vote_dict

    def matches(self, message):
        return re.search(r'\b(end)\s+\b([^\s]+)\s+\b(vote)', message.content, re.I) != None

    def action(self, message, send_func):
        args = re.search(r'\b(end)\s+\b([^\s]+)\s+\b(vote)', message.content, re.I)
        #group(1) is end, group(2) is vote name, group(3) is vote
        if args.group(2) in self.vote_dict:
            yield from send_func(message.channel, embed=embed.create_embed(title=self.vote_dict[args.group(2)][NAME], description=self.format_results(self.vote_dict[args.group(2)][VOTES].tallyVotes()), footer={"text":"Voting ended", "icon_url":None}, colour=0xee3333))
            del(self.vote_dict[args.group(2)])
        else:
            yield from send_func(message.channel, "Invalid ID")

    def format_results(self, results, start="Vote Results: \n"):
        output = start[:]
        if len(results) != 0:
            for i in results:
                output += str(i[0])+": "+str(i[1])+"\n"
        else:
            output += "No Votes Recorded"
        return output
