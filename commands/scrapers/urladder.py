# -*- coding: utf-8 -*-
"""
That's "URL Adder" not "ur ladder"
Created on Sun Jan 14 12:32:50 2018

@author: 14flash
"""

from libs import command
import re

class Command(command.DirectOnlyCommand, command.Multi):
    '''UrlAdderCommand adds a url to the reddit watch list. URLs in the watch
    list will have updates posted in the discord.

    **Usage:**
    ```@Idea (add or remove) (reddit, twitter, youtube or freeforum) <url> [<channel id>]``` '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url_adder = self.public_namespace.newRedditThread

    def matches(self, message):
        return self.collect_args(message) != None

    def action(self, message):
        args_match = self.collect_args(message)
        url = args_match.group(3).strip('<>')
        type = args_match.group(2).lower()
        channel = args_match.group(4) if args_match.group(4) else message.channel.id
        params = {'action': args_match.group(1), 'url': url, 'id':url.strip('/').split('/')[-1], 'channel':channel}
        if type == 'reddit':
            self.public_namespace.newRedditThread.put(params)
        elif type == 'twitter':
            self.public_namespace.newTwitterChannel.put(params)
        elif type == 'youtube':
            self.public_namespace.newYTChannel.put(params)
        elif type == 'freeforum' or type=='freeforums':
            self.public_namespace.newProBoardsForum.put(params)
        elif type == 'calendar':
            self.public_namespace.newGCal.put(params)
        if '-v' in message.content:
            yield from self.send_message(message.channel, 'Trying to add `%s`' % params)
        else:
            yield from self.send_message(message.channel, 'Trying to add <%s> ' % url)

    def collect_args(self, message):
        return re.search(r'\b(add|remove)\s+(reddit|twitter|youtube|freeforums?|calendar)\s+(\S+)\s?(\d{18})?', message.content, re.I)
