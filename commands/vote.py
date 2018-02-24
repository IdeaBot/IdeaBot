from commands import command
from libs import voting, embed

import re

vote_dict = dict() #dict of polls, by name
MODE = "mode"
VOTES = "votes"

class VoteCommand(command.Command):

    def matches(self, message):
        #vote for <option> in <poll>
        return re.search(r'\b(vote\s+for)\s+\b([^\s]+)\s+\b(in)\s+\b([^\s])', message.content, re.I) != None and message.server == None

    def action(self, message, send_func):
        #vote for <option(s)> in <poll name>
        #options should only be seperated by a comma (when appropriate)
        args = re.search(r'\b(vote\s+for)\s+\b([^\s]+)\s+\b(in)\s+\b([^\s]+)', message.content, re.I)
        #group(1) is vote for, group(2) is option, group(3) is in, group(4) is poll name
        if args.group(4) in vote_dict:
            if vote_dict[args.group(4)][MODE] == "stv":
                try:
                    vote_dict[args.group(4)][VOTES].addVote(message.author.id, args.group(2).split(","))
                    yield from send_func(message.channel, "Thanks for voting `"+args.group(2)+"` in `"+args.group(4)+"`")
                except ValueError:
                    yield from send_func(message.channel, "I'm sorry, are you sure your vote is right for that poll?")
            elif vote_dict[args.group(4)][MODE] == "fptp" or vote_dict[args.group(4)][MODE] == "":
                try:
                    vote_dict[args.group(4)][VOTES].addVote(message.author.id, args.group(2))
                    yield from send_func(message.channel, "Thanks for voting `"+args.group(2)+"` in `"+args.group(4)+"`")
                except ValueError:
                    yield from send_func(message.channel, "I'm sorry, are you sure your vote is right for that poll?")
        else:
            yield from send_func(message.channel, "I'm sorry, are you sure your vote is right for that poll?")
            print("Invalid poll name")
        print("name:", args.group(4), "options:", args.group(2))

class StartVoteCommand(command.DirectOnlyCommand):

    def matches(self, message):
        messagelowercase = message.content.lower()
        return "start" in messagelowercase and "vote" in messagelowercase and re.search(r'\b(mode:?)?\s+\b([^\s]+)\s+\b(name:?)?\s+\b([^\s]+)\s+\b(options:?)?\s+\b([^\s]+)', message.content, re.I) != None

    def action(self, message, send_func):
        #this should add the name of the vote to vote_dict and initialise vote_dict[vote name]
        args = re.search(r'\b(mode:?)?\s+\b([^\s]+)\s+\b(name:?)?\s+\b([^\s]+)\s+\b(options:?)?\s+\b([^\s]+)', message.content, re.I)
        #group(1) is mode, group(2) is mode value, group(3) is name, group(4) is name value
        #group(5) is options, group(6) is options value (which will be split at commas)
        #TODO: clean this up and make it work better
        if args.group(4) not in vote_dict:
            if args.group(2).lower() == "fptp" or args.group(2)=="":
                vote_dict[args.group(4)] = dict()
                vote_dict[args.group(4)][VOTES] = voting.FPTP(options=args.group(6).split(","))
                vote_dict[args.group(4)][MODE] = args.group(2).lower()
            elif args.group(2).lower() == "stv":
                vote_dict[args.group(4)] = dict()
                vote_dict[args.group(4)][VOTES] = voting.STV(options=args.group(6).split(","))
                vote_dict[args.group(4)][MODE] = args.group(2).lower()
            yield from send_func(message.channel, embed=embed.create_embed(title=args.group(4), description="Options: "+str(vote_dict[args.group(4)][VOTES].options)+"\nMode: "+vote_dict[args.group(4)][MODE], footer={"text":"Voting started", "icon_url":None}, colour=0x00ff00))
            #print("mode:", vote_dict[args.group(4)][MODE], "name:", args.group(4), "options:", vote_dict[args.group(4)][VOTES].options)
        else:
            yield from send_func(message.channel, "Name conflict - please choose a different name")

class EndVoteCommand(command.DirectOnlyCommand):

    def matches(self, message):
        return re.search(r'\b(end)\s+\b([^\s]+)\s+\b(vote)', message.content, re.I) != None

    def action(self, message, send_func):
        args = re.search(r'\b(end)\s+\b([^\s]+)\s+\b(vote)', message.content, re.I)
        #group(1) is end, group(2) is vote name, group(3) is vote
        if args.group(2) in vote_dict:
            #vote counting
            yield from send_func(message.channel, embed=embed.create_embed(title=args.group(2), description=self.format_results(vote_dict[args.group(2)][VOTES].tallyVotes()), footer={"text":"Voting ended", "icon_url":None}, colour=0xff0000))
            del(vote_dict[args.group(2)])

    def format_results(self, results, start="Vote Results: \n"):
        print(results)
        output = start[:]
        if len(results) != 0:
            for i in results:
                output += str(i[0])+": "+str(i[1])+"\n"
        else:
            output += "No Votes Recorded"
        return output
