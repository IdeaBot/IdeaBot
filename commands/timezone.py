# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 12:35:40 2018

@author: 14flash
"""

from libs import command
import re
from libs import timezones

class Command(command.DirectOnlyCommand):
    '''TimeZoneCommand converts a specified time to the deired timezone and
    responds with a message.'''

    def matches(self, message):
        return re.search(r'\bwhat\'?s?\s+(.*)\s+in\s+([A-Z]{3})', message.content, re.IGNORECASE)

    def action(self, message):
        try:
            time, timezoneTarget = timezones.getConversionParameters(message.content)
            yield from self.send_message(message.channel, time.convertTo(timezoneTarget))
        except TypeError:
            if "-v" in message.content.lower():
                yield from self.send_message(message.channel, "You're missing something; `Missing argument error`")
