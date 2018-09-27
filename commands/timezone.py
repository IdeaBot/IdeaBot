# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 12:35:40 2018

@author: 14flash
"""

from libs import command
import re
from libs import timezones

class Command(command.DirectOnlyCommand):
    '''Time Zone command converts a specified time to the desired timezone and
    responds with a message.

    **Usage:**
    ```@Idea what's <time> <timezone> in <new timezone>?``` '''

    def matches(self, message):
        return re.search(r'\bwhat\'?s?\s+(.*)\s+in\s+([A-Z]{3})', message.content, re.IGNORECASE)

    def action(self, message):
        try:
            time, timezoneTarget = timezones.getConversionParameters(message.content)
            yield from self.send_message(message.channel, time.convertTo(timezoneTarget))
        except TypeError:
            if "-v" in message.content.lower():
                yield from self.send_message(message.channel, "You're missing something; `Missing argument error`")
