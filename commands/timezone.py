# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 12:35:40 2018

@author: 14flash
"""

from libs import command
import re
from libs import timezones

class Command(command.DirectOnlyCommand):
    '''Converts a specified time to the desired timezone and responds with a message.

**Usage**
```@Idea what's <time> <timezone> in <new timezone>?```
Where
**`<time>`** is a digital time (##:##)
**`<timezone>`** is a valid timezone (UTC-# or TLA)
**`<new timezone>`** is a valid timezone

**Example**
`@Idea what's 12:00 EST in EDT?`
`@Idea what's 4:00 UTC-1 in UTC+6?` '''

    def matches(self, message):
        return re.search(r'\bwhat\'?s?\s+(.*)\s+in\s+([A-Z]{3})', message.content, re.IGNORECASE)

    def action(self, message):
        try:
            time, timezoneTarget = timezones.getConversionParameters(message.content)
            yield from self.send_message(message.channel, time.convertTo(timezoneTarget))
        except TypeError:
            if "-v" in message.content.lower():
                yield from self.send_message(message.channel, "You're missing something; `Missing argument error`")
