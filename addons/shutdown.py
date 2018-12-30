# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 10:57:59 2018

@author: 14flash
"""

from libs import command
from libs import discordstats
import re, time

class Command(command.DirectOnlyCommand, command.AdminCommand):
    '''Shuts the bot down.

You must be a bot admin to use this
Only special developpers are bot admins'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.perms=None

    def matches(self, message):
        return re.search(r'shutdown protocol', message.content, re.IGNORECASE)

    def action(self, message, client):
        if message.author.id in client.ADMINS:
            # client.stop_queue.put("Stopping time!")
            if re.search(r'shutdown protocol 1', message.content, re.IGNORECASE): # basic shutdown with stats
                discordstats.dumpMessages(client, filename="./data/msgdump"+str(time.time())+".csv")
            elif re.search(r'shutdown protocol 0', message.content, re.IGNORECASE): # basic shutdown
                pass
            yield from client.logout()
            raise KeyboardInterrupt
