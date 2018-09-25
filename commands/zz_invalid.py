# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 13:44:48 2018

@author: 14flash
"""

INVALID_MESSAGE = "I'm sorry, did you say `KILL ALL HUMANS`?"

from libs import command
# TODO(NGnius): Make this actually run last
class Command(command.DirectOnlyCommand):
    '''InvalidCommand is a catch all for direct commands that didn't work.'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.invalid_message = INVALID_MESSAGE

    def matches(self, message):
        return True

    def action(self, message):
        yield from self.send_message(message.channel, self.invalid_message)
