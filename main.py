import discord
import logging, time, asyncio, random

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class MyClient(discord.Client):

    @asyncio.coroutine
    def on_ready(self):
        #work or die
        print(self.user)
        print(self.email)
        for i in self.servers:
            print(i)
        #self.logout()

    @asyncio.coroutine
    def on_message(self, message):
        if message.author != self.user: # everything past here will eventually become some super string parser
            if message.author[:len("ngnius")].lower() == "ngnius" and "shutdown protocol 0" in message.content.lower(): #if ngnius says shutdown
                yield from self.logout()
            elif "hotdog" in message.content.lower() or "dick" in message.content.lower() or "hot-dog" in message.content.lower():
                yield from self.send_message(message.channel, "Hotdog :)")
                #yield from self.logout()
            else:
                yield from self.send_message(message.channel, "Not hotdog :(")

loop = asyncio.get_event_loop()
bot = MyClient()
print(loop.run_until_complete(bot.login('melonspoik@gmail.com', 'p4$$w0rd')), "done start")
loop.run_until_complete(bot.connect())
print("Ended")
