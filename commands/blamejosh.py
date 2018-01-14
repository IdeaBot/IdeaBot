# -*- coding: utf-8 -*-
"""
Why does this exist? blame josh ¯\_(ツ)_/¯
Created on Sat Jan 13 13:23:56 2018

@author: 14flash
"""

from commands import command
import re

class BlameJoshCommand(command.Command):
    '''BlameJoshCommand blames josh when anyone says to blame josh.'''

    def matches(self, message):
        return re.search(r'\bblame josh\b', message.content, re.IGNORECASE)

    def action(self, message, send_func):
        yield from send_func(message.channel, 'https://cdn.discordapp.com/attachments/382856950079291395/392398975686279168/unknown.png')
