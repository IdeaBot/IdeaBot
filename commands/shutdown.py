# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 10:57:59 2018

@author: 14flash
"""

from commands import command
import re

class ShutdownCommand(command.DirectOnlyCommand):
    '''ShutdownCommand shuts the bot down.'''

    def __init__(self, logout_func, **kwargs):
        super().__init__(**kwargs)
        self.logout = logout_func

    def matches(self, message):
        return re.search(r'shutdown protocol 0', message.content, re.IGNORECASE)

    def action(self, message, send_func):
        yield from self.logout()
