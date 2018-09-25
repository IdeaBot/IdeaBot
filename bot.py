# -*- coding: utf-8 -*-
"""
Bot is the discord bot which is responsible for holding all the state necessary
to initialize and run.

Created on Wed Jan 10 20:05:03 2018

@author: 14flash and NGnius
"""

import discord
import asyncio
import traceback

from libs import dataloader, embed, command, savetome, plugin
from libs import reaction as reactioncommand
from collections import OrderedDict

DEFAULT = 'DEFAULT'
CHANNEL_LOC = 'channelsloc'
MSG_BACKUP_LOCATION='msgbackuploc'
WATCH_MSG_LOCATION='alwayswatchmsgloc'
ROLE_MSG_LOCATION='rolemessagesloc'
LOADING_WARNING = "Things are loading"
ADMINS = ["106537989684887552", "255041793417019393"]

class Bot(discord.Client):
    '''A Discord client which has config data and a list of commands to try when
    a message is received.'''

    CHANNEL_LOC = 'channelsloc'
    MSG_BACKUP_LOCATION='msgbackuploc'
    WATCH_MSG_LOCATION='alwayswatchmsgloc'
    ROLE_MSG_LOCATION='rolemessagesloc'

    def __init__(self, config, log, always_watch_messages):
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
        self.data = dict()
        self.commands = OrderedDict() # maps names to commands
        self.reactions = OrderedDict() # maps names to reaction commands
        self.plugins = OrderedDict() # maps names to plugins
        self.always_watch_messages=always_watch_messages
        self.ADMINS = ADMINS
        self.role_messages=dict()

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

    def register_command(self, cmd, name):
        '''(Command) -> None
        Registers a Command for execution when a message is received.'''
        if not isinstance(cmd, command.Command):
            raise ValueError('Only commands may be registered in Bot::register_command')
        self.commands[name]=cmd

    def register_plugin(self, plugin_object, name):
        '''(Plugin) -> None
        Registers a Plugin which executes in a separate process'''
        if not isinstance(plugin_object, plugin.Plugin):
            raise ValueError('Only plugins may be registered in Bot::register_plugin')
        if isinstance(plugin_object, plugin.AdminPlugin): # give AdminPlugins access to all this class's variables
            plugin_object.add_client_variable(self)
        self.plugins[name]=plugin_object
        self.loop.create_task(plugin_object._action())

    def register_reaction_command(self, cmd, name):
        '''(discord.Client, reactions.Command) -> None
        Registers a reaction command for execution when a message is reacted to'''
        if not (isinstance(cmd, reactioncommand.ReactionAddCommand) or isinstance(cmd, reactioncommand.ReactionRemoveCommand) or isinstance(cmd, reactioncommand.Dummy)):
            raise ValueError("%s is not a reaction command. Only reaction add/remove commands may be registered in Bot::register_reaction_command" % name)
        self.reactions[name]=cmd
    @asyncio.coroutine
    def on_message(self, message):
        yield from self.message_stuff()
        for cmd in self.commands:
            try:
                if self.commands[cmd]._matches(message):
                    if isinstance(self.commands[cmd], command.AdminCommand):
                        yield from self.commands[cmd]._action(message, self)
                    else:
                        yield from self.commands[cmd]._action(message)
                    if self.commands[cmd].breaks_on_match:
                        break
            except Exception as e:
                # Catch all problems that happen in matching/executing a command.
                # This means that if there's a bug that would cause execution to
                # break, other commands can still be tried.
                traceback.print_exc()
                self.log.warning('command %s raised an exception during its execution: %s', cmd, e)

    @asyncio.coroutine
    def on_reaction_add(self, reaction, user):
        for cmd in self.reactions:
            if isinstance(self.reactions[cmd], reactioncommand.ReactionAddCommand) and self.reactions[cmd]._matches(reaction, user):
                if isinstance(self.reactions[cmd], reactioncommand.AdminReactionCommand):
                    yield from self.reactions[cmd]._action(reaction, user, self)
                else:
                    yield from self.reactions[cmd]._action(reaction, user)
                break

    @asyncio.coroutine
    def on_reaction_remove(self, reaction, user):
        for cmd in self.reactions:
            if isinstance(self.reactions[cmd], reactioncommand.ReactionRemoveCommand) and self.reactions[cmd]._matches(reaction, user):
                if isinstance(self.reactions[cmd], reactioncommand.AdminReactionCommand):
                    yield from self.reactions[cmd]._action(reaction, user, self)
                else:
                    yield from self.reactions[cmd]._action(reaction, user)
                break

    @asyncio.coroutine
    def on_ready(self):
        print("Bot online & running startup (this may take a while)")
        self.log.info('API connection created successfully')
        self.log.info('Username: ' + str(self.user.name))
        #self.log.info('Email: ' + str(self.email))
        self.log.info('Connected to %s servers' %len(self.servers))
        yield from self.load_messages()
        print("All messages loaded. Full functionality enabled")

    def load_messages(self):
        '''() -> None
        Convenience function for loading the messages the bot might need from before it's last restart'''
        #load messages from file
        self.always_watch_messages.add(LOADING_WARNING)
        try:
            messagefile = dataloader.datafile(self.data_config[MSG_BACKUP_LOCATION])
        except FileNotFoundError:
            messagefile = dataloader.newdatafile(self.data_config[MSG_BACKUP_LOCATION])
            messagefile.content = list()

        self.log.info("Loading %a messages" % len(messagefile.content))
        for msg_str in messagefile.content:
            channel_id, msg_id = msg_str.strip().split(":")
            try:
                msg = yield from self.get_message_properly(channel_id, msg_id)
                if msg.server: # PATCH: private messages can't be loaded properly, this prevents them from being used
                    self.messages.append(msg)
            except (discord.NotFound, discord.Forbidden, discord.InvalidArgument):
                self.log.warning("Unable to load %a message" % msg_id)
        self.log.info("Finished loading messages")

        #load always_watch_messages from file
        try:
            watchfile = dataloader.datafile(self.data_config[WATCH_MSG_LOCATION])
        except FileNotFoundError:
            watchfile = dataloader.newdatafile(self.data_config[WATCH_MSG_LOCATION])
            watchfile.content = list()

        self.log.info("Loading %a watched messages" % len(watchfile.content))
        for msg_str in watchfile.content:
            channel_id, msg_id = msg_str.strip().split(":")
            try:
                msg = yield from self.get_message_properly(channel_id, msg_id)
                if msg.server: # PATCH: private messages can't be loaded properly, this prevents them from being used
                    if msg not in self.messages:
                        self.messages.append(msg)
                    self.always_watch_messages.add(msg)
            except (discord.NotFound, discord.Forbidden, discord.InvalidArgument):
                # prevents the following, respectively: msg deleted/not-accessible, bot permissions changed, malformed save file
                self.log.warning("Unable to load %a message" % msg_id)
        self.always_watch_messages.remove(LOADING_WARNING)
        self.log.info("Finished loading watched messages")


    @asyncio.coroutine
    def get_message_properly(self, channel_id, msg_id):
        '''(Bot, str, str) -> discord.Message
        retrieves a message with id msg_id from channel_id which has (most) variables properly defined
        unlike the API's darn annoying default thing that doesn't set anything that I didn't already know arrrg!!'''
        msg = yield from self.get_message(discord.Object(channel_id), msg_id)
        # get_message returns a discord.Message which is lacking a certain variables, including .server and .channel
        # match private channel to msg
        for channel in self.private_channels: # NOTE: private_channels is not loaded at startup, so it will contain nothing initially
            # NOTE: private_channels is loaded when you send a message, though, to make things weirder
            # print(channel.id==channel_id)
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
        if isinstance(msg, str):
            print("What the fuck", msg_id)
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
            # self.log.info("Saved %a messages" % len(messagefile.content))
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
            # self.log.info("Saved %a watched messages" % len(watchfile.content))
        else:
            self.log.info("Messages are still being loaded, skipping save always watched messages")

    def sync_always_watched(self):
        '''(Bot) -> None
        ensure self.messages contains all the necessary messages in the watch list'''
        for msg in self.always_watch_messages:
            if msg not in self.messages and msg!=LOADING_WARNING:
                self.messages.append(msg)
