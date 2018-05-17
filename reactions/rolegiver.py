from reactions import reactioncommand
from libs import dataloader

import asyncio, re, discord, time

class RoleReaction(reactioncommand.ReactionCommand):
    def __init__(self, role_messages, **kwargs):
        super().__init__(**kwargs)
        self.role_messages=role_messages

class RoleGiveReaction(reactioncommand.AdminReactionAddCommand, RoleReaction):
    def matches(self, reaction, user):
        return reaction.message.id in self.role_messages and reaction.emoji in self.role_messages[reaction.message.id]
    def action(self, reaction, user, bot):
        yield from bot.add_roles(user, self.role_messages[reaction.message.id][reaction.emoji])

class RoleRemoveReaction(reactioncommand.AdminReactionRemoveCommand, RoleReaction):
    def matches(self, reaction, user):
        return reaction.message.id in self.role_messages and reaction.emoji in self.role_messages[reaction.message.id]
    def action(self, reaction, user, bot):
        yield from bot.remove_roles(user, self.role_messages[reaction.message.id][reaction.emoji])

class RoleMessageCreate(reactioncommand.AdminReactionAddCommand, reactioncommand.WatchReactionCommand,RoleReaction):
    @asyncio.coroutine
    def action(self, reaction, user, bot):
        emojiToRoleDict = self.associateEmojiToRoles(reaction.message.content)
        if emojiToRoleDict!=None:
            for emoji in emojiToRoleDict: #add all the emojis so people don't have to search through the list
                yield from bot.add_reaction(reaction.message, emoji)
            self.always_watch_messages.add(reaction.message)
            self.role_messages[reaction.message.id]=dict(emojiToRoleDict)
            for emoji in emojiToRoleDict: #make sure the bot doesn't get the roles as it reacts with the emojis
                yield from bot.remove_roles(reaction.message.server.me, self.role_messages[reaction.message.id][emoji])

    def associateEmojiToRoles(self, content):
        result = dict() # {discord.Emoji:discord.Object(id=role id),...}
        info = re.search(r'\`{3}((\s|.)+)\`{3}', content, re.I|re.M)
        info = info.group(1).splitlines()
        for line in info:
            lineInfo = re.match(r'(\d{18}|.)\s*:?\s*(\d{18})', line, re.I)
            if lineInfo!=None:
                if len(lineInfo.group(1))==1: #unicode emoji, WIP
                    result[self.matchemoji(lineInfo.group(1))] = discord.Object(lineInfo.group(2)) #this may or may not work
                else:
                    result[self.matchemoji(lineInfo.group(1))] = discord.Object(lineInfo.group(2))
        return result


def save_role_messages(filename, role_messages):
    '''(str) -> None
    saves role_messages dictionary to a json that is readable from load_role_messages(filename)'''
    role_messages_file = dataloader.newdatafile(filename)
    new_role_messages = dict()
    for msg_id in role_messages:
        new_role_messages[msg_id]=dict()
        for emoji in role_messages[msg_id]:
            if str(emoji)==emoji: # if unicode emoji
                new_role_messages[msg_id][emoji]=role_messages[msg_id][emoji].id # turns into dict of {<emoji char>:discord.Role.id}
            else:
                new_role_messages[msg_id][emoji.id]=role_messages[msg_id][emoji].id # turns into dict of {discord.Emoji.id:discord.Role.id}
    role_messages_file.content = new_role_messages
    role_messages_file.save(save_as='json')

def load_role_messages(filename, all_emojis_func):
    '''(str) -> dict
    loads role_messages dictionnary from file filename and returns it'''
    role_messages = dict()
    try:
        role_messages_file = dataloader.datafile(filename, load_as='json')
    except:
        print("The %a file is either missing or corrupted; unable to load" %filename)
        return dict()

    for msg_id in role_messages_file.content:
        role_messages[msg_id]=dict()
        for emoji_id in role_messages_file.content[msg_id]:
            role_messages[msg_id][matchemoji(all_emojis_func, emoji_id)]=discord.Object(role_messages_file.content[msg_id][emoji_id])
    return role_messages

def matchemoji(all_emojis_func, emoji_id):
    '''(ReactionCommand, str) -> discord.Emoji or chr
    matches the emoji's id with the Discord emoji '''
    #return self.emoji==None or self.emoji==reaction.emoji or self.emoji==reaction.emoji.id
    if all_emojis_func == None:
        return
    if str(emoji_id) == emoji_id:
        return emoji_id
    for e in all_emojis_func():
        try:
            if e.id == emoji_id:
                return e
        except:
            if str(e) == emoji_id:
                return e
    print("Fuck")
