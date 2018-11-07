from libs import reaction

class Reaction(reaction.AdminReactionAddCommand):
    '''A Reaction command for setting emojis to commands in servers
    This works alongside `emoji_starter`

    **Usage:**
    React with an emoji to the message sent in response to `emoji_starter` to use that emoji'''
    def matches(self, reaction, user):
        #print(self.public_namespace.active_emoji_messages)
        return reaction.message.id in self.public_namespace.active_emoji_messages

    def action(self, reaction, user, bot):
        if isinstance(reaction.emoji, str):
            emoji_id = reaction.emoji
        else:
            emoji_id = reaction.emoji.id
        if isinstance(bot.reactions[self.public_namespace.active_emoji_messages[reaction.message.id]].emoji, dict):
            bot.reactions[self.public_namespace.active_emoji_messages[reaction.message.id]].emoji[reaction.message.server.id]=emoji_id
        else:
            bot.reactions[self.public_namespace.active_emoji_messages[reaction.message.id]].emoji={reaction.message.server.id:emoji_id}
        yield from self.send_message(reaction.message.channel, "Success!")
