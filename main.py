import discord
import logging, time, asyncio, random, sys, configparser

sys.path.append('./libs')
import configloader, scraper

def configureDiscordLogging():
    '''() -> None
    set ups discord log so that it outputs to ./discord.log'''
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

def mainLogging():
    '''() -> Logger class
    set ups main log so that it outputs to ./main.log and then returns the log'''
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

class DiscordClient(discord.Client): # subClass : overwrites certain functions of discord.CLient class
    '''To overwrite functions without modifying the Discord API Python code'''
    @asyncio.coroutine
    def on_ready(self):
        '''() -> None
        logs info when API is ready'''
        #work or die
        log.info("API connection created successfully")
        log.info("Useranme: " + self.user.name)
        log.info("Email: " + self.email)
        log.info(self.servers)
        #self.logout()

    @asyncio.coroutine
    def on_message(self, message):
        '''(Message class) -> None
        interprets and responds to the message'''
        if message.author != self.user: # everything past here will eventually become some super string parser
            if "hotdog" in message.content.lower() or "dick" in message.content.lower() or "hot-dog" in message.content.lower():
                yield from self.send_message(message.channel, "Hotdog :)")
                #yield from self.logout()
            else:
                yield from self.send_message(message.channel, "Not hotdog :(")

            if message.author.name[:len("ngnius")].lower() == "ngnius" and "shutdown protocol 0" in message.content.lower(): #if ngnius says shutdown
                yield from self.logout()
                log.info("Shutdown started by: " + message.author.name)

# main
# init stuff
loop = asyncio.get_event_loop()
bot = DiscordClient()
credentials = loadConfig("./data/credentials.txt")
credentials = credentials["DEFAULT"]
loop.run_until_complete(bot.login(credentials["username"], credentials["password"]))

#run until logged out
loop.run_until_complete(bot.connect())
print("Ended")
