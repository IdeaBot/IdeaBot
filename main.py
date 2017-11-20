import discord
import logging, time, asyncio, random, sys, configparser

sys.path.append('./libs')
import configloader, scraper

def configureDiscordLogging():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

def mainLogging():
    logger = logging.getLogger('main')
    handler = logging.FileHandler(filename='main.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    return logger

def loadConfig(filename):
    '''() -> None
    load the config.txt file'''
    config = configparser.ConfigParser()
    config.read(filename)
    return config

configureDiscordLogging()
log = mainLogging()

class MyClient(discord.Client): # subClass : overwrites certain functions of discord.CLient class

    @asyncio.coroutine
    def on_ready(self):
        #work or die
        log.info("API connection created successfully")
        log.info("Useranme: " + self.user.name)
        log.info("Email: " + self.email)
        log.info(self.servers)
        #self.logout()

    @asyncio.coroutine
    def on_message(self, message):
        if message.author != self.user: # everything past here will eventually become some super string parser
            if "hotdog" in message.content.lower() or "dick" in message.content.lower() or "hot-dog" in message.content.lower():
                yield from self.send_message(message.channel, "Hotdog :)")
                #yield from self.logout()
            else:
                yield from self.send_message(message.channel, "Not hotdog :(")

            if message.author.name[:len("ngnius")].lower() == "ngnius" and "shutdown protocol 0" in message.content.lower(): #if ngnius says shutdown
                yield from self.logout()
                log.info("Shutdown started by: " + message.author.name)

loop = asyncio.get_event_loop()
bot = MyClient()
credentials = loadConfig("./data/credentials.txt")
credentials = credentials["DEFAULT"]
loop.run_until_complete(bot.login(credentials["username"], credentials["password"]))
loop.run_until_complete(bot.connect())
print("Ended")
