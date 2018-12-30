# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 13:08:24 2018

@author: 14flash
"""

from libs import command
import re

class Command(command.Command):
    '''Adds an emoji reaction to any message that has
the words "forum post".

This. Is. A. Joke.

**NOTE:** This is a joke command and will probably be removed very soon '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.emoji = r'🥔'

    def matches(self, message):
        return re.search(r'\bforum post\b', message.content, re.IGNORECASE)

    def action(self, message):
        yield from self.add_reaction(message, self.emoji)
