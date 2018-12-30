from libs import command
from addons.pipes.libs import pipe as pipe_class
import re

class Command(command.DirectOnlyCommand):
    '''Modify pipes by adding & removing channels

**Usage**
```@Idea add [<channel>] to pipe "<name>"```
```@Idea remove [<channel>] from pipe "<name>"```
Where
**`<channel>`** is the channel you want to add or remove (optional)
**`<name>`** is the name of the pipe you want to add or remove `channel` from

**Example**
`@Idea add #broadcasts to pipe "Idea Announcements"`
adds #broadcasts to the Idea Announcements pipe

`@Idea remove #bot-testing from pipe "Sewer"`
removes #bot-testing from the Sewer pipe
'''
    def matches(self, message):
        return self.collect_args(message) != None

    def action(self, message):
        args = self.collect_args(message)
        pipe_name = self.collect_name_args(args.group(3)).group(1)
        pipe = self.public_namespace.find_pipe_by_name(pipe_name, self.public_namespace.pipes)
        if pipe is None:
            yield from self.send_message(message.channel, 'I\'m sorry, I couldn\'t find `%s`. ' %pipe_name)
            return
        if pipe.perm==pipe_class.Pipe.PRIVATE and message.author.id != pipe.owner and message.author.id not in pipe.maintainers:
            yield from self.send_message(message.channel, 'I\'m sorry, only the owner or maintainers of `%s` can modify this pipe. ' %pipe_name)
            return
        # determine action
        if args.group(1).lower() in ['connect', 'add', 'append']:
            _action = 'add'
        else:
            _action = 'remove'
        # process channel
        if args.group(2) is None or args.group(2).lower() in ['this']:
            channel_id = message.channel.id
        else:
            channel_id = args.group(2)[2:-1]
        # add/remove from pipe appropriately
        if _action == 'add':
            if channel_id not in pipe.channels and channel_id!=pipe.root_channel:
                pipe.channels.append(channel_id)
            else:
                yield from self.send_message(message.channel, 'I\'m sorry, <#%s> is already a channel in %s' %(channel_id, pipe_name) )
                return
        elif _action == 'remove':
            if channel_id in pipe.channels:
                pipe.channels.remove(channel_id)
            else:
                yield from self.send_message(message.channel, 'I\'m sorry, <#%s> is not a removable channel in %s' %(channel_id, pipe_name) )
                return
        yield from self.send_message(message.channel, 'Successfully %sed <#%s> from/to %s' %(_action, channel_id, pipe_name) )

    def collect_args(self, message):
        return re.search(r'(connect|append|add|remove|delete)\s+(?:(this|\<\#(?:\d{18})\>)\s+)?(?:to|from)\s+pipe\s+(.+)', message.content, re.I)

    def collect_name_args(self, string):
        option1 = re.match(r'\"(.+?)\"', string)
        if option1: return option1
        return re.match(r'([^\s]+)', string) # option2
