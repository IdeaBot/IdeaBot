import discord
import logging, time, asyncio, random, sys, configparser
from multiprocessing import Process, Queue
import bot as botlib
from commands import ping
from commands import id
from commands import blamejosh
from commands import timezone
from commands import snark
from commands import execute
from commands import shutdown
from commands import urladder
from commands import forumpost
from commands import invalid
from commands import karma
from commands import featurelist
from commands import advancedvote as advancedvoteC
from commands import retrievequote
from commands import pi as picommand
from commands import statistics
from commands import todo
from commands import roles
from commands import colourroles

from reactions import invalid as invalidreaction
from reactions import retry
from reactions import id as emojid #I'm sorry, I'm not even sure what I did there
from reactions import simplevote
from reactions import quote
from reactions import advancedvote as advancedvoteR
from reactions import pin
from reactions import rolegiver

sys.path.append('./libs')
from libs import configloader, scraperff, dataloader, scrapert, scraperred, embed

EMOJIS_LOCATION = 'emojiloc'
PERMISSIONS_LOCATION = 'permissionsloc'
EXECUTION_PERM = 'executionperm'
SHUTDOWN_PERM = 'shutdownperm'
MANAGE_VOTE_PERM = 'managevoteperm'
DEV_PERM = 'devperm'
STATISTICS_PERM = "statsperm"
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

def convertTime(string):
    '''(str)->str
    does nothing'''
    return "Cheaky bastard"

configureDiscordLogging()

