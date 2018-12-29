from libs import command
import discord, asyncio

class Command(command.Command):
    '''Pipes messages around Discord

**Usage**
1. Create a pipe
```@Idea create pipe "<name>" ```
Where
**`<name>`** is the name of the pipe you want to make

For more info on creating pipes, do
```@Idea help pipe_create ```

2. Add another side to your pipe
```@Idea add <channel> to pipe "<name>" ```
Where
**`<channel>`** is a channel mention
**`<name>`** is the name of the pipe you just made in step 1

For more info on modifying pipes, do
```@Idea help pipe_modify ```

3. ???

4. Profit

Also check out help information for `pipe_delete` and `pipe_authorize` commands for more pipe functionality

**NOTE:** The piper command does not do anything on it's own. It relies on the rest of the pipes command package '''
    def matches(self, message):
        if message.server is None:
            return False
        if message.server.me.id == message.author.id:
            return False
        for pipe in self.public_namespace.pipes:
            # print(pipe.getAllStartChannels())
            if message.channel.id in pipe.getAllStartChannels():
                return True
        return False

    def action(self, message):
        for pipe in self.public_namespace.pipes:
            if message.channel.id in pipe.getAllStartChannels():
                args, kwargs = pipe.gen_message(message)
                for channel_id in pipe.getOtherChannelIds(message.channel.id):
                    channel = discord.Object(id=channel_id)
                    yield from self.send_message(channel, *args, **kwargs)
