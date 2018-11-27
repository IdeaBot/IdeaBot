from libs import command
import re

class Command(command.DirectOnlyCommand, command.AdminCommand):
    '''A command for setting emojis for reaction commands
    This works alongside the `emoji_setter` reaction command

    **Usage:**
    ```@Idea emoji -> <reaction-command>```
    where <reaction-command> is a valid reaction-command 

    (Use `@Idea list reactions` to view the list of reaction-commands)'''
    def matches(self, message):
        args = re.search(r'emoji\s?->\s?(\S+)', message.content, re.I)
        return args!=None

    def action(self, message, bot):
        send_func = self.send_message
        args = re.search(r'emoji\s?->\s?(\S+)', message.content, re.I)
        if args.group(1) in bot.reactions and bot.reactions[args.group(1)].emoji!=None:
            reply = yield from send_func(message.channel, "React to this message with the emoji you want to set")
            # self.public_namespace.active_emoji_messages[message.id]=args.group(1)
            self.public_namespace.active_emoji_messages[reply.id]=args.group(1)
            #print(self.public_namespace.active_emoji_messages)
        else:
            if args.group(1) in bot.reactions:
                yield from send_func(message.channel, "I'm sorry, that doesn't let you set an emoji")
            else:
                yield from send_func(message.channel, "I'm sorry, that isn't a valid reaction-command. For a list of valid reaction-commands, use ```@Idea list reactions``` ")
