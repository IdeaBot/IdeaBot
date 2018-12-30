from libs import command
from addons.pipes.libs import pipe as pipe_class
import re

class Command(command.DirectOnlyCommand):
    '''Authorize other people to modify your pipe

**Usage**
```@Idea authorize <user> for pipe "<name>"```
Where
**`<user>`** is the user you want to add (user mention/ping)
**`<name>`** is the name of the pipe you want `<user>` to be able to modify

**Example**
`@Idea authorize @NGnius#1234 for pipe "Sewer"`
authorizes NGnius#1234 to add & remove channels from your Sewer pipe

**NOTE:** By `modify` I mean use `pipe_modify`; for more information, do
```@Idea help pipe_modify```
'''
    def collect_args(self, message):
        return re.search(r'authorize\s+<@\!?(\d{18})>\s+(?:for|to)\s+pipe\s+(.+)', message.content, re.I)

    def collect_name_args(self, string):
        option1 = re.match(r'\"(.+?)\"', string)
        if option1: return option1
        return re.match(r'([^\s]+)', string) # option2

    def matches(self, msg):
        return self.collect_args(msg) != None

    def action(self, message):
        args = self.collect_args(message)
        pipe_name = self.collect_name_args(args.group(2)).group(1)
        pipe = self.public_namespace.find_pipe_by_name(pipe_name, self.public_namespace.pipes)
        if pipe is None:
            yield from self.send_message(message.channel, 'I\'m sorry, I couldn\'t find `%s`. ' %pipe_name)
            return
        if message.author.id != pipe.owner:
            yield from self.send_message(message.channel, 'I\'m sorry, only the owner of `%s` can authorize other people. ' %pipe_name)
            return
        if args.group(1) not in pipe.maintainers and args.group(1)!=pipe.owner:
            pipe.maintainers.append(args.group(1))
        yield from self.send_message(message.channel, '<@!%s> is now authorized to use the %s pipe `%s`! ' %(args.group(1), pipe.perm, pipe.name))
