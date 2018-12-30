from libs import command
from addons.pipes.libs import pipe as pipe_class
import re

class Command(command.DirectOnlyCommand):
    '''Delete a pipe you own

**Usage**
```@Idea delete pipe "<name>" ```
Where
**`<name>`** is the name of a pipe you own '''
    def collect_args(self, message):
        return re.search(r'delete\s+pipe\s+(.+)', message.content, re.I)

    def collect_name_args(self, string):
        option1 = re.match(r'\"(.+?)\"', string)
        if option1: return option1
        return re.match(r'([^\s]+)', string) # option2

    def matches(self, msg):
        return self.collect_args(msg) != None

    def action(self, message):
        args = self.collect_args(message)
        pipe_name = self.collect_name_args(args.group(1)).group(1)
        pipe = self.public_namespace.find_pipe_by_name(pipe_name, self.public_namespace.pipes)
        if pipe is None:
            yield from self.send_message(message.channel, 'I\'m sorry, I couldn\'t find `%s`. ' %pipe_name)
            return
        if message.author.id != pipe.owner:
            yield from self.send_message(message.channel, 'I\'m sorry, only the owner of `%s` can delete their pipe. ' %pipe_name)
            return
        self.public_namespace.pipes.remove(pipe)
        yield from self.send_message(message.channel, 'Successfully removed `%s` from existence. RIP' %pipe_name)
