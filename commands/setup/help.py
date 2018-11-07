import re
from libs import command, embed

HELP_HELPSTRING = '''
Use this command to show the usage instructions for a command, reaction-command or plugin (ie any add-on).

**Usage:**
```@Idea help <add-on>```
Shows the help information for <add-on>

To get a list of commands/reaction-commands/plugins, use:
```@Idea list (commands/reactions/plugins)``` (respectively)
'''

class Command(command.AdminCommand, command.DirectOnlyCommand):
    def matches(self, message):
        return self.collect_args(message)!=None

    def action(self, message, client):
        send_func = self.send_message
        args = self.collect_args(message)
        response_channel = message.author if '-p' not in message.content else message.channel

        if args == None or not args.group(1):
            help = self.make_help('', HELP_HELPSTRING)
            foot_text = 'Bot maintained by NGnius'
            help.set_footer(text=foot_text)
            yield from send_func(response_channel, embed=help)
            return

        is_reaction = args.group(1) in client.reactions
        is_command = args.group(1) in client.commands
        is_plugin = args.group(1) in client.plugins
        is_two = (is_reaction + is_command + is_plugin) > 1
        has_flag = '-c' in message.content or '-r' in message.content or '-l'
        is_verbose = '-v' in message.content

        if is_two and not has_flag:
            yield from send_func(response_channel, 'Please specify between the reaction, command and plugin with `-r`, `-c` and `-l`, respectively')

        elif (is_command and not is_two) or ('-c' in message.content and is_reaction and is_command):
            help = self.make_help(args.group(1), client.commands[args.group(1)]._help(verbose=is_verbose))
            foot_text = 'Command maintained by '+(yield from client.get_user_info(self.public_namespace.commanders[self.public_namespace.COMMANDS][args.group(1)][self.public_namespace.OWNER])).name
            help.set_footer(text=foot_text)
            yield from send_func(response_channel, embed=help)

        elif (is_reaction and not is_two) or ('-r' in message.content and is_two):
            help = self.make_help(args.group(1), client.reactions[args.group(1)]._help(verbose=is_verbose))
            foot_text = 'Reaction maintained by '+(yield from client.get_user_info(self.public_namespace.commanders[self.public_namespace.REACTIONS][args.group(1)][self.public_namespace.OWNER])).name
            help.set_footer(text=foot_text)
            yield from send_func(response_channel, embed=help)

        elif (is_plugin and not is_two) or ('-l' in message.content and is_two):
            help = self.make_help(args.group(1), client.plugins[args.group(1)]._help(verbose=is_verbose))
            foot_text = 'Plugin maintained by '+(yield from client.get_user_info(self.public_namespace.commanders[self.public_namespace.PLUGINS][args.group(1)][self.public_namespace.OWNER])).name
            help.set_footer(text=foot_text)
            yield from send_func(response_channel, embed=help)

        else:
            yield from send_func(response_channel, 'Command not found')

    def collect_args(self, message):
        return re.search(r'help\s*(?:me\s)?(?:with\s)?(\S+)?', message.content, re.I)

    def make_help(self, name, docstring):
        description = '%s Help\n' % name
        em = embed.create_embed(title=description, description=docstring, colour=0xff00ff)
        return em

    def help(self, *args, verbose=False, **kwargs):
        return HELP_HELPSTRING
