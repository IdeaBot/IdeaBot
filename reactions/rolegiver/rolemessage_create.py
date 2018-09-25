from libs import reaction as reactioncommand
import asyncio, re, discord
from libs import savetome

class Reaction(reactioncommand.AdminReactionAddCommand, reactioncommand.WatchReactionCommand, reactioncommand.RoleReaction):
    @asyncio.coroutine
    def action(self, reaction, user, bot):
        emojiToRoleDict = self.associateEmojiToRoles(reaction.message.content)
        if emojiToRoleDict!=None:
            for emoji in emojiToRoleDict: #add all the emojis so people don't have to search through the list
                yield from self.add_reaction(reaction.message, emoji)
            self.always_watch_messages.add(reaction.message)
            self.role_messages[reaction.message.id]=dict(emojiToRoleDict)
            for emoji in emojiToRoleDict: #make sure the bot doesn't get the roles as it reacts with the emojis
                yield from bot.remove_roles(reaction.message.server.me, self.role_messages[reaction.message.id][emoji])
            savetome.save_role_messages(bot.data_config[bot.ROLE_MSG_LOCATION], self.role_messages)

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
