# -*- coding: utf-8 -*-
"""
That's "URL Adder" not "ur ladder"
Created on Sun Jan 14 12:32:50 2018

@author: 14flash
"""

from libs import command
import re

class Command(command.DirectOnlyCommand):
    '''UrlAdderCommand adds a url to the reddit watch list. URLs in the watch
    list will have updates posted in the discord.

    Currently not implemented!'''
    #TODO: Re-implement

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url_adder = None

    def matches(self, message):
        return False#self.collect_args(message) != None

    def action(self, message):
        args_match = self.collect_args(message)
        url = args_match.group(1)
        self.url_adder.put({'action': 'add', 'url': url})
        yield from self.send_message(message.channel, 'Ok, I\'ll try!')

    def collect_args(self, message):
        return re.search(r'\badd\s+`(.+?)`', message.content, re.I)
