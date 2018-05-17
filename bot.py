# -*- coding: utf-8 -*-
"""
Bot is the discord bot which is responsible for holding all the state necessary
to initialize and run.

Created on Wed Jan 10 20:05:03 2018

@author: 14flash and NGnius
"""

import discord
import asyncio
from commands import command
from reactions import reactioncommand

from libs import dataloader, embed

DEFAULT = 'DEFAULT'
CHANNEL_LOC = 'channelsloc'
MSG_BACKUP_LOCATION='msgbackuploc'
WATCH_MSG_LOCATION='alwayswatchmsgloc'
LOADING_WARNING = "Things are loading"

class Bot(discord.Client):
    '''A Discord client which has config data and a list of commands to try when
    a message is received.'''

    def __init__(self, config, log, checks, stop_queue, always_watch_messages):
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
        self.always_watch_messages=always_watch_messages

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
        yield from self.message_stuff()
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
        self.log.info('Connected to %s servers' %len(self.servers))
        self.setup_channels()
        yield from self.load_messages()
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

    @asyncio.coroutine
    def load_messages(self):
        '''() -> None
        Convenience function for loading the messages the bot might need from before it's last restart'''
        #load messages from file
        self.always_watch_messages.add(LOADING_WARNING)
        messagefile = dataloader.datafile(self.data_config[MSG_BACKUP_LOCATION])
        self.log.info("Loading %a messages" % len(messagefile.content))
        for msg_str in messagefile.content:
            channel_id, msg_id = msg_str.strip().split(":")
            try:
                msg = yield from self.get_message_properly(channel_id, msg_id)
                if msg.server: # PATCH: private messages can't be loaded properly, this prevents them from being used
                    self.messages.append(msg)
            except discord.NotFound:
                self.log.warning("Unable to find %a message" % msg_id)

        #load always_watch_messages from file
        watchfile = dataloader.datafile(self.data_config[WATCH_MSG_LOCATION])
        self.log.info("Loading %a watched messages" % len(watchfile.content))
        for msg_str in watchfile.content:
            channel_id, msg_id = msg_str.strip().split(":")
            try:
                msg = yield from self.get_message_properly(channel_id, msg_id)
                if msg.server: # PATCH: private messages can't be loaded properly, this prevents them from being used
                    if msg not in self.messages:
                        self.messages.append(msg)
                    self.always_watch_messages.add(msg)
            except discord.NotFound:
                self.log.warning("Unable to find %a message" % msg_id)
        self.always_watch_messages.remove(LOADING_WARNING)


    @asyncio.coroutine
    def get_message_properly(self, channel_id, msg_id):
        '''(Bot, str, str) -> discord.Message
        retrieves a message with id msg_id from channel_id which has (most) variables properly defined
        unlike the API's darn annoying default thing that doesn't set anything that I didn't already know arrrg!!'''
        msg = yield from self.get_message(discord.Object(channel_id), msg_id)
        # get_message returns a discord.Message which is lacking a certain variables, including .server and .channel
        # match private channel to msg
        for channel in self.private_channels: # NOTE: private_channels is not loaded at startup, so it will contain nothing initially
            print(channel.id==channel_id)
            if channel.id == channel_id:
                msg.server = None
                msg.channel = channel
                break
        # match server to msg
        for server in self.servers:
            for channel in server.channels:
                if channel.id == channel_id:
                    msg.server = server
                    msg.channel = channel
                    break
        return msg

    @asyncio.coroutine
    def message_stuff(self):
        '''(Bot) -> None
        Convenience function for calling save_messages(), save_always_watched_messages() and sync_always_watched() in one line'''
        self.save_messages()
        self.save_always_watched_messages()
        self.sync_always_watched()

    def save_messages(self):
        '''(Bot) -> None
        backup self.messages deque'''
        if LOADING_WARNING not in self.always_watch_messages: # if not still loading messages (likely from startup)
            messagefile = dataloader.newdatafile(dataloader.datafile("./data/config.config").content["DEFAULT"][MSG_BACKUP_LOCATION])
            for msg in self.messages:
                messagefile.content.append(msg.channel.id + ":" + msg.id)
            messagefile.save()
            self.log.info("Saved %a messages" % len(messagefile.content))
        else:
            self.log.info("Messages are still being loaded, skipping save messages")

    def save_always_watched_messages(self):
        '''(Bot) -> None
        backup self.always_watch_messages set'''
        if LOADING_WARNING not in self.always_watch_messages: # if not still loading messages (likely from startup)
            watchfile = dataloader.newdatafile(dataloader.datafile("./data/config.config").content["DEFAULT"][WATCH_MSG_LOCATION])
            for msg in self.always_watch_messages:
                watchfile.content.append(msg.channel.id + ":" + msg.id)
            watchfile.save()
            self.log.info("Saved %a watched messages" % len(watchfile.content))
        else:
            self.log.info("Messages are still being loaded, skipping save always watched messages")

    def sync_always_watched(self):
        '''(Bot) -> None
        ensure self.messages contains all the necessary messages in the watch list'''
        for msg in self.always_watch_messages:
            if msg not in self.messages:
                self.messages.append(msg)