@asyncio.coroutine
def doChecks(bot):
    '''(discord.Client) -> None
    checks to make sure no messages need to be sent about something special, like scraper updates'''
    while not qForum.empty():
        thread = qForum.get()
        #yield from bot.send_message(bot.forumchannel, "BEEP BOOP. This is a debug msg:"+str(thread[1]))
        users = []
        for i in thread[1]:
            user = matchuser(i)
            if user != None and user not in users:
                users.append(user)
        if len(users)>0:
            yield from bot.send_message(bot.forumchannel, mentionChain(users), embed=embed.create_embed(description="In: "+thread[0], author={"name" : thread[1][-1]["name"], "url" : FORUM_URL+thread[1][-1]["url"], "icon_url" : None}, footer={"text":"Forum", "icon_url":None}))
        else:
            yield from bot.send_message(bot.forumchannel, embed=embed.create_embed(description="In: "+thread[0], author={"name" : thread[1][-1]["name"], "url" : FORUM_URL+thread[1][-1]["url"], "icon_url" : None}, footer={"text":"forum", "icon_url":None}))
    while not qTwitter.empty():
        tweet = qTwitter.get()
        yield from bot.send_message(bot.twitterchannel, embed=embed.create_embed(author={"name":"Idea Project", "url":TWITTER_URL, "icon_url":TWITTER_PROFILE_ICON}, description=tweet[1], footer={"text":"Twitter", "icon_url":TWITTER_LOGO}))
    while not qReddit.empty():
        comment = qReddit.get()
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
    perms = dataloader.datafile(config.content["permissionsloc"])
    perms.content = perms.content["DEFAULT"]
    forumdiscorduser = dataloader.datafile(config.content["forumdiscorduserloc"])
    forumdiscorduser.content = forumdiscorduser.content["DEFAULT"]

    log = mainLogging()

    stop = Queue()
    bot = botlib.Bot("./data/config.config", log, doChecks, stop)
    bot.add_data(PERMISSIONS_LOCATION)
    bot.add_data(botlib.CHANNEL_LOC)
    bot.add_data(EMOJIS_LOCATION)
    # user_func uses lambda to create a closure on bot. This way when bot.user
    # updates it's available to DirectOnlyCommand's without giving extra info.
    user_func = lambda: bot.user

    vote_dict=dict()
    ballot=dict()
    role_messages = dict()

    bot.register_command(ping.PingCommand(user=user_func))
    bot.register_command(execute.ExecuteCommand(user=user_func, perms=bot.get_data(PERMISSIONS_LOCATION, EXECUTION_PERM)))
    bot.register_command(shutdown.ShutdownCommand(user=user_func, perms=bot.get_data(PERMISSIONS_LOCATION, SHUTDOWN_PERM), logout_func=bot.logout))
    bot.register_command(id.IdCommand(user=user_func))
    bot.register_command(timezone.TimeZoneCommand(user=user_func))
    snark_data = dataloader.datafile(config.content["snarkloc"])
    bot.register_command(snark.SnarkCommand(user=user_func, snark_data=snark_data))
    bot.register_command(featurelist.FeatureListCommand(user=user_func))
    bot.register_command(blamejosh.BlameJoshCommand())
    emoji = config.content["forumpostemoji"]
    bot.register_command(forumpost.ForumPostCommand(add_reaction_func=bot.add_reaction, emoji=emoji))
    karma_up_data = dataloader.datafile(config.content["karmauploc"])
    karma_down_data = dataloader.datafile(config.content["karmadownloc"])
    bot.register_command(karma.KarmaAdderCommand(karma_up_data=karma_up_data, karma_down_data=karma_down_data))
    bot.register_command(karma.KarmaValueCommand(user=user_func))
    #bot.register_command(privatevote.VoteCommand())
    bot.register_command(advancedvoteC.StartVoteCommand(vote_dict=vote_dict, user=user_func, perms=bot.get_data(PERMISSIONS_LOCATION, MANAGE_VOTE_PERM)))
    bot.register_command(advancedvoteC.EndVoteCommand(vote_dict=vote_dict, user=user_func, perms=bot.get_data(PERMISSIONS_LOCATION, MANAGE_VOTE_PERM)))
    bot.register_command(advancedvoteC.StartBallot(vote_dict=vote_dict, user=user_func, ballots=ballot))
    bot.register_command(retrievequote.DisplayQuote(saveloc=bot.data_config["quotesavedir"]))
    bot.register_command(picommand.PiCommand(bot.data_config["pifile"], user=user_func))
    bot.register_command(statistics.GetStats(user=user_func, perms=bot.get_data(PERMISSIONS_LOCATION, STATISTICS_PERM)))
    bot.register_command(todo.ToDoCommand(user=user_func, saveloc=bot.data_config["todosavedir"]))
    bot.register_command(roles.RolesCommand(role_messages=role_messages))
    bot.register_command(colourroles.CreateColourRoleMessage(role_messages=role_messages, user=user_func, perms=bot.get_data(PERMISSIONS_LOCATION, MANAGE_ROLES_PERM)))
    bot.register_command(colourroles.DeleteColourRoles(user=user_func, perms=bot.get_data(PERMISSIONS_LOCATION, MANAGE_ROLES_PERM)))

    #bot.register_reaction_command(<command>) can go here
    bot.register_reaction_command(retry.RetryCommand(all_emojis_func=bot.get_all_emojis, emoji=bot.get_data(EMOJIS_LOCATION, "retry")))
    bot.register_reaction_command(simplevote.VoteAddReaction(bot.get_data(EMOJIS_LOCATION, "yes_vote"), bot.get_data(EMOJIS_LOCATION, "no_vote"), all_emojis_func=bot.get_all_emojis))
    bot.register_reaction_command(simplevote.VoteRemoveReaction(bot.get_data(EMOJIS_LOCATION, "yes_vote"), bot.get_data(EMOJIS_LOCATION, "no_vote"), all_emojis_func=bot.get_all_emojis))
    bot.register_reaction_command(simplevote.VoteTallyReaction(all_emojis_func=bot.get_all_emojis, emoji=bot.get_data(EMOJIS_LOCATION, "tally_vote"), perms=bot.get_data(PERMISSIONS_LOCATION, MANAGE_VOTE_PERM)))
    bot.register_reaction_command(quote.SaveQuote(saveloc=bot.data_config["quotesavedir"],all_emojis_func=bot.get_all_emojis, emoji=bot.get_data(EMOJIS_LOCATION, "save")))
    bot.register_reaction_command(quote.DisplayQuote(all_emojis_func=bot.get_all_emojis, emoji=bot.get_data(EMOJIS_LOCATION, "quote")))
    bot.register_reaction_command(pin.PinReaction(all_emojis_func=bot.get_all_emojis, emoji=bot.get_data(EMOJIS_LOCATION, "pin")))
    bot.register_reaction_command(advancedvoteR.StartBallot(vote_dict=vote_dict, ballots=ballot, all_emojis_func=bot.get_all_emojis, emoji=bot.get_data(EMOJIS_LOCATION, "vote")))
    bot.register_reaction_command(advancedvoteR.RegisterVote(vote_dict=vote_dict, ballots=ballot))
    bot.register_reaction_command(rolegiver.RoleGiveReaction(all_emojis_func=bot.get_all_emojis, role_messages=role_messages))
    bot.register_reaction_command(rolegiver.RoleRemoveReaction(all_emojis_func=bot.get_all_emojis, role_messages=role_messages))
    bot.register_reaction_command(rolegiver.RoleMessageCreate(role_messages=role_messages, all_emojis_func=bot.get_all_emojis, emoji=bot.get_data(EMOJIS_LOCATION, "rolemessagecreate"), perms=bot.get_data(PERMISSIONS_LOCATION, MANAGE_ROLES_PERM)))


    qForum = Queue()
    qTwitter = Queue()
    qReddit = Queue()
    global qRedditURLAdder
    qRedditURLAdder = Queue()

    bot.register_reaction_command(emojid.IdCommand(perms=bot.get_data(PERMISSIONS_LOCATION, DEV_PERM)))
    bot.register_reaction_command(invalidreaction.InvalidCommand())
    bot.register_command(urladder.UrlAdderCommand(user=user_func, url_adder=qRedditURLAdder))

    forumScraper = Process(target = scraperff.continuousScrape, args = (qForum, stop, ))
    forumScraper.start()
    twitterScraper = Process(target = scrapert.continuousScrape, args = (qTwitter, stop, ))
    twitterScraper.start()
    redditScraper = Process(target = scraperred.continuousScrape, args = (qReddit, stop, qRedditURLAdder, ))
    redditScraper.start()

    bot.register_command(invalid.InvalidCommand(user=user_func, invalid_message=config.content["invalidmessagemessage"]))
    if "token" in credentials.content:
        loop.run_until_complete(bot.login(credentials.content["token"]))
    else:
        loop.run_until_complete(bot.login(credentials.content["username"], credentials.content["password"]))
    #print(timezones.FullTime(timezones.SimpleTime("12pm"), timezones.Timezone("EST")).convertTo("CHUT"))
    #run until logged out
    while stop.empty():
        try:
            loop.run_until_complete(bot.connect())
        except KeyboardInterrupt:
            stop.put("KeyboardInterrupt")
        except:
            exception = sys.exc_info()
            print("Something went wrong", str(exception[0]).replace("'>", "").replace("<class '", "") + ":" + str(exception[1]))
        if stop.empty():
            print("Something tripped up - reconnecting Discord API")

    karma_entity_sum = 0
    for key in karma.Karma.karma:
        karma_entity_sum += len(key)
    log.info("karma would take about %d bytes to save" % karma_entity_sum)

    twitterScraper.join()
    forumScraper.join()
    redditScraper.join()

    print("Ended")
