# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 12:23:16 2018

@author: 14flash & NGnius
"""

from libs import command
import re

class Command(command.DirectOnlyCommand):
    '''IdCommand responds with the id of the user who called this command.'''

    def matches(self, message):
        return re.search(r'\bwhat(\'s\s*)?(my)?\s+id\b', message.content, re.I)

    def action(self, message, send_func):
        yield from send_func(message.channel, message.author.id)
