# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 13:08:24 2018

@author: 14flash
"""

from commands import command
import re

class ForumPostCommand(command.Command):
    """ForumPostCommand adds a :forum_post: reaction to any message that has
    the words "forum post"."""

    def __init__(self, add_reaction_func, emoji, **kwargs):
        super().__init__(**kwargs)
        self.add_reaction = add_reaction_func
        self.emoji = emoji

    def matches(self, message):
        return re.search(r'\bforum post\b', message.content, re.IGNORECASE)

    def action(self, message, send_func):
        yield from self.add_reaction(message, self.emoji)
