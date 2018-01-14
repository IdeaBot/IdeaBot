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

class Command():
    '''Command represents a command that the discord bot can use to take action
    based on messages posted in any discord channels it listens to.'''

    def __init__(self, perms=None, **kwargs):
        '''(str, dict) -> Command
        perms: string of users who have permission to use this command
        kwargs: included for sub-classing.'''
        # TODO: more verification on the structure of perms
        self.perms = perms

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

    def _matches(self, message):
        mentioned = self.user().mention in message.content
        return mentioned and super()._matches(message)
