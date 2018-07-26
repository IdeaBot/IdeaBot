from libs import plugin, embed
import discord, traceback, datetime

CHANNEL = 'channel'
MESSAGE = 'message'

class Plugin(plugin.OnReadyPlugin, plugin.AdminPlugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.CHANNEL_ID = self.config[CHANNEL]
        self.MESSAGE_ID = self.config[MESSAGE]
        self.channel = discord.Object(id=self.CHANNEL_ID)
        self.message = discord.Object(id=self.MESSAGE_ID)
        self.message.channel = self.channel

    async def action(self):
        # create embed description
        description = ""
        description += "**Servers** : %s \n" %len(self.bot.servers)
        description += "**Messages seen** : %s \n" %len(self.bot.messages)
        description += "**Messages watched** : %s \n" %len(self.bot.always_watch_messages)
        description += "~~Potatoes picked~~ : 2\n"
        description += "**Last Updated** : %s \n" % datetime.datetime.now().isoformat()

        await self.edit_message(self.message, new_content=' ', embed=embed.create_embed(description=description))
