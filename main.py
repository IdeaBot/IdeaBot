import discord
import logging, time, asyncio, random, sys, configparser
from multiprocessing import Process, Queue

sys.path.append('./libs')
import configloader, scraperff, dataloader, scrapert

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

@asyncio.coroutine
def doChecks():
    '''() -> None
    checks to make sure no messages need to be sent about something special, like scraper updates'''
    while not qForum.empty():
        yield from bot.send_message(bot.forumchannel, qForum.get()[0])
    while not qTwitter.empty():
        tweet = qTwitter.get()
        yield from bot.send_message(bot.twitterchannel, "Idea Project tweeted this: "+ tweet[1] + " (from: <"+tweet[0]+">)")



class DiscordClient(discord.Client): # subClass : overwrites certain functions of discord.Client class
    '''To overwrite functions without modifying the Discord API Python code'''
    @asyncio.coroutine
    def on_ready(self):
        '''() -> None
        logs info when API is ready'''
        #work or die
        log.info("API connection created successfully")
        log.info("Username: " + self.user.name)
        log.info("Email: " + self.email)
        log.info(str([i for i in self.servers]))
        for i in bot.get_all_channels(): # play the matchy-matchy game with server names
            if i.name == channels.content["twitter"]:
                self.twitterchannel = i
                log.info("twitter channel found")
            if i.name == channels.content["forum"]:
                self.forumchannel = i
                log.info("forum channel found")
        yield from self.send_message(self.twitterchannel, "Hello humans...")
        yield from doChecks()

    @asyncio.coroutine
    def on_message(self, message):
        '''(Message class) -> None
        interprets and responds to the message'''
        yield from doChecks()
        if message.author != self.user: # everything past here will eventually become some super string parser
            if "hotdog" in message.content.lower() or "dick" in message.content.lower() or "hot-dog" in message.content.lower():
                yield from self.send_message(message.channel, "Hotdog :)")
                #yield from self.logout()
            else:
                yield from self.send_message(message.channel, "Not hotdog :(")

            if self.user.mention in message.content:
                if "what" in message.content.lower():
                    if " id " in message.content.lower() or message.content[-len(" id"):].lower() == " id":
                        yield from self.send_message(message.channel, message.author.id)

            if message.author.name[:len("ngnius")].lower() == "ngnius" and "shutdown protocol 0" in message.content.lower(): #if ngnius says shutdown
                yield from self.send_message(message.channel, "Goodbye humans...")
                yield from self.logout()
                log.info("Shutdown started by: " + message.author.name)

bot = DiscordClient()

if __name__ == '__main__':
    # main
    # init stuff
    loop = asyncio.get_event_loop()

    credentials = dataloader.datafile("./data/credentials.config")
    credentials.content = credentials.content["DEFAULT"]
    channels = dataloader.datafile("./data/channels.config")
    channels.content = channels.content["DEFAULT"]
    qForum = Queue()
    qTwitter = Queue()
    stop = Queue()
    qTwitter.put(["This is a url", "This is a tweet"])
    forumScraper = Process(target = scraperff.continuousScrape, args = (qForum, stop, ))
    forumScraper.start()
    twitterScraper = Process(target = scrapert.continuousScrape, args = (qTwitter, stop, ))
    twitterScraper.start()
    loop.run_until_complete(bot.login(credentials.content["username"], credentials.content["password"]))

    #run until logged out
    loop.run_until_complete(bot.connect())
    print("Ended")
