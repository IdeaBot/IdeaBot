from libs import command, loader
import requests, traceback, re
from os.path import join

COMMANDS_DIR = './commands'
REACTIONS_DIR = './reactions'

class Command(command.DirectOnlyCommand, command.AdminCommand, command.Multi, command.WatchCommand, command.RoleCommand):
    '''load_command downloads an attached python file and tries to add it as a command

    It will spit back any error trying to download or save the file causes'''

    def matches(self, message):
        return re.search(r'load\s*(command|reaction)\s*(\S+)?\s*(?:from\s*)?(\S+)?', message.content, re.I)!=None

    def action(self, message, send_func, bot):
        args = re.search(r'load\s*(command|reaction)\s*(\S+)?\s*(?:from\s*)?(\S+)?', message.content, re.I)
        parameters = {"user_func":self.user, "role_messages":self.role_messages, "always_watch_messages":self.always_watch_messages}# by the end , it'll look something like this: {filename, namespace, user_func, role_messages, always_watch_messages, package=""}
        try:
            # determine the appropriate filename, name and namespace to init the command/reaction with
            try:
                assert args.group(2)==""
                parameters["filename"]=self.public_namespace.most_recent_download.strip("\\/").replace("/", ".").replace("\\", ".").replace(".commands", "").replace(".reactions", "")
                downloaded = True
            except (AttributeError, AssertionError):
                parameters["filename"] = args.group(2).strip("\\/").replace("/", ".").replace("\\", ".")
                downloaded = False
            name = parameters["filename"].split(".")[-2]
            print(parameters["filename"], name)
            if parameters["filename"]:
                if args.group(3):
                    parameters["package"]=args.group(3)
                    if parameters["package"] in loader.sub_namespaces:
                        parameters["namespace"]=loader.sub_namespaces[parameters["package"]]
                    else:
                        loader.sub_namespaces[parameters["package"]]=loader.CustomNamespace()
                        parameters["namespace"]=loader.sub_namespaces[parameters["package"]]
                elif downloaded and len(parameters["filename"].split("."))>2: # if command is downloaded and is in subfolder (format [<folder>.]<command>.py)
                    filepath = parameters["filename"].split(".")
                    parameters["package"]=filepath[-3] # third last thing; should be first but I'm not going to assume
                    if parameters["package"] in loader.sub_namespaces:
                        parameters["namespace"]=loader.sub_namespaces[parameters["package"]]
                    else:
                        loader.sub_namespaces[parameters["package"]]=loader.CustomNamespace()
                        parameters["namespace"]=loader.sub_namespaces[parameters["package"]]
                else:
                    parameters["namespace"]=loader.namespace
            else:
                raise ImportError("No filename declared. Please provide one in `load command/reaction <filename> [from <folder name>]`")

            # finally actually load the command/reaction
            if args.group(1)=='command': # load command
                if '-f' in message.content:
                    bot.commands[name]=loader.init_command(**parameters, reload=True)
                elif name in bot.commands:
                    raise ImportError('Command by that name already exists. Use "-f" to force the import')
                else:
                    bot.commands[name]=loader.init_command(**parameters)
                bot.commands.move_to_end(name, last=False)
            elif args.group(1)=='reaction': # load reaction
                parameters['all_emojis_func']=bot.get_all_emojis
                parameters['emoji_dir']=loader.emoji_dir
                if '-f' in message.content:
                    bot.reactions[name]=loader.init_reaction(**parameters, reload=True)
                elif name in bot.reactions:
                    raise ImportError('Reaction by that name already exists. Use "-f" to force the import')
                else:
                    bot.reactions[name]=loader.init_reaction(**parameters)
                bot.reactions.move_to_end(name, last=False)
            yield from send_func(message.channel, "Successfully loaded %s" % parameters["filename"])

        except:
            yield from send_func(message.channel, "Is that supposed to happen? \n"+"```"+traceback.format_exc()+"```")
