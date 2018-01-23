# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 19:11:09 2018

@author: Yuhas
"""

from commands import command
import re

class FeatureListCommand(command.DirectOnlyCommand):
    
    MESSAGE = (
        'You can see the requested features or add more here: '
        '<http://ideahavers.freeforums.net/thread/74/discord-bot-feature-wishlist> '
        ' or here: '
        '<https://docs.google.com/document/d/1CREz-CWA0GrinAa7d22Q3nfpqj60wywQzJrYCcH1xhU/edit?usp=sharing>'
    )
    
    def matches(self, message):
        return re.search(r'feature\s?(list|request)', message.content, re.I)
    
    def action(self, message, send_func):
        yield from send_func(message.channel, FeatureListCommand.MESSAGE)