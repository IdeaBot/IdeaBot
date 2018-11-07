import re
from libs import command, dataloader, loader

class Command(command.AdminCommand, command.DirectOnlyCommand):
    '''A command to generate/update the commanders file and information
    Commanders are the maintainers of an add-on, including the owner of the plugin

    **Usage:**
    ```@Idea generate commanders```

    Commanders is probably restricted to certain users'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.public_namespace.generate_commanders=self.generate_commanders
        self.public_namespace.merge_commanders=self.merge_commanders

    def matches(self, message):
        return re.search(r'(?:re)?generate\s+(commanders|command\s+maintainers|import\s+perm(?:ission)?s?)', message.content, re.I) != None

    def action(self, message, bot):
        send_func = self.send_message
        commanders2 = self.generate_commanders(self, bot)
        self.merge_commanders(commanders2)
        yield from send_func(message.channel, "Aye aye captain")
        # save file
        self.public_namespace.commandersfile.content = self.public_namespace.commanders
        self.public_namespace.commandersfile.save()

    def generate_commanders(self, bot):
        commanders2 = dataloader.datafile(self.public_namespace.commandersfile.filename).content
        if not isinstance(commanders2, dict):
            commanders2 = dict()
            commanders2[self.public_namespace.COMMANDS] = dict()
            commanders2[self.public_namespace.REACTIONS] = dict()
            commanders2[self.public_namespace.PLUGINS] = dict()
            commanders2[self.public_namespace.PACKAGES] = dict()

        # ensure all commands are in commanders2
        if self.public_namespace.COMMANDS not in commanders2:
            commanders2[self.public_namespace.COMMANDS] = dict()
        for name in bot.commands:
            if name not in commanders2[self.public_namespace.COMMANDS]:
                commanders2[self.public_namespace.COMMANDS][name] = "missing"

        # ensure all reactions are in commanders2
        if self.public_namespace.REACTIONS not in commanders2:
            commanders2[self.public_namespace.REACTIONS] = dict()
        for name in bot.reactions:
            if name not in commanders2[self.public_namespace.REACTIONS]:
                commanders2[self.public_namespace.REACTIONS][name] = "missing"

        # ensure all plugins are in commanders2
        if self.public_namespace.PLUGINS not in commanders2:
            commanders2[self.public_namespace.PLUGINS] = dict()
        for name in bot.plugins:
            if name not in commanders2[self.public_namespace.PLUGINS]:
                commanders2[self.public_namespace.PLUGINS][name] = "missing"

        # ensure all packages are in commanders2
        if self.public_namespace.PACKAGES not in commanders2:
            commanders2[self.public_namespace.PACKAGES] = dict()
        for package in loader.sub_namespaces:
            if package not in commanders2[self.public_namespace.PACKAGES]:
                commanders2[self.public_namespace.PACKAGES][package] = "missing"

        return commanders2

    def merge_commanders(self, commanders2):
        '''Merges commanders2 with self.public_namespace.commanders'''
        for type in commanders2: # type is packages, reactions, commands or plugins
            for name in commanders2[type]: # name is the command's name, determined by the command's filename
                # some verification to make sure keys are declared properly
                if not isinstance(commanders2[type][name], dict):
                    commanders2[type][name] = dict()
                if self.public_namespace.MAINTAINERS not in commanders2[type][name]:
                    commanders2[type][name][self.public_namespace.MAINTAINERS] = list()
                if self.public_namespace.OWNER not in commanders2[type][name]:
                    commanders2[type][name][self.public_namespace.OWNER] = self.public_namespace.DEFAULT_OWNER_ID
                # the merging part
                if type not in self.public_namespace.commanders:
                    self.public_namespace.commanders[type]=commanders2[type]
                elif name not in self.public_namespace.commanders[type]:
                    self.public_namespace.commanders[type][name] = commanders2[type][name]
                else:
                    # self.public_namespace.commanders is assumed to have the most up to date information
                    # so the owner will not be touched unless it is non-existent
                    if self.public_namespace.OWNER not in self.public_namespace.commanders[type][name]:
                        self.public_namespace.commanders[type][name][self.public_namespace.OWNER] = self.public_namespace.DEFAULT_OWNER_ID
                    self.public_namespace.commanders[type][name][self.public_namespace.MAINTAINERS] = list(set(self.public_namespace.commanders[type][name][self.public_namespace.MAINTAINERS]) | set(commanders2[type][name][self.public_namespace.MAINTAINERS]))
