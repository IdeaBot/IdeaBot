from libs import command
import re

class Command(command.DirectOnlyCommand):
    '''KarmaCountCommand responds to direct queries about an entity's karma.

**Usage**
To get the karma of <word>
```karma count <word>```

To get the top or bottom <number> words
```karma (top/bottom) <number>``` '''

    TOP_MIN = 1
    TOP_MAX = 10
    TOP_DEF = 5

    def matches(self, message):
        return self.collect_args(message)

    def action(self, message):
        send_func = self.send_message
        send_wrapper = lambda text: send_func(message.channel, text)
        args_match = self.collect_args(message)
        if args_match.group(1) == 'count':
            yield from self.count(args_match.group(2), send_wrapper)
        elif args_match.group(1) == 'top':
            yield from self.top(args_match.group(2), send_wrapper)
        elif args_match.group(1) == 'bottom':
            yield from self.bottom(args_match.group(2), send_wrapper)

    def collect_args(self, message):
        # would it be better to just have group 2 be a .* catch all and have
        # each command do a smaller regex?
        return re.search(r'\bkarma\s(count|top|bottom)\b\s?(\w*)', message.content, re.I)

    def count(self, entity, send_func):
        if not entity:
            yield from send_func('What do you want me to count silly human?')
        else:
            amount = self.public_namespace.get_karma(entity)
            yield from send_func('%s has %d karma' % (entity, amount))

    def top(self, num, send_func):
        num = self.parse_and_validate_number(num)
        entities = self.public_namespace.get_top(num)
        yield from send_func('The top %d karma holders are:' % num)
        for entity in entities:
            yield from send_func('%s: %d' % (entity, self.public_namespace.get_karma(entity)))

    def bottom(self, num, send_func):
        num = self.parse_and_validate_number(num)
        entities = self.public_namespace.get_bottom(num)
        yield from send_func('The bottom %d karma holders are:' % num)
        for entity in entities:
            yield from send_func('%s: %d' % (entity, self.public_namespace.get_karma(entity)))

    def parse_and_validate_number(self, num_string):
        if not num_string:
            num = self.TOP_DEF
        else:
            try:
                num = int(num_string)
            except ValueError:
                num = self.TOP_DEF
        if num < self.TOP_MIN:
            num = self.TOP_MIN
        if num > self.TOP_MAX:
            num = self.TOP_MAX
        return num
