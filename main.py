import logging, asyncio, traceback

import bot as botlib

from libs import dataloader, embed, command, reaction, savetome, loader

MSG_BACKUP_LOCATION='msgbackuploc'
WATCH_MSG_LOCATION='alwayswatchmsgloc'
ROLE_MSG_LOCATION='rolemessagesloc'
COMMANDS_DIR = './commands'
REACTIONS_DIR = './reactions'
PLUGINS_DIR = './plugins'
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

def configureDiscordLogging():
    '''() -> None
    set ups discord log so that it outputs to ./discord.log'''
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

def mainLogging():
    '''() -> Logger class
    set ups main log so that it outputs to ./main.log and then returns the log'''
    logger = logging.getLogger('main')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='main.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    return logger

configureDiscordLogging()

if __name__ == '__main__':
    # main
    # init stuff
    loop = asyncio.get_event_loop()
    config = dataloader.datafile("./data/config.config")
    config.content = config.content["DEFAULT"]
    credentials = dataloader.datafile(config.content["credentialsloc"])
    credentials.content = credentials.content["DEFAULT"]

    log = mainLogging()

    always_watch_messages = {botlib.LOADING_WARNING} # set

    print("Initializing bot...")
    bot = botlib.Bot("./data/config.config", log, always_watch_messages)
    bot.add_data(botlib.CHANNEL_LOC)

    # user_func uses lambda to create a closure on bot. This way when bot.user
    # updates it's available to DirectOnlyCommand's without giving extra info.
    user_func = lambda: bot.user
    all_emojis_func = bot.get_all_emojis #lambda: bot.get_all_emojis wasn't working predictably
    role_messages = savetome.load_role_messages(config.content[ROLE_MSG_LOCATION], all_emojis_func)
    bot.role_messages = role_messages

    # load commands, up to two levels deep (ie in ./commands and in ./commands/*, but no deeper)
    commands = loader.load_commands(COMMANDS_DIR, bot, role_messages, always_watch_messages)
    #register commands
    for cmd_name in commands:
        bot.register_command(commands[cmd_name], cmd_name)

    # load reactions, up to two levels deep
    reactions = loader.load_reactions(REACTIONS_DIR, bot, role_messages, always_watch_messages, all_emojis_func)
    # register reactions
    for cmd_name in reactions:
        bot.register_reaction_command(reactions[cmd_name], cmd_name)

    # load plugins, up to two levels deep
    plugins = loader.load_plugins(PLUGINS_DIR, bot)
    # register plugins
    for plugin_name in plugins:
        bot.register_plugin(plugins[plugin_name], plugin_name)

    if "token" in credentials.content:
        loop.run_until_complete(bot.login(credentials.content["token"]))
    else:
        loop.run_until_complete(bot.login(credentials.content["username"], credentials.content["password"]))

    #run until logged out
    stop = False
    while not stop:
        try:
            loop.run_until_complete(bot.connect())
        except KeyboardInterrupt:
            stop = True
            print("KeyboardInterrupting tf outta here")
        except:
            print("Something went wrong")
            traceback.print_exc()
        if not stop:
            print("Something tripped up - reconnecting Discord API")

    # do command shutdown
    for cmd_name in bot.commands:
        bot.commands[cmd_name]._shutdown()
    for cmd_name in bot.reactions:
        bot.reactions[cmd_name]._shutdown()
    for cmd_name in bot.plugins:
        bot.plugins[cmd_name]._shutdown()

    savetome.save_role_messages(config.content[ROLE_MSG_LOCATION], role_messages)

    print("Ended")
