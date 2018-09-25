# -*- coding: utf-8 -*-
"""
Created on Wed May 23 21:56:21 2018

@author: 14flash
"""

from libs import command
import re

class Command(command.Command):

    def matches(self, message):
        return re.search(r'\b(gave\sme|gives\sme|get|gets|got)\scancer\b', message.content, re.I)

    def action(self, message):
        yield from self.send_messsage(message.channel, 'https://i.imgur.com/km8vp8v.png')
