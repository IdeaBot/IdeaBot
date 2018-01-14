# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 16:50:26 2018

@author: Yuhas
"""

from commands import command
import re
import random
from libs import dataloader

class SnarkCommand(command.DirectOnlyCommand):
    
    def __init__(self, snark_data=None, **kwargs):
        super().__init__(**kwargs)
        self.snark_data = snark_data.content
    
    def matches(self, message):
        return re.search(r'\bsnark\b', message.content, re.IGNORECASE)
    
    def action(self, message, send_func):
        match = re.search(r'\bsnark\s*(\blist\b)?', message.content, re.IGNORECASE)
        if not match:
            return
        if match.group(1):
            yield from send_func(message.channel, "``` " + str(self.snark_data) + " ```")
            return
        yield from send_func(message.channel, random.choice(self.snark_data))