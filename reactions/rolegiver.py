from reactions import reactioncommand
from libs import dataloader

import asyncio, re, discord, time

role_messages = dict()

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

class RoleMessageCreate(reactioncommand.AdminReactionAddCommand, RoleReaction):
    @asyncio.coroutine
    def action(self, reaction, user, bot):
        emojiToRoleDict = self.associateEmojiToRoles(reaction.message.content)
        if emojiToRoleDict!=None:
            for emoji in emojiToRoleDict: #add all the emojis so people don't have to search through the list
                yield from bot.add_reaction(reaction.message, emoji)
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

    def matchRole(self, roleID, roles): #unnecessary method
        for role in roles:
            if role.id == roleID:
                return role
