from libs import plugin
import discord, random

class Plugin(plugin.AdminPlugin, plugin.OnReadyPlugin):
    async def action(self):
        #await self.client.send_message(discord.Object(id="381172950448996365"), "testing") # slowly spam #bot-spam channel
        print("test")
