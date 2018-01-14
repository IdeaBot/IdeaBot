# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 13:44:48 2018

@author: 14flash
"""

from commands import command

class InvalidCommand(command.DirectOnlyCommand):
    '''InvalidCommand is a catch all for direct commands that didn't work.'''
    
    def __init__(self, invalid_message, **kwargs):
        super().__init__(**kwargs)
        self.invalid_message = invalid_message

    def matches(self, message):
        return True

    def action(self, message, send_func):
        yield from send_func(message.channel, self.invalid_message)