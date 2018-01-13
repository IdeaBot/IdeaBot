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

class Bot(discord.Client):
    """TODO: Add description"""
    
    def __init__(self, config):
        super().__init__()
        if not config:
            # TODO: raise some kind of exception
            pass
        self.data_config = dataloader.datafile(config).content[DEFAULT]
        self.data = dict()
        self.commands = list()
        self.plugins = list()
        
    def add_data(self, name, content_from=DEFAULT):
        data_file = dataloader.datafile(self.data_config[name])
        self.data[name] = data_file.content[content_from]
        
    def register_command(self, cmd):
        if not isinstance(cmd, command.Command):
            raise ValueError('Only commands may be registered in Bot::register_command')
        self.commands.append(cmd)
    
    def register_plugin(self, plugin):
        pass
    
    @asyncio.coroutine
    def on_message(self, message):
        for cmd in self.commands:
            if cmd._matches(message):
                yield from cmd._action(message, self.send_message)
                # TOOD(14flash): is break necessary? Can this be done per command?
                break
    
    @asyncio.coroutine
    def on_ready(self):
        # TODO: transfer from main.pu
        pass