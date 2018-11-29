# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 10:07:23 2018

@author: 14flash
"""

from libs import command
from libs import discordstats
import re
import sys

evalDictOriginalNameThisIs = {}

class Command(command.DirectOnlyCommand, command.AdminCommand, command.BenchmarkableCommand):
    '''ExecuteCommand tries to execute a passed in piece of code and responds
with the result of the execution.

**Usage**
```@Idea execute `<code>` ```

You probably don't have permissions to run this command '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.perms = None

    def matches(self, message):
        return self.collect_args(message)

    def action(self, message, client):
        send_func = self.send_message
        if message.author.id in client.ADMINS:
            args_match = self.collect_args(message)
            # TODO(14flash): Avoid magic number.
            code = args_match.group(3)
            try:
                result = eval(code)
                if result is None:
                    result = 'Execution completed successfully'
                yield from send_func(message.channel, result)
            except KeyboardInterrupt:
                raise
            except:
                exception = sys.exc_info()
                yield from send_func(message.channel, 'I\'m sure it\'s a feature that your code crashes, right? ' + self.exception_message(exception))

    def collect_args(self, message):
        '''(discord.Message) -> re.MatchObject
        Returns a match for the execute command. Group 3 is the code to be executed.'''
        # tested: https://regexr.com/3j6hc
        return re.search(r'\b(execute|evaluate)\s+(`{1}|`{3})([^`]+)\2', message.content, re.I)

    def exception_message(self, exception):
        '''() -> str
        Returns a message about a raised exception.'''
        return "Your code raised this: " + str(exception[0]).replace("'>", "").replace("<class '", "") + ":" + str(exception[1])

def test(a,b):
    '''(int,int) -> (int)'''
    c = a+b
    return c

def assign(a,b):
    '''(object, object) -> bool
    assigns b value in a global dict to a
    returns True if it creates a new key'''
    global evalDictOriginalNameThisIs
    if a in evalDictOriginalNameThisIs:
        output = False
    else:
        output = True
    evalDictOriginalNameThisIs[a] = b
    return output

def retrieve(a):
    '''(object) -> object
    retrieves a in evalDictOriginalNameThisIs
    Precondition: a must be in evalDictOriginalNameThisIs'''
    return evalDictOriginalNameThisIs[a]
