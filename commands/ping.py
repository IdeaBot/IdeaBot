# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 21:19:47 2018

@author: 14flash
"""

from libs import command
import re

class Command(command.DirectOnlyCommand, command.BenchmarkableCommand):
    '''PingCommand is a command that responds to the word "ping" as a quick way
    of checking that the bot is working correctly.'''

    def matches(self, message):
        # match objects have a boolean value, so we can just return
        return re.search(r'\bping\b', message.content, re.IGNORECASE)

    def action(self, message):
        yield from self.send_message(message.channel, "PONG.")
