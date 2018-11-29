# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 19:11:09 2018

@author: Yuhas
"""

from libs import command
import re

class Command(command.DirectOnlyCommand):
    '''Gives information about my features

**Usage**
```@Idea featurelist [-v]```

If you're interested in helping to improve Idea, check out what happens when you include `-v`'''

    MESSAGE = '''
    Got a sweet new idea for Idea? Send it to the devs here:
    <https://discord.gg/gwq2vS7> in #wishlist
    Or create a feature request on GitHub:
    <https://github.com/NGnius/IdeaBot/issues>'''

    MESSAGE_V = MESSAGE+'''

    To learn how to add new features, go here:
    <https://github.com/NGnius/IdeaBot/wiki>
    Contact the devs with your question through the server invite'''

    def matches(self, message):
        return re.search(r'\bfeature\s?(list|request)', message.content, re.I)

    def action(self, message):
        if "-v" in message.content.lower():
            yield from self.send_message(message.channel, self.MESSAGE_V)
        else:
            yield from self.send_message(message.channel, self.MESSAGE)
