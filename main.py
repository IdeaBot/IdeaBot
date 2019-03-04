import logging
import asyncio
import traceback

import bot as botlib

from libs import dataloader

import time

MSG_BACKUP_LOCATION = 'msgbackuploc'
WATCH_MSG_LOCATION = 'alwayswatchmsgloc'
ROLE_MSG_LOCATION = 'rolemessagesloc'
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

RESTART_WAIT = 2  # seconds to wait before trying to start the bot again


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
    set ups main log outputing to ./main.log and then returns the log'''
    logger = logging.getLogger('main')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='main.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    return logger


configureDiscordLogging()

if __name__ == '__main__':  # main
    # init stuff
    loop = asyncio.get_event_loop()
    config = dataloader.datafile("./data/config.config")
    config.content = config.content["DEFAULT"]
    _credentials = dataloader.datafile(config.content["credentialsloc"])
    _credentials.content = _credentials.content["DEFAULT"]

    log = mainLogging()

    print("Starting bot...")
    # run until logged out
    _stop = False
    while not _stop:
        try:
            # init bot
            bot = botlib.Bot("./data/config.config", log)
            bot.add_data(botlib.CHANNEL_LOC)
        except Exception as e:
            _stop = True
            print("Bot failed to start due to an error during initialization")
            traceback.print_exc()
            botlib.Bot.cancel_all_tasks(None)
        if not _stop:
            try:
                # log in
                if "token" in _credentials.content:
                    loop.run_until_complete(bot.login(_credentials.content["token"]))
                else:
                    loop.run_until_complete(bot.login(_credentials.content["username"], _credentials.content["password"]))
                # run bot
                loop.run_until_complete(bot.connect())
            except KeyboardInterrupt:
                _stop = True
                print("KeyboardInterrupting outta here")
            except Exception as e:
                print("Something went wrong")
                traceback.print_exc()
            bot._shutdown()
            del(bot)
        if not _stop:
            print("Something tripped up - reconnecting Discord API")
            time.sleep(RESTART_WAIT)

    print("Ended")
