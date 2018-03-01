from commands import command
from libs import voting, embed

import re, time

MODE = "mode"
VOTES = "votes"
NAME = "name"
VALID_MODES=["fptp", "stv", ""] #iterable
DEFAULT_MODE="fptp" #string
DEFAULT_NAME_GEN=time.time #function
DEFAULT_OPTIONS=["Yes", "No"] #list
DEFAULT_TRANSFERABLES=3 #int

class StartVoteCommand(command.DirectOnlyCommand):

    def __init__(self, vote_dict=None, **kwargs):
        super().__init__(**kwargs)
        self.vote_dict = vote_dict

    def matches(self, message):
        messagelowercase = message.content.lower()
        return re.search(r'start\s+vote\s*', message.content, re.I) != None

    def action(self, message, send_func):
        #this should add the name of the vote to vote_dict and initialise vote_dict[vote name]
        # old thing: args = re.search(r'\b(mode:?)?\s+\b([^\s]+)\s+\b(name:?)?\s+\b([^\s]+)\s+\b(options:?)?\s+\b([^\s]+)', message.content, re.I)
        #mode:?\s*["'\s]([^"'\s]+)["'\s]
        #group(1) is mode, group(2) is mode value, group(3) is name, group(4) is name value
        #group(5) is options, group(6) is options value (which will be split at commas)
        #TODO: clean this up and make it work better
        reply = ""
        temp_dict = dict()
        mode = re.compile(r'\bmode[:=]?\s*([^\s]+)\s*', re.I).search(message.content)
        if mode==None or mode.group(1).strip("\'\"").lower() not in VALID_MODES:
            reply+= 'Choosing default mode. Set a mode by putting `mode` in front of a valid mode, like `mode: stp ` or `mode fptp ` \n'
            temp_dict[MODE]=DEFAULT_MODE
        else:
            temp_dict[MODE]=mode.group(1).strip("\'\"").lower()

        name = re.compile(r'\bname[:=]?\s*["]([^"]+)["]', re.I).search(message.content)
        if name==None or name.group(1)=="":
            reply+='Choosing default name. Set a mode by putting `name` in front of a name, surrounded by quotes, like `name \"My Cool Poll\"` or `name:\"Awesome Poll Name\"` \n'
            temp_dict[NAME]=str(DEFAULT_NAME_GEN())
        else:
            temp_dict[NAME]=name.group(1)

        options = re.compile(r'\boptions?[:=]?\s*((["][^"]+["][\s,]*)+)', re.I).search(message.content)
        if options==None:
            reply+='Choosing default options. Set options by putting `options` in front of options surrounded by quotes, like `options: \"Idea\" \"Project\" \"Channel\"` or `option\"Mace\"\"Flash\"\"Mike\"\"NG\"` \n'
            options = DEFAULT_OPTIONS
        else:
            options = options.group(1).split('\"')
            options = [options[i] for i in range(len(options)) if i%2==1]

        if temp_dict[MODE] == "fptp" or temp_dict[MODE]=="":
            temp_dict[VOTES] = voting.FPTP(options=list(options))
        elif temp_dict[MODE] == "stv":
            try:
                transferables=int(re.compile(r'\bt[\D]{0,12}[:=]?\s*(\d+)\s*', re.I).search(message.content).group(1))
            except:
                transferables=DEFAULT_TRANSFERABLES
            reply+="Transferables set to "+str(transferables)
            temp_dict[VOTES] = voting.STV(options=list(options), transferables=transferables)
        if reply !="" and (" -v " in message.content.lower() or " -v" == message.content.lower()[-3:]):
            yield from send_func(message.author, reply) #send error msg (if any)
        embed_message = yield from send_func(message.channel, embed=embed.create_embed(title=temp_dict[NAME], description="Options: "+str(temp_dict[VOTES].options)+"\nMode: "+temp_dict[MODE], footer={"text":"Voting started", "icon_url":None}, colour=0x33ee33))
        self.vote_dict[embed_message.id]=dict(temp_dict)
        return


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
