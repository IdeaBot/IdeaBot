from libs import command, dataloader, embed
from addons.pipes.libs import pipe
import re

class Command(command.DirectOnlyCommand):
    '''Creates a new pipe

**Usage**
```@Idea create [private/public] [<mode>] [<style>] pipe "<name>" ```
Where
**`<mode>`** is a valid pipe mode (either `one-way` or `two-way` mode)
**`<style>`** is a valid style for piped messages (either `embed` or `simple`(default) mode)
**`<name>`** is the name of the pipe you want to make

**Example**
`@Idea create public embed pipe "Idea Announcements" `
creates a pipe named Idea Announcements which everyone can modify & access, where messages are embedded like links

`@Idea create private one-way embed pipe "Sewer" `
creates a Sewer pipe which will pipe messages from the pipe's original channel to other channels.
The Sewer pipe also makes messages look fancy and only you can access the Sewer, fittingly enough.'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.public_namespace.pipes=pipe.load_pipes()
        self.public_namespace.find_pipe_by_name = find_pipe_by_name

    def shutdown(self):
        pipe.save_pipes(self.public_namespace.pipes)

    def matches(self, message):
        return self.collect_args(message)!=None

    def collect_args(self, message):
        args = re.search(r'(?:create|make|new|plumb)\s+(?:(.+?)\s+)?pipe\s+(.+)', message.content, re.I)
        if args is not None and args.group(1) is not None:
            mode_args = self.collect_mode_args(args.group(1))
            style_args = self.collect_style_args(args.group(1))
            perm_args = self.collect_perm_args(args.group(1))
            if not (mode_args or style_args or perm_args):
                return
        return args

    def collect_mode_args(self, string):
        if string is None:
            return
        return re.search(r'(?:(one|two|1|2)\-?way)', string, re.I)

    def collect_perm_args(self, string):
        if string is None:
            return
        return re.search(r'(private|public)', string, re.I)

    def collect_style_args(self, string):
        if string is None:
            return
        return re.search(r'(default|embed|embeded|embedded|fancy|simple)', string, re.I)

    def collect_name_args(self, string):
        option1 = re.match(r'\"(.+?)\"', string)
        if option1: return option1
        return re.match(r'([^\s]+)', string) # option2

    def action(self, message):
        args = self.collect_args(message)
        mode_args = self.collect_mode_args(args.group(1))
        style_args = self.collect_style_args(args.group(1))
        perm_args = self.collect_perm_args(args.group(1))
        # set up params for Pipe
        name = self.collect_name_args(args.group(2)).group(1)
        # make sure name not already used
        if find_pipe_by_name(name, self.public_namespace.pipes):
            yield from self.send_message(message.channel, 'I\'m sorry, `%s` has been used already.' %name )
            return
        owner = message.author.id
        root_channel = message.channel.id
        # process mode
        if mode_args and mode_args.group(1).lower() in ['1', 'one']:
            mode = pipe.Pipe.ONEWAY
        else:
            mode = pipe.Pipe.TWOWAY
        # process style
        if style_args and style_args.group(1).lower() in ['fancy', 'embed', 'embeded', 'embedded']:
            style = pipe.Pipe.EMBED
        else:
            style = pipe.Pipe.DEFAULT
        # process perm
        if perm_args and perm_args.group(1).lower() in ['private']:
            perm = pipe.Pipe.PRIVATE
        else:
            perm = pipe.Pipe.PUBLIC
        # create new pipe from args
        new_pipe = pipe.Pipe(name=name, root_channel=root_channel, mode=mode, style=style, perm=perm, owner=owner, channels=list(), maintainers=list())
        self.public_namespace.pipes.append(new_pipe)
        yield from self.send_message(message.channel, 'Pipe created')

def find_pipe_by_name(name, pipes):
    for p in pipes:
        if p.name == name:
            return p
