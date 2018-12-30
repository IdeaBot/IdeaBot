from libs import plugin, embed
import discord, traceback, asyncio
import logging
from os import getcwd

def errorLogging():
    '''() -> Logger class
    set ups main log so that it outputs to errors.log and then returns the log'''
    logger = logging.getLogger('errors')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='errors.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logger.addHandler(handler)
    return logger

log = errorLogging()

class Plugin(plugin.AdminPlugin):
    '''Dummy plugin for modifying the error catching methods of the bot.
    The methods are modified in order to send PMs to the owner of the add-on'''
    def on_client_add(self):
        self.bot.on_command_error=self.on_command_error
        self.bot.on_reaction_add_error=self.bot.on_reaction_remove_error=self.on_reaction_error

    @asyncio.coroutine
    def on_command_error(self, cmd_name, error, message):
        if isinstance(error, discord.DiscordException):
            log.info("Caught discord exception in %s" %cmd_name)
            return
        package = self.get_package(cmd_name, self.bot.COMMANDS)
        if not package:
            type = self.public_namespace.COMMANDS
            name = cmd_name
        else:
            type = self.public_namespace.PACKAGES
            name = package
        if name not in self.public_namespace.commanders[type]:
            commanders2 = self.public_namespace.generate_commanders(self.bot)
            self.public_namespace.merge_commanders(commanders2)
        user_id = self.public_namespace.commanders[type][name][self.public_namespace.OWNER]
        user = discord.utils.find(lambda u: u.id == user_id, self.bot.get_all_members())
        error = ''.join(traceback.format_exc())
        error = error.replace(str(getcwd()), '') # remove root folder leaks on errors
        if user:
            title = '**%s** (command) raised an exception during execution' %cmd_name
            desc = '```'+error+'```'
            desc+= '**message.content**```%s```' %message.content
            footer = {'text':'You are receiving this because your are the registered owner of this %s' %type[:-1], 'icon_url':None}
            em = embed.create_embed(footer=footer, title=title, description=desc, colour=0xff1111)
            try:
                yield from self.send_message(user, embed=em)
            except:
                traceback.print_exc()
                pass

    @asyncio.coroutine
    def on_reaction_error(self, cmd_name, error, reaction, user):
        if isinstance(error, discord.DiscordException):
            log.info("Caught discord exception in %s" %cmd_name)
            return
        package = self.get_package(cmd_name, self.bot.REACTIONS)
        if not package:
            type = self.public_namespace.COMMANDS
            name = cmd_name
        else:
            type = self.public_namespace.PACKAGES
            name = package
        if name not in self.public_namespace.commanders[type]:
            commanders2 = self.public_namespace.generate_commanders(self.bot)
            self.public_namespace.merge_commanders(commanders2)
        user_id = self.public_namespace.commanders[type][name][self.public_namespace.OWNER]
        user = discord.utils.find(lambda u: u.id == user_id, self.bot.get_all_members())
        if user:
            error = ''.join(traceback.format_exc())
            error = error.replace(str(getcwd()), '')
            title = '**%s** (reaction) raised an exception during execution' %cmd_name
            desc = '```'+error+'```'
            footer = {'text':'You are receiving this because you are the registered owner of this %s' %type[:-1], 'icon_url':None}
            em = embed.create_embed(footer=footer, title=title, description=desc, colour=0xff1111)
            try:
                yield from self.send_message(user, embed=em)
            except:
                traceback.print_exc()
                pass

    def get_package(self, cmd_name, addon_type):
        for package in self.bot.packages:
            if cmd_name in self.bot.packages[package][addon_type]:
                return package
