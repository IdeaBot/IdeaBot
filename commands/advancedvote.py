from commands import command
from libs import voting, embed, dataloader

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

class StartVoteCommand(command.DirectOnlyCommand, command.WatchCommand):

    def __init__(self, vote_dict=None, **kwargs):
        super().__init__(**kwargs)
        self.vote_dict = vote_dict

    def matches(self, message):
        messagelowercase = message.content.lower()
        return re.search(r'start\s+vote\s*', message.content, re.I) != None

    def action(self, message, send_func):
        reply = ""
        temp_dict = dict()
        mode = re.compile(r'\bmode[:=]?\s*([^\s]+)\s*', re.I).search(message.content)
        if mode==None or mode.group(1).strip("\'\"").lower() not in VALID_MODES:
            reply+= 'Choosing default mode. Set a mode by putting `mode` in front of a valid mode, like `mode: stp ` or `mode fptp ` \n'
            temp_dict[MODE]=DEFAULT_MODE
        else:
            temp_dict[MODE]=mode.group(1).strip("\'\"").lower()
            reply+='Mode set to '+temp_dict[MODE]+"\n"

        name = re.compile(r'\bname[:=]?\s*["]([^"]+)["]', re.I).search(message.content)
        name_is_used = False
        if name!=None and name.group(1)!="":
            for poll in self.vote_dict:
                if self.vote_dict[poll][NAME]==name.group(1):
                    name_is_used=True
                    break
        if name==None or name.group(1)=="" or name_is_used:
            reply+='Name conflict or no name declared. Choosing default name. Set a unique name by putting `name` in front of a name, surrounded by quotes, like `name \"My Cool Poll\"` or `name:\"Awesome Poll Name\"` \n'
            temp_dict[NAME]=str(DEFAULT_NAME_GEN())
        else:
            temp_dict[NAME]=name.group(1)
            reply+='Name set to '+temp_dict[NAME]+"\n"

        options = re.compile(r'\boptions?[:=]?\s*((["][^"]+["][\s,]*)+)', re.I).search(message.content)
        if options==None:
            reply+='Choosing default options. Set options by putting `options` in front of options surrounded by quotes, like `options: \"Idea\" \"Project\" \"Channel\"` or `option\"Mace\"\"Flash\"\"Mike\"\"NG\"` \n'
            options = DEFAULT_OPTIONS
        else:
            options = options.group(1).split('\"')
            options = [options[i] for i in range(len(options)) if i%2==1]
            reply+= 'Options set to '+str(options)+"\n"

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
        self.always_watch_messages.add(embed_message) # never stop watching for reactions to embed_message
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

class StartBallot(command.DirectOnlyCommand):
    def __init__(self, vote_dict=dict(), ballots=dict(), **kwargs):
        super().__init__(**kwargs)
        self.vote_dict = vote_dict
        self.ballots = ballots

    def matches(self, message):
        args = re.search(r'\bvote\s+in\s+["]([^"]+)["]', message.content, re.I)
        if args == None:
            return False
        for i in self.vote_dict:
            if self.vote_dict[i][NAME] == args.group(1) or i == args.group(1):
                self.ballots[message.author.id]=i
                return True
        return False

    def action(self, message, send_func):
        reply = "Poll: **"+self.vote_dict[self.ballots[message.author.id]][NAME]+"**\n"
        for i in range(len(self.vote_dict[self.ballots[message.author.id]][VOTES].options)):
            reply += REACTIONS[i]+" : "+self.vote_dict[self.ballots[message.author.id]][VOTES].options[i]+"\n"
        reply +="""
Please place your vote by reacting with your choice(s).
In the event that multiple choices are accepted, choices will be considered in chronological order (ie first reaction is first choice, second reaction is second choice, etc).
**No take-backsies.**"""
        msg = yield from send_func(message.author, reply)
        self.always_watch_messages.add(msg)

def save_vote_dict(filename, vote_dict):
    '''(str, dict) -> None
    Saves vote_dict to filename in a format interpretable by load_vote_dict(filename)'''
    vote_dict_file = dataloader.newdatafile(filename)
    new_vote_dict=dict()
    for poll_msg_id in vote_dict:
        new_vote_dict[poll_msg_id]=vote_dict[poll_msg_id]
        new_vote_dict[poll_msg_id][VOTES]=vote_dict[poll_msg_id][VOTES].__dict__ #dict representation of variables contained in Poll object
    vote_dict_file.content = new_vote_dict
    vote_dict_file.save(save_as="json")

def load_vote_dict(filename):
    '''(str) -> dict
    Loads vote_dict from filename'''
    vote_dict=dict()
    try:
        vote_dict = dataloader.datafile(filename, load_as="json").content
    except:
        print("The %a file is either missing or corrupted; unable to load" %filename)
    finally:
        for poll_msg_id in vote_dict:
            if vote_dict[poll_msg_id][MODE] == 'stv':
                vote_dict[poll_msg_id][VOTES]=voting.STV(**vote_dict[poll_msg_id][VOTES])
            elif vote_dict[poll_msg_id][MODE] in VALID_MODES:
                vote_dict[poll_msg_id][VOTES]=voting.FPTP(**vote_dict[poll_msg_id][VOTES])
            else:
                try:
                    vote_dict[poll_msg_id][VOTES]=Poll(**vote_dict[poll_msg_id][VOTES])
                except:
                    del(vote_dict[poll_msg_id])
        return vote_dict

def save_ballot(filename, ballot):
    '''(str, dict) -> None
    Saves ballot to filename in a format interpretable by load_ballot(filename)
    In this case it's simply converted to JSON format'''
    ballot_file = dataloader.newdatafile(filename)
    ballot_file.content = ballot
    ballot_file.save(save_as="json")

def load_ballot(filename):
    ballot=dict()
    try:
        ballot = dataloader.datafile(filename, load_as="json").content
    except:
        print("The %a file is either missing or corrupted; unable to load" %filename)
    finally:
        return ballot
