# -*- coding: utf-8 -*-
"""
That's "URL Adder" not "ur ladder"
Created on Sun Jan 14 12:32:50 2018

@author: 14flash
"""

from commands import command
import re

class UrlAdderCommand(command.DirectOnlyCommand):
    '''UrlAdderCommand adds a url to the reddit watch list. URLs in the watch
    list will have updates posted in the discord.'''
    
    def __init__(self, url_adder, **kwargs):
        super().__init__(**kwargs)
        self.url_adder = url_adder
    
    def matches(self, message):
        return self.collect_args(message)
    
    def action(self, message, send_func):
        args_match = self.collect_args(message)
        url = args_match.group(1)
        self.url_adder.put({'action': 'add', 'url': url})
        yield from send_func(message.channel, 'Ok, I\'ll try!')
    
    def collect_args(self, message):
        return re.search(r'\badd\s+`(.+?)`', message.content, re.I)