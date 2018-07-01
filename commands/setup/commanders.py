import re
from libs import command, dataloader

class Command(command.Multi, command.AdminCommand, command.DirectOnlyCommand):
    def matches(self, message):
        return re.search(r'(?:re)?generate\s+(commanders|command\s+maintainers|import\s+perm(?:ission)?s?)', message.content, re.I) != None

    def action(self, message, send_func, bot):
        commanders2 = dataloader.datafile(self.public_namespace.commandersfile.filename).content

        # ensure all commands are in commanders2
        for name in bot.commands:
            if name not in commanders2[self.public_namespace.COMMANDS]:
                commanders2[self.public_namespace.COMMANDS][name] = "missing"

        for name in bot.reactions:
            if name not in commanders2[self.public_namespace.REACTIONS]:
                commanders2[self.public_namespace.REACTIONS][name] = "missing"

        # merge commanders2 with current commanders, in case something changed
        for type in commanders2: # type is reactions or commands, but this may expand to include plugins eventually
            for name in commanders2[type]: # name is the command's name, determined by the command's filename
                # some verification to make sure keys are declared properly
                if not isinstance(commanders2[type][name], dict):
                    commanders2[type][name] = dict()
                if self.public_namespace.MAINTAINERS not in commanders2[type][name]:
                    commanders2[type][name][self.public_namespace.MAINTAINERS] = list()
                if self.public_namespace.OWNER not in commanders2[type][name]:
                    commanders2[type][name][self.public_namespace.OWNER] = self.public_namespace.DEFAULT_OWNER_ID
                # the merging part
                if name not in self.public_namespace.commanders[type]:
                    self.public_namespace.commanders[type][name] = commanders2[type][name]
                else:
                    # self.public_namespace.commanders is assumed to have the most up to date information
                    # so the owner will not be touched unless it is non-existent
                    if self.public_namespace.OWNER not in self.public_namespace.commanders[type][name]:
                        self.public_namespace.commanders[type][name][self.public_namespace.OWNER] = self.public_namespace.DEFAULT_OWNER_ID
                    self.public_namespace.commanders[type][name][self.public_namespace.MAINTAINERS] = list(set(self.public_namespace.commanders[type][name][self.public_namespace.MAINTAINERS]) + set(commanders2[type][name][self.public_namespace.MAINTAINERS]))

        yield from send_func(message.channel, "Aye aye captain")
        # save file
        self.public_namespace.commandersfile.content = self.public_namespace.commanders
        self.public_namespace.commandersfile.save()
