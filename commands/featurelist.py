# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 19:11:09 2018

@author: Yuhas
"""

from libs import command
import re

class Command(command.DirectOnlyCommand):

    MESSAGE = (
        'You can see the requested features or add more here: '
        '<http://ideahavers.freeforums.net/thread/74/discord-bot-feature-wishlist> '
        ' or here: '
        '<https://docs.google.com/document/d/1CREz-CWA0GrinAa7d22Q3nfpqj60wywQzJrYCcH1xhU/edit?usp=sharing>'
    )

    MESSAGE_V = MESSAGE+(
        ' To learn how to use features, go here: '
        '<https://github.com/NGnius/IdeaBot/wiki> '
        ' or ping `@Bot Dev` with your question or suggestion '

    )

    def matches(self, message):
        return re.search(r'feature\s?(list|request)', message.content, re.I)

    def action(self, message, send_func):
        if "-v" in message.content.lower():
            yield from send_func(message.channel, FeatureListCommand.MESSAGE_V)
        else:
            yield from send_func(message.channel, FeatureListCommand.MESSAGE)
