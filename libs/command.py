# -*- coding: utf-8 -*-
"""
Command is the definition of the command class as well as extensible utilities
that can be used to create more commands easily.

Created on Thu Jan 11 20:03:56 2018

@author: 14flash
"""

import time
import re
import types

from libs import dataloader, addon

DEFAULT = addon.DEFAULT

class Command(addon.AddOn):
    '''Command represents a command that the discord bot can use to take action
    based on messages posted in any discord channels it listens to.'''

    def __init__(self, perms_loc=None, api_methods=dict(), always_watch_messages=set(), role_messages=dict(), namespace=None, events=dict(), **kwargs):
        '''(str, dict, set, dict, CustomNamespace) -> Command
        perms: string of users who have permission to use this command
        kwargs: included for sub-classing.'''

        # associate API methods
        self.send_message = api_methods[self.SEND_MESSAGE]
        self.edit_message = api_methods[self.EDIT_MESSAGE]
        self.add_reaction = api_methods[self.ADD_REACTION]
        self.remove_reaction = api_methods[self.REMOVE_REACTION]
        self.send_typing = api_methods[self.SEND_TYPING]
        self.send_file = api_methods[self.SEND_FILE]

        self.always_watch_messages=always_watch_messages
        self.role_messages=role_messages
        self.public_namespace = namespace
        self.events = events

        # TODO: more verification on the structure of perms
        try:
            self.perms_file = dataloader.datafile(perms_loc, load_as="json")
            self.perms = self.perms_file.content
        except FileNotFoundError:
            self.perms_file = dataloader.newdatafile(perms_loc)
            self.perms = dict()
        self.breaks_on_match = False

    def _matches(self, message):
        '''(discord.Message) -> bool
        Concrete instances of Command should NOT override this function. This
        is intended to be overriden by sub-classes which provide utility to
        concrete instances (see DirectOnlyCommand as an example).

        Returns true if this command can interpret the message.'''
        return (self.perms is None or message.server is None or message.server.id not in self.perms or message.author.id in self.perms[message.server.id]) and self.matches(message)

    def matches(self, message):
        '''(discord.Message) -> bool
        Returns true if this command can interpret the message.'''
        return False

    def _action(self, message):
        '''(discord.Message, func) -> None
        Concrete instances of Command should NOT override this function. This
        is intended to be overriden by sub-classes which provide utility to
        concrete instances (see BenchmarkableCommand as an example).

        Reacts to a message.'''
        yield from self.action(message)

    def action(self, message):
        '''(discord.Message, func) -> None
        Reacts to a message.'''
        pass

    def _shutdown(self):
        '''(Command) -> None
        Concrete implementations should NOT override this function. Only sub-classes should override this,
        in order to expand or modify it's functionality.

        the method to call shutdown()'''
        if self.perms != None: # save permissions
            self.perms_file.content = self.perms
            self.perms_file.save()
        return self.shutdown()

    def shutdown(self):
        '''(Command) -> None
        This is called during bot shutdown
        Use this to save any variables that need to be loaded again when the bot restarts'''
        pass


class BenchmarkableCommand(Command):
    '''Extending BenchmarkableCommand will make the bot respond with the time
    it took to execute a command if "benchmark" appears in the message.'''

    def _action(self, message):
        # start the benchmark
        start_time = time.perf_counter()
        # do whatever the class's action is
        yield from super()._action(message)
        # report on benchmark if requested
        if re.search(r'\bbenchmark\b', message.content, re.IGNORECASE):
            end_time = time.perf_counter()
            yield from self.send_message(message.channel, 'Executed in ' + str(end_time-start_time) + ' seconds')


class DirectOnlyCommand(Command):
    '''Extending DirectOnlyCommand will make the bot only respond to this
    command if it is mentioned in the message.'''

    # TODO(14flash): try reworking the structure so that user doesn't have to
    # be passed in.
    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        # hypothectically, you could also make this so that it responds if a
        # particular user is @ed, not just the bot
        if user is None or type(user) is not types.FunctionType:
            raise ValueError('DirectOnlyCommand requires a user func to be passed in')
        self.user = user
        self.breaks_on_match = True

    def _matches(self, message):
        mentioned = re.search(r'<@!?'+self.user().id+r'>', message.content, re.I) != None
        return mentioned and super()._matches(message)

class PrivateCommand(Command):
    '''Extending PrivateCommand will make the bot only respond to this
    command if it is sent in a private message to the bot.'''
    def _matches(self, message):
        return message.server == None and super()._matches(message)

class AdminCommand(Command):
    '''Extending AdminCommand will make the command have access to the bot object (discord.Client object)'''

    def _action(self, message, client):
        '''(AdminCommand, discord.Message, func, discord.Client) -> None
        Allows for action() to receive the client object for advanced use '''
        yield from self.action(message, client)

    def action(self, message, client):
        '''(AdminCommand, discord.Message, func, discord.Client) -> None
        Responds to the message with access to discord.Client '''
        pass

class Dummy(Command):
    '''Extending Dummy will make the command a dummy command (ie the command won't do anything)

    Great for setting up the data structure of the public_namespace in Multi'''

    def _matches(self, *args):
        return False

    def _action(self, *args):
        pass

class Config(Command):
    '''Extending Config will make the command "catch" the configuration file for the command in self.config
    The usage of self.config is the same as any other dataloader.datafile class'''

    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        if config:
            try:
                self.config = dataloader.datafile(config) # configuration file for the Command
                if self.config.type=='config':
                    self.config=self.config.content[self.DEFAULT]
            except FileNotFoundError:
                self.config = None # NOTE: This is a bad state for a Config Command to be in, since it will cause unexpected errors
                raise ImportError("No config file found")
        else:
            raise ImportError("Config file cannot be None")
