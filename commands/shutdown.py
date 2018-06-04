# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 10:57:59 2018

@author: 14flash
"""

from libs import command
from libs import discordstats
import re, time

class Command(command.DirectOnlyCommand, command.AdminCommand):
    '''ShutdownCommand shuts the bot down.'''

    def matches(self, message):
        return re.search(r'shutdown protocol', message.content, re.IGNORECASE)

    def action(self, message, send_func, client):
        client.stop_queue.put("Stopping time!")
        if re.search(r'shutdown protocol 1', message.content, re.IGNORECASE): # basic shutdown with stats
            discordstats.dumpMessages(client, filename="./data/msgdump"+str(time.time())+".csv")
        elif re.search(r'shutdown protocol 0', message.content, re.IGNORECASE): # basic shutdown
            pass
        yield from client.logout()
