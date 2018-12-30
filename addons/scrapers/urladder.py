# -*- coding: utf-8 -*-
"""
That's "URL Adder" not "ur ladder"
Created on Sun Jan 14 12:32:50 2018

@author: 14flash
"""

from libs import command
import re

class Command(command.DirectOnlyCommand):
    '''UrlAdderCommand adds a url to the appropriate scraper watch list.
URLs in the watch list will have updates posted in the current channel or the channel with id <channel id>.

Currently supported sites: reddit, twitter, youtube *channel*, google calendar and freeforum

**Usage**
```@Idea (add/remove) url <url> [<channel id>]```
Where
**`<url>`** is the url to

**Example**
`@Idea add url https://www.youtube.com/channel/UCYO_jab_esuFRV4b17AJtAw`

**NOTE:** YouTube *channels* are supported, but *users* are not. The urls are different'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url_adder = self.public_namespace.newRedditThread

    def matches(self, message):
        return self.collect_args(message) != None

    def action(self, message):
        args_match = self.collect_args(message)
        url = args_match.group(2).strip('<>')
        type = self.determine_type(url)
        channel = args_match.group(3) if args_match.group(3) else message.channel.id
        params = {'action': args_match.group(1), 'url': url, 'id':url.strip('/').split('/')[-1], 'channel':channel}
        action = args_match.group(1).lower()
        if type == 'reddit':
            self.public_namespace.newRedditThread.put(params)
        elif type == 'twitter':
            self.public_namespace.newTwitterChannel.put(params)
        elif type == 'youtube':
            self.public_namespace.newYTChannel.put(params)
        elif type == 'freeforum':
            self.public_namespace.newProBoardsForum.put(params)
        elif type == 'calendar':
            self.public_namespace.newGCal.put(params)
        else:
            yield from self.send_message(message.channel, 'The site for the url provided `%s` is not currently supported. Use ```@Idea help urladder``` to learn more.' % url)
            return
        if '-v' in message.content:
            yield from self.send_message(message.channel, 'Trying to %s `%s`' %(action, params))
        else:
            yield from self.send_message(message.channel, 'Trying to %s <%s> ' %(action, url))

    def collect_args(self, message):
        return re.search(r'\b(add|remove)\s+url\s+(\S+)(?:\s+?(\d{18}))?', message.content, re.I)

    def determine_type(self, url):
        if '.reddit.com/r/' in url:
            return 'reddit'
        elif 'twitter.com/' in url:
            return 'twitter'
        elif 'youtube.com/channel/' in url:
            return 'youtube'
        elif '.freeforums.net/' in url:
            return 'freeforum'
        elif 'calendar.google.com/calendar/embed?src=' in url:
            return 'calendar'
