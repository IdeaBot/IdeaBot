# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 12:23:16 2018

@author: 14flash
"""

from commands import command
import re

class IdCommand(command.DirectOnlyCommand):
    '''IdCommand responds with the id of the user who called this command.'''

    def matches(self, message):
        return re.search(r'\bwhat\s+id\b', message.content, re.IGNORECASE)

    def action(self, message, send_func):
        yield from send_func(message.channel, message.author.id)
