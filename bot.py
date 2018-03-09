# -*- coding: utf-8 -*-
"""
Bot is the discord bot which is responsible for holding all the state necessary
to initialize and run.

Created on Wed Jan 10 20:05:03 2018

@author: 14flash
"""

import discord
import asyncio
from commands import command
from reactions import reactioncommand

from libs import dataloader, embed

DEFAULT = 'DEFAULT'
CHANNEL_LOC = 'channelsloc'

class Bot(discord.Client):
    '''A Discord client which has config data and a list of commands to try when
    a message is received.'''

    def __init__(self, config, log, checks, stop_queue):
        '''(str, Logger, fun) -> Bot
        config: a string which is the loaction of the base config file
        log: a Logger for dumping info
        checks: a function which checks reddit/forum/twitter for new stuff'''
        super().__init__()
        if not config:
            # TODO: raise some kind of exception
            pass
        self.data_config = dataloader.datafile(config).content[DEFAULT]
        self.log = log
        # TODO(14flash): Plugin refactor, where we won't need a doCheck() func anymore
        self.checks = checks
        self.data = dict()
        self.commands = list()
        self.reaction_add_commands = list()
        self.reaction_remove_commands = list()
        self.plugins = list()
        self.stop_queue=stop_queue

    def add_data(self, name, content_from=DEFAULT):
        '''(str, str) -> None
        Adds configuration data to Bot's data dict. It expects that data_config
        contains an entry for 'name' which points to a file that it can extract
        content from. content_from may be specified to get data other than the
        default.'''
        data_file = dataloader.datafile(self.data_config[name])
        self.data[name] = data_file.content[content_from]

    def get_data(self, name, key=None):
        '''(str, str) -> object
        Returns data from a previously read configuration file.'''
        if key:
            return self.data[name][key]
        return self.data[name]

    def register_command(self, cmd):
        '''(Command) -> None
        Registers a Command for execution when a message is received.'''
        if not isinstance(cmd, command.Command):
            raise ValueError('Only commands may be registered in Bot::register_command')
        self.commands.append(cmd)

    def register_plugin(self, plugin):
        '''(Plugin) -> None
        Registers a Plugin which executes in a separate process'''
        # TODO(14flash): Plugin refactor.
        pass

    def register_reaction_command(self, cmd):
        '''(discord.Client, reactions.Command) -> None
        Registers a reaction command for execution when a message is reacted to'''
        if not (isinstance(cmd, reactioncommand.ReactionAddCommand) or isinstance(cmd, reactioncommand.ReactionRemoveCommand)):
            raise ValueError("Only reaction add/remove commands may be registered in Bot::register_reaction_command")
        if isinstance(cmd, reactioncommand.ReactionAddCommand):
            self.reaction_add_commands.append(cmd)
        if isinstance(cmd, reactioncommand.ReactionRemoveCommand):
            self.reaction_remove_commands.append(cmd)

    @asyncio.coroutine
    def on_message(self, message):
        yield from self.checks(self)
        for cmd in self.commands:
            if cmd._matches(message):
                if isinstance(cmd, command.AdminCommand):
                    yield from cmd._action(message, self.send_message, self)
                else:
                    yield from cmd._action(message, self.send_message)
                # TOOD(14flash): is break necessary? Can this be done per command?
                break

    @asyncio.coroutine
    def on_reaction_add(self, reaction, user):
        for cmd in self.reaction_add_commands:
            if cmd._matches(reaction, user):
                if isinstance(cmd, reactioncommand.AdminReactionAddCommand):
                    yield from cmd._action(reaction, user, self)
                else:
                    yield from cmd._action(reaction, user)
                break

    @asyncio.coroutine
    def on_reaction_remove(self, reaction, user):
        for cmd in self.reaction_remove_commands:
            if cmd._matches(reaction, user):
                if isinstance(cmd, reactioncommand.AdminReactionRemoveCommand):
                    yield from cmd._action(reaction, user, self)
                else:
                    yield from cmd._action(reaction, user)
                break

    @asyncio.coroutine
    def on_ready(self):
        self.log.info('API connection created successfully')
        self.log.info('Username: ' + str(self.user.name))
        self.log.info('Email: ' + str(self.email))
        self.log.info(str([i for i in self.servers]))
        self.setup_channels()
        #yield from self.send_message(self.twitterchannel, 'Hello humans...', embed=embed.create_embed(title="Test", description="Potato"))
        yield from self.checks(self)

    def setup_channels(self):
        '''() -> None
        Convinience fuction for on_ready()'''
        for i in self.get_all_channels(): # play the matchy-matchy game with server names
            if i.name == self.get_data(CHANNEL_LOC, 'twitter'):
                self.twitterchannel = i
                self.log.info('twitter channel found')
            if i.name == self.get_data(CHANNEL_LOC, 'forum'):
                self.forumchannel = i
                self.log.info('forum channel found')
            if i.name == self.get_data(CHANNEL_LOC, 'reddit'):
                self.redditchannel = i
                self.log.info('reddit channel found')
