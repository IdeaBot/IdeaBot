from libs import command, voting, embed, dataloader, savetome

import re, time, traceback

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
    '''Command for closing already opened polls

**Usage**
```@Idea end "<poll name>" vote```
Where
**`<poll name>`** is an open poll

The End Vote command is probably restricted to certain users'''

    def __init__(self, vote_dict=None, **kwargs):
        super().__init__(**kwargs)
        self.vote_dict = self.public_namespace.vote_dict

    def matches(self, message):
        return re.search(r'\bend\s+["]([^"]+)["]+\s+\bvote', message.content, re.I) != None

    def action(self, message):
        args = re.search(r'\b(end)\s+["]([^"]+)["]+\s+\b(vote)', message.content, re.I)
        #group(1) is end, group(2) is vote name, group(3) is vote
        try:
            yield from self.close_poll(message, self.send_message, args.group(2))
        except:
            traceback.print_exc()
        '''
        if args.group(2) in self.vote_dict: # find by ID
            yield from send_func(message.channel, embed=embed.create_embed(title=self.vote_dict[args.group(2)][NAME], description=self.format_results(self.vote_dict[args.group(2)][VOTES].tallyVotes()), footer={"text":"Voting ended", "icon_url":None}, colour=0xee3333))
            del(self.vote_dict[args.group(2)])
        else:
            found=False
            for poll in self.vote_dict: # find by name
                if args.group(2) == self.vote_dict[poll][NAME]:
                    found=True
                    yield from send_func(message.channel, embed=embed.create_embed(title=self.vote_dict[poll][NAME], description=self.format_results(self.vote_dict[poll][VOTES].tallyVotes()), footer={"text":"Voting ended", "icon_url":None}, colour=0xee3333))
                    del(self.vote_dict[poll])
                    break
            if not found:
                yield from send_func(message.channel, "Invalid ID or name")'''

    def format_results(self, results, start="Vote Results: \n"):
        output = start[:]
        if len(results) != 0:
            for i in results:
                output += str(i[0])+": "+str(i[1])+"\n"
        else:
            output += "No Votes Recorded"
        return output

    def format_dump(self, dump, start="Votes: \n"):
        output = start[:]
        if len(dump) != 0:
            count = 0
            for vote in dump:
                output += str(vote[0])+": "+str(vote[1]).strip('[]')+"\n"
        else:
            output += "No Votes Recorded"
        return output


    def close_poll(self, message, send_func, poll_name):
        '''(EndVoteCommand, discord.Message, func, str) -> None '''
        poll = self.find_poll_id(poll_name)
        if poll!=None:
            dump = self.vote_dict[poll][VOTES].dumpVotes()
            tally = self.vote_dict[poll][VOTES].tallyVotes()
            description = self.format_results(tally)
            if '-v' in message.content.lower():
                description_v = self.format_dump(dump)
                if '--public' in message.content.lower():
                    yield from send_func(message.channel, embed=embed.create_embed(title=self.vote_dict[poll][NAME], description=description_v, footer={"text":"Votes (verbose mode)", "icon_url":None}, colour=0xeeee00))
                else:
                    yield from send_func(message.author, embed=embed.create_embed(title=self.vote_dict[poll][NAME], description=description_v, footer={"text":"Votes (verbose mode)", "icon_url":None}, colour=0xeeee00))
            yield from send_func(message.channel, embed=embed.create_embed(title=self.vote_dict[poll][NAME], description=description, footer={"text":"Voting ended", "icon_url":None}, colour=0xee3333))
            del(self.vote_dict[poll])
            # remove message from always_watch_messages
            for item in self.always_watch_messages:
                if item.id == poll:
                    self.always_watch_messages.remove(item)
                    break
        else:
            yield from send_func(message.channel, "Invalid ID or name")

    def find_poll_id(self, name):
        if name in self.vote_dict: # name is an ID
            return name
        else:
            for poll_id in self.vote_dict: # find poll_id by poll's name
                if name == self.vote_dict[poll_id][NAME]:
                    return poll_id
