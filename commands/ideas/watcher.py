from libs import command, dataloader
import re, asyncio, time

FILENAME = 'commands/ideas/last_messages_time.json'

class Command(command.Command):
    '''A command for setting up and maintaining the scrapertidea plugin.

**Usage**
To enable ideas in the current channel:
```enable ideas```

To disable ideas in the current channel:
```disable ideas```

For more information, use
```@Idea help scrapertidea``` '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_last_times(FILENAME)

    def matches(self, message):
        return (message.channel.id in self.public_namespace.last_messages_time) or (self.collect_args(message.content) != None)

    @asyncio.coroutine
    def action(self, message):
        send_func = self.send_message
        args = self.collect_args(message.content)
        if args != None:
            if args.group(1) == 'enable':
                self.public_namespace.last_messages_time[message.channel.id] = time.time()
                yield from send_func(message.channel, 'enabled ideas')
            elif args.group(1) == 'disable':
                if message.channel.id in self.public_namespace.last_messages_time:
                    del(self.public_namespace.last_messages_time[message.channel.id])
                    yield from send_func(message.channel, 'disabled ideas')
        else:
            self.public_namespace.last_messages_time[message.channel.id] = time.time()
        self.save_last_times()

    def load_last_times(self, filename):
        self.last_times_file = dataloader.loadfile_safe(filename) # must be json
        if not isinstance(self.last_times_file.content, dict):
            self.last_times_file.content = dict()
        self.public_namespace.last_messages_time = self.last_times_file.content

    def save_last_times(self):
        self.last_times_file.content = self.public_namespace.last_messages_time
        self.last_times_file.save()

    def collect_args(self, string):
        return re.search(r'\b(enable|disable)\s+ideas?\s*(here|in\s+this\s+channel)?', string, re.I)
