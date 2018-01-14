# -*- coding: utf-8 -*-
"""
Bot is the discord bot.
TODO(14flash): Expand the description

Created on Wed Jan 10 20:05:03 2018

@author: 14flash
"""

import discord
import asyncio
from commands import command

from libs import dataloader

DEFAULT = 'DEFAULT'
CHANNEL_LOC = 'channelsloc'

class Bot(discord.Client):
    """TODO: Add description"""
    
    def __init__(self, config, log, checks):
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
        self.plugins = list()
        
    def add_data(self, name, content_from=DEFAULT):
        data_file = dataloader.datafile(self.data_config[name])
        self.data[name] = data_file.content[content_from]
    
    def get_data(self, name, key=None):
        if key:
            return self.data[name][key]
        return self.data[name]
        
    def register_command(self, cmd):
        if not isinstance(cmd, command.Command):
            raise ValueError('Only commands may be registered in Bot::register_command')
        self.commands.append(cmd)
    
    def register_plugin(self, plugin):
        # TODO(14flash): Plugin refactor.
        pass
    
    @asyncio.coroutine
    def on_message(self, message):
        self.checks()
        for cmd in self.commands:
            if cmd._matches(message):
                yield from cmd._action(message, self.send_message)
                # TOOD(14flash): is break necessary? Can this be done per command?
                break
    
    @asyncio.coroutine
    def on_ready(self):
        self.log.info('API connection created successfully')
        self.log.info('Username: ' + str(self.user.name))
        self.log.info('Email: ' + str(self.email))
        self.log.info(str([i for i in self.servers]))
        self.setup_channels()
        yield from self.send_message(self.twitterchannel, "Hello humans...")
        self.checks()
    
    def setup_channels(self):
        for i in self.get_all_channels(): # play the matchy-matchy game with server names
            if i.name == self.get_data(CHANNEL_LOC, 'twitter'):
                self.twitterchannel = i
                self.log.info("twitter channel found")
            if i.name == self.get_data(CHANNEL_LOC, 'forum'):
                self.forumchannel = i
                self.log.info("forum channel found")
            if i.name == self.get_data(CHANNEL_LOC, 'reddit'):
                self.redditchannel = i
                self.log.info("reddit channel found")