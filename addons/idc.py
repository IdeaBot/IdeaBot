# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 12:23:16 2018

@author: 14flash & NGnius
"""

from libs import command
import re

class Command(command.DirectOnlyCommand):
    '''IdCommand responds with the id of the user who called this command.

**Usage**
```@Idea what's my id```

**NOTE:** This is a debug command, so it may be removed or deprecated without notice in the future'''

    def matches(self, message):
        return re.search(r'\bwhat(\'s\s*)?(my)?\s+id\b', message.content, re.I)

    def action(self, message):
        yield from self.send_message(message.channel, message.author.id)
