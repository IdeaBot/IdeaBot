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

from libs import dataloader

class Command():
    '''Command represents a command that the discord bot can use to take action
    based on messages posted in any discord channels it listens to.'''

    def __init__(self, perms_loc, **kwargs):
        '''(str, dict) -> Command
        perms: string of users who have permission to use this command
        kwargs: included for sub-classing.'''
        # TODO: more verification on the structure of perms
        try:
            self.perms_file = dataloader.datafile(perms_loc, load_as="json")
            self.perms = self.perms_file.content
        except FileNotFoundError:
            self.perms_file = dataloader.newdatafile(perms_loc)
            self.perms = None
        self.breaks_on_match = False

    def _matches(self, message):
        '''(discord.Message) -> bool
        Concrete instances of Command should NOT override this function. This
        is intended to be overriden by sub-classes which provide utility to
        concrete instances (see DirectOnlyCommand as an example).

        Returns true if this command can interpret the message.'''
        return (self.perms is None or message.author.id in self.perms) and self.matches(message)

    def matches(self, message):
        '''(discord.Message) -> bool
        Returns true if this command can interpret the message.'''
        return False

    def _action(self, message, send_func):
        '''(discord.Message, func) -> None
        Concrete instances of Command should NOT override this function. This
        is intended to be overriden by sub-classes which provide utility to
        concrete instances (see BenchmarkableCommand as an example).

        Reacts to a message.'''
        yield from self.action(message, send_func)

    def action(self, message, send_func):
        '''(discord.Message, func) -> None
        Reacts to a message.'''
        pass

    def shutdown(self):
        '''(Command) -> None
        This is called during bot shutdown
        Use this to save any variables that need to be loaded again when the bot restarts'''
        if self.perms != None: # save permissions
            self.perms_file.content = self.perms
            self.perms_file.save()


class BenchmarkableCommand(Command):
    '''Extending BenchmarkableCommand will make the bot respond with the time
    it took to execute a command if "benchmark" appears in the message.'''

    def _action(self, message, send_func):
        # start the benchmark
        start_time = time.time()
        # do whatever the class's action is
        yield from super()._action(message, send_func)
        # report on benchmark if requested
        if re.search(r'\bbenchmark\b', message.content, re.IGNORECASE):
            end_time = time.time()
            yield from send_func(message.channel, 'Executed in ' + str(end_time-start_time) + ' seconds')


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

    def _action(self, message, send_func, client):
        '''(AdminCommand, discord.Message, func, discord.Client) -> None
        Allows for action() to receive the client object for advanced use '''
        yield from self.action(message, send_func, client)

    def action(self, message, send_func, client):
        '''(AdminCommand, discord.Message, func, discord.Client) -> None
        Responds to the message with access to discord.Client '''
        pass

class WatchCommand(Command):
    '''Extending WatchCommand will make it possible for the command
    to add discord.Messages for the bot to always keep track of

    To add a message to the watchlist, use self.always_watch_messages.add(<discord.Message object>)
    self.always_watch_messages is a set()'''

    def __init__(self, always_watch_messages, **kwargs):
        super().__init__(**kwargs)
        self.always_watch_messages=always_watch_messages

class RoleCommand(Command):
    '''Extending RoleCommand will make the command "catch" the role_messages variables'''

    def __init__(self, role_messages, **kwargs):
        super().__init__(**kwargs)
        self.role_messages=role_messages

class Multi(Command):
    '''Extending Multi will make it possible for the command to access the namespace (ie variables) of
    other commands contained in the same folder or within the same folder name (not necessarily the same folder path)'''

    def __init__(self, namespace, **kwargs):
        super().__init__(**kwargs)
        self.public_namespace = namespace

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
            self.config = dataloader.datafile(config)
        else:
            self.config = None
