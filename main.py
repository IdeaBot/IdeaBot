import discord
import logging, time, asyncio, random, sys, configparser, traceback, importlib
from multiprocessing import Process, Queue
from os import listdir
from os.path import isfile, join

import bot as botlib

from libs import configloader, scraperff, dataloader, scrapert, scraperred, embed, command, reaction, savetome

EMOJIS_LOCATION = 'emojiloc'
PERMISSIONS_LOCATION = 'permissionsloc'
#PERMS_LOCATION = './data/perms.json'
MSG_BACKUP_LOCATION='msgbackuploc'
WATCH_MSG_LOCATION='alwayswatchmsgloc'
ROLE_MSG_LOCATION='rolemessagesloc'
COMMANDS_DIR = './commands'
REACTIONS_DIR = './reactions'
PERMS = 'perms'
COMMAND = 'command'
REACTION = 'reaction'
EMOJIS = 'emojis'
CONFIGEND = 'configend'

EXECUTION_PERM = 'executionperm'
SHUTDOWN_PERM = 'shutdownperm'
MANAGE_VOTE_PERM = 'managevoteperm'
DEV_PERM = 'devperm'
STATISTICS_PERM = 'statsperm'
MANAGE_ROLES_PERM = 'manageroleperm'

FORUM_URL = r"http://ideahavers.freeforums.net/"
TWITTER_URL = r"https://twitter.com/openideaproject"
TWITTER_PROFILE_ICON = r"https://pbs.twimg.com/profile_images/913153081566691328/wDhS7B1w_400x400.jpg"
TWITTER_LOGO = r"https://pbs.twimg.com/profile_images/875087697177567232/Qfy0kRIP_400x400.jpg"
REDDIT_LOGO = r"https://pbs.twimg.com/profile_images/868147475852312577/fjCSPU-a_400x400.jpg" #ignore that this is a Twitter link *whistles innocently*

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
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='main.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    return logger

def matchuser(user):
    '''(str)-> discord.User object
    matches the user, by forum url, with their Discord user'''
    userurl = user["url"]
    if userurl in forumdiscorduser.content:
        for i in bot.get_all_members():
            if i.id == forumdiscorduser.content[userurl]:
                return i

def mentionChain(users):
    '''(list of discord.User object) -> str
    returns a string of all the mentions'''
    output = ""
    for i in users:
        output += i.mention + " "
    return output

def loadConfig(filename):
    '''() -> None
    load the config.txt file'''
    config = configparser.ConfigParser()
    config.read(filename)
    return config

configureDiscordLogging()

def init_command(filename, namespace, package="", **kwargs):
    config_end=bot.data_config[CONFIGEND]
    parameters = {'user':user_func, 'namespace':namespace, 'always_watch_messages':always_watch_messages, 'role_messages':role_messages}
    if package:
        package=package+"."
    temp_lib = importlib.import_module("commands."+package+filename[:-len(".py")])
    parameters['perms_loc']=perms_dir+package+filename[:-len(".py")]+".json"
    try:
        parameters['config']=bot.data_config[filename[:-len(".py")]+config_end]
    except KeyError:
        parameters['config']=None
    return temp_lib.Command(**parameters, **kwargs)

def init_reaction(filename, namespace, package="", emoji_dir="/", **kwargs):
    config_end=bot.data_config[CONFIGEND]
    parameters = {'user':user_func, 'namespace':namespace, 'always_watch_messages':always_watch_messages, 'role_messages':role_messages}
    if package!="":
        package=package+"."
    temp_lib = importlib.import_module("reactions."+package+filename[:-len(".py")])#, ".reactions"+package)
    parameters['perms_loc']=perms_dir+package+filename[:-len(".py")]+".json"
    parameters['emoji_loc']=emoji_dir+package+filename[:-len(".py")]+".json"
    try:
        parameters['config']=bot.data_config[filename[:-len(".py")]+config_end]
    except KeyError:
        parameters['config']=None
    return temp_lib.Reaction(**parameters, **kwargs)

class CustomNamespace:
    '''For creating custom namespaces wherever necessary'''
    pass

