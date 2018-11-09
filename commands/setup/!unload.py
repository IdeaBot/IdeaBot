from libs import command, dataloader
import re

DATA_FILE='commanderswap'

class Command(command.DirectOnlyCommand, command.AdminCommand, command.Config):
    '''unload command unloads an add-on from the bot and resets the permissions of the add-on

    **Usage:**
    ```@Idea unload <filepath>```
    where <filepath> is an existing add-on filepath
    Please use forward slashes / to denote the filepath, not back slashes \\

    If the add-on has already been unloaded, this command restores the permissions

    The Unload command is probably restricted to certain users'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commanders_swap = dataloader.loadfile_safe(self.config[DATA_FILE])
        # ensure proper data structure
        if not isinstance(self.commanders_swap.content, dict):
            self.commanders_swap.content = dict()
            self.commanders_swap.content[self.public_namespace.COMMANDS]=dict()
            self.commanders_swap.content[self.public_namespace.REACTIONS]=dict()
            self.commanders_swap.content[self.public_namespace.PLUGINS]=dict()
            self.commanders_swap.content[self.public_namespace.PACKAGES]=dict()
    def shutdown(self):
        self.commanders_swap.save()

    def matches(self, message):
        args = self.collect_args(message)
        return args!=None and args.group(1).count('/')<=2
    def collect_args(self, message):
        return re.search(r'\bunload\s*\`?((reactions|commands|plugins)\/[\w\_\/]+(?=\.py))\`?', message.content)

    def action(self, message, bot):
        args = self.collect_args(message)
        addon_type=args.group(2).lower()
        name = args.group(1)+'.py'
        addon_name = name[name.rfind('/')+1:-len('.py')]
        package = name[name.find('/')+1:name.rfind('/')]
        has_perms = False
        # verify package
        if package == '':
            package = None # no package
        # determine type to check perms for
        if package:
            type = self.public_namespace.PACKAGES
            commanders_name = package
        else:
            type = addon_type
            commanders_name = addon_name

        if commanders_name in self.commanders_swap.content[type]:
            # check perms before restoring permissions
            if message.author.id == self.public_namespace.commanders[type][commanders_name][self.public_namespace.OWNER] or message.author.id in bot.ADMINS:
                # restore permissions
                self.public_namespace.commanders[type][commanders_name]=self.commanders_swap.content[type][commanders_name]
                self.commanders_swap.content[type][commanders_name]=None # change reference to not delete real commanders data
                del(self.commanders_swap.content[type][commanders_name])
                yield from self.send_message(message.channel, 'Restored permissions for the %s %s' %(commanders_name, type))
                self.commanders_swap.save()
                return
            else:
                yield from self.send_message(message.channel, 'You do not have permissions for the %s %s' %(commanders_name, type))
                return
        else: # reset permissions
            # check perms
            if commanders_name in self.public_namespace.commanders[type]:
                # check that add-on exists
                if addon_type==self.public_namespace.COMMANDS and name[:-len('.py')] in bot.commands:
                    pass
                elif addon_type==self.public_namespace.REACTIONS and name[:-len('.py')] in bot.reactions:
                    pass
                elif addon_type==self.public_namespace.PLUGINS and name[:-len('.py')] in bot.plugins:
                    pass
                else:
                    yield from self.send_message(message.channel, '`%s` %s does not exist' %(addon_name[:-len('.py')], type[:-1]) )
                    return
                if message.author.id == self.public_namespace.commanders[type][commanders_name][self.public_namespace.OWNER]:
                    has_perms = True
            else:
                yield from self.send_message(message.channel, '`%s` %s does not exist' %(commanders_name, type[:-1]) )
                return

            if has_perms or message.author.id in bot.ADMINS:
                # reset the permissions to lock out other people from reloading the add-on
                self.commanders_swap.content[type][commanders_name]=self.public_namespace.commanders[type][commanders_name]
                new_commanders = {self.public_namespace.OWNER:message.author.id, self.public_namespace.MAINTAINERS:bot.ADMINS}
                self.public_namespace.commanders[type][commanders_name]=new_commanders
                # unload add-on
                if addon_type==self.public_namespace.COMMANDS:
                    del(bot.commands[addon_name])
                elif addon_type==self.public_namespace.REACTIONS:
                    del(bot.reactions[addon_name])
                elif addon_type==self.public_namespace.PLUGINS:
                    del(bot.plugins[addon_name])
                yield from self.send_message(message.channel, 'Unloaded %s' %addon_name)
                return
            else:
                yield from self.send_message(message.channel, 'You do not have permissions for the %s %s' %(commanders_name, type))
                return
