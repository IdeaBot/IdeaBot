# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 16:50:26 2018

@author: 14flash
"""

from libs import command
import re
import random

class Command(command.DirectOnlyCommand, command.Config):
    '''Replies with a snarky comment when someone wants one.

**Usage**
Figure it out yourself

Oh, you weren't expecting snark here as well?
Well, you're the one who asked for help with snark; I'm just delivering on what you asked for '''

    def __init__(self, snark_data=None, **kwargs):
        super().__init__(**kwargs)
        self.snark_data = self.config.content

    def matches(self, message):
        return re.search(r'\bsnark\b', message.content, re.IGNORECASE)!=None

    def action(self, message):
        match = re.search(r'\bsnark\s*(\blist\b)?', message.content, re.IGNORECASE)
        if not match:
            return
        if match.group(1):
            yield from self.send_message(message.channel, '``` ' + str(self.snark_data) + ' ```')
            return
        yield from self.send_message(message.channel, random.choice(self.snark_data))