@asyncio.coroutine
def doChecks(bot):
    '''(discord.Client) -> None
    checks to make sure no messages need to be sent about something special, like scraper updates'''
    threads = list()
    while not qForum.empty():
        threads.append(qForum.get())
    for thread in threads[::-1]:
        #thread = qForum.get()
        #yield from bot.send_message(bot.forumchannel, "BEEP BOOP. This is a debug msg:"+str(thread[1]))
        users = []
        for i in thread[1]:
            user = matchuser(i)
            if user != None and user not in users:
                users.append(user)
        if len(users)>0:
            yield from bot.send_message(bot.forumchannel, mentionChain(users), embed=embed.create_embed(description="In: "+thread[0], author={"name" : thread[1][-1]["name"], "url" : FORUM_URL+thread[1][-1]["url"], "icon_url" : None}, footer={"text":"Forum", "icon_url":None}))
        else:
            yield from bot.send_message(bot.forumchannel, embed=embed.create_embed(description="In: "+thread[0], author={"name" : thread[1][-1]["name"], "url" : FORUM_URL+thread[1][-1]["url"], "icon_url" : None}, footer={"text":"Forum", "icon_url":None}))
    tweets = list()
    while not qTwitter.empty():
        tweets.append(qTwitter.get())
    for tweet in tweets[::-1]:
        #tweet = qTwitter.get()
        if not tweet["retweet"]:
            yield from bot.send_message(bot.twitterchannel, embed=embed.create_embed(author={"name":tweet["author"], "url":tweet["url"], "icon_url":TWITTER_PROFILE_ICON}, description=tweet["content"], footer={"text":"Twitter", "icon_url":TWITTER_LOGO}))
        else:
            yield from bot.send_message(bot.twitterchannel, embed=embed.create_embed(author={"name":"openideaproject retweeted "+tweet["author"], "url":tweet["url"], "icon_url":TWITTER_PROFILE_ICON}, description=tweet["content"], footer={"text":"Twitter", "icon_url":TWITTER_LOGO}))
    comments = list()
    while not qReddit.empty():
        comments.append(qReddit.get())
    for comment in comments[::-1]:
        #comment = qReddit.get()
        yield from bot.send_message(bot.redditchannel, embed=embed.create_embed(description="A comment has been posted here: " + comment[0] + " (direct link: "+comment[1]+" )", footer={"text":"Reddit", "icon_url":REDDIT_LOGO}))

