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
    '''Starts a poll

**Usage**
```@Idea start vote [name "<name>"] [options "<option1>" "<option2>" (...)] [mode (FPTP or STV)] [-v]```
Where
**`FPTP`** stands for First Past The Post *(default)*
**`STV`** stands for Single Transferable Vote
*(You know where Google is if you don't know what those are)*

**NOTE:** everything surrounded by [ and ] is optional

**Example**
`@Idea start vote name "Yomama is..." options "fat" "easy" "ugly" mode FPTP`
`@Idea start vote name "Is Idea Great?" options "yes" "no doubt"`

The StartVoteCommand is probably restricted to certain users'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vote_dict = self.public_namespace.vote_dict

    def matches(self, message):
        messagelowercase = message.content.lower()
        return re.search(r'start\s+vote\s*', message.content, re.I) != None

    def action(self, message):
        send_func = self.send_message
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
