from libs import command, dataloader
import re, random

KARMA_UP_LOC = "karmauploc"
KARMA_DOWN_LOC = "karmadownloc"

class Command(command.Command):
    '''KarmaAdderCommand finds ++ and -- messages and adjusts the karma
appropriately.

**Usage**
To add karma to <word>
```<word> karma++```

To subtract karma from <word>
```<word> karma--``` '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.karma_up_data = dataloader.datafile(self.public_namespace.config[KARMA_UP_LOC]).content
        self.karma_down_data = dataloader.datafile(self.public_namespace.config[KARMA_DOWN_LOC]).content

    def matches(self, message):
        return len(self.collect_args(message)) > 0

    def action(self, message):
        send_func = self.send_message
        args_match = self.collect_args(message)
        for args in args_match:
            entity = args[0]
            if args[1] == '++':
                amount = 1
                base_message = random.choice(self.karma_up_data)
                karma_message = base_message + ' (karma: %d)'
            else:
                amount = -1
                base_message = random.choice(self.karma_down_data)
                karma_message = base_message + ' (karma: %d)'
            new_amount = self.public_namespace.add_karma(entity, amount)
            yield from send_func(message.channel, karma_message % (entity, new_amount))


    def collect_args(self, message):
        # An enitity must be more than 1 character so I can tlak about how
        # great C++ is without the bot going crazy.
        return re.findall(r'(\w{2,})\skarma(\+\+|--)', message.content, re.I)