if __name__ == '__main__':
    # main
    # init stuff
    loop = asyncio.get_event_loop()
    config = dataloader.datafile("./data/config.config")
    config.content = config.content["DEFAULT"]
    credentials = dataloader.datafile(config.content["credentialsloc"])
    credentials.content = credentials.content["DEFAULT"]
    channels = dataloader.datafile(config.content["channelsloc"])
    channels.content = channels.content["DEFAULT"]
    forumdiscorduser = dataloader.datafile(config.content["forumdiscorduserloc"])
    forumdiscorduser.content = forumdiscorduser.content["DEFAULT"]

    log = mainLogging()

    stop = Queue()

    always_watch_messages = {botlib.LOADING_WARNING}

    commands = dict()
    reactions = dict()

    bot = botlib.Bot("./data/config.config", log, doChecks, stop, always_watch_messages)
    bot.add_data(botlib.CHANNEL_LOC)

    # variables that should be accessible to all other commands are declared here

    # user_func uses lambda to create a closure on bot. This way when bot.user
    # updates it's available to DirectOnlyCommand's without giving extra info.
    user_func = lambda: bot.user
    all_emojis_func = bot.get_all_emojis #lambda: bot.get_all_emojis wasn't working predictably
    role_messages = savetome.load_role_messages(config.content[ROLE_MSG_LOCATION], all_emojis_func)

    qForum = Queue()
    qTwitter = Queue()
    qReddit = Queue()
    global qRedditURLAdder
    qRedditURLAdder = Queue()

    # load commands, up to two levels deep (ie in ./commands and in ./commands/*, but no deeper)
    namespace=CustomNamespace()
    sub_namespaces=dict()
    perms_dir=config.content[PERMISSIONS_LOCATION]
    emoji_dir=config.content[EMOJIS_LOCATION]

    for item in sorted(listdir(COMMANDS_DIR)):
        if isfile(join(COMMANDS_DIR, item)):
            if item[-len(".py"):] == ".py" and item[0]!="_":
                log.info("Loading command in %a " % item)
                commands[item[:-len(".py")]]=init_command(item, namespace, url_adder=qRedditURLAdder)
        elif item[0] != "_": # second level
            if item not in sub_namespaces:
                sub_namespaces[item]=CustomNamespace()
            for sub_item in sorted(listdir(join(COMMANDS_DIR, item))):
                if isfile(join(join(COMMANDS_DIR, item), sub_item)):
                    if sub_item[-len(".py"):] == ".py" and sub_item[0]!="_":
                        log.info("Loading command in %a " % join(item, sub_item))
                        commands[sub_item[:-len(".py")]]=init_command(sub_item, sub_namespaces[item], package=item, url_adder=qRedditURLAdder)
    #register commands
    for cmd_name in commands:
        bot.register_command(commands[cmd_name], cmd_name)

    # load reactions, up to two levels deep
    for item in sorted(listdir(REACTIONS_DIR)):
        if isfile(join(REACTIONS_DIR, item)):
            if item[-len(".py"):] == ".py" and item[0]!="_":
                log.info("Loading reaction in %a " % item)
                reactions[item[:-len(".py")]]=init_reaction(item, namespace, all_emojis_func=all_emojis_func, emoji_dir=emoji_dir)
        elif item[0] != "_": # second level
            if item not in sub_namespaces:
                sub_namespaces[item]=CustomNamespace()
            for sub_item in sorted(listdir(join(REACTIONS_DIR, item))):
                if isfile(join(REACTIONS_DIR, item, sub_item)):
                    if sub_item[-len(".py"):] == ".py" and sub_item[0]!="_":
                        log.info("Loading reaction in %a " % join(item, sub_item))
                        reactions[sub_item[:-len(".py")]]=init_reaction(sub_item, sub_namespaces[item], package=item, all_emojis_func=all_emojis_func, emoji_dir=emoji_dir)
    # register reactions
    for cmd_name in reactions:
        bot.register_reaction_command(reactions[cmd_name], cmd_name)

    forumScraper = Process(target = scraperff.continuousScrape, args = (qForum, stop, ))
    forumScraper.start()
    twitterScraper = Process(target = scrapert.continuousScrape, args = (qTwitter, stop, ))
    twitterScraper.start()
    redditScraper = Process(target = scraperred.continuousScrape, args = (qReddit, stop, qRedditURLAdder, ))
    redditScraper.start()

    # bot.register_command(invalid.InvalidCommand(user=user_func, invalid_message=config.content["invalidmessagemessage"]))
    if "token" in credentials.content:
        loop.run_until_complete(bot.login(credentials.content["token"]))
    else:
        loop.run_until_complete(bot.login(credentials.content["username"], credentials.content["password"]))

    #run until logged out
    while stop.empty():
        try:
            loop.run_until_complete(bot.connect())
        except KeyboardInterrupt:
            stop.put("KeyboardInterrupt")
            print("KeyboardInterrupting tf outta here")
        except:
            print("Something went wrong")
            traceback.print_exc()
        if stop.empty():
            print("Something tripped up - reconnecting Discord API")
    '''
    karma_entity_sum = 0
    for key in karma.Karma.karma:
        karma_entity_sum += len(key)
    log.info("karma would take about %d bytes to save" % karma_entity_sum)'''
    # do command shutdown
    for cmd_name in commands:
        commands[cmd_name].shutdown()
    for cmd_name in reactions:
        reactions[cmd_name].shutdown()

    savetome.save_role_messages(config.content[ROLE_MSG_LOCATION], role_messages)
    twitterScraper.join()
    forumScraper.join()
    redditScraper.join()

    print("Ended")
