from libs import command, dataloader, verifyaddon
import re, requests, time, os, traceback, datetime

DEFAULT_PLUGIN_CONFIG='data/default_plugin.config'
TEMP_START = 'data/temp'
COMMAND = 'commands'
REACTION = 'reactions'
PLUGIN = 'plugins'

class Command(command.AdminCommand, command.DirectOnlyCommand):
    '''load command loads a python file from the server and tries to add it as an add-on

    This replaces the now deprecated load_command and download_command commands

    **Usage:**
    ```@Idea load <filepath>```
    where <filepath> is an appropriate filepath for the add-on to be saved to
    Please use forward slashes / to denote the filepath, not back slashes \\

    If an add-on file is attached to the message, the I will verify that it follows
    everything described here: <https://github.com/NGnius/IdeaBot/wiki/Rules-&-Suggestions-for-Good-Add-Ons>

    The Load command is probably restricted to certain users'''

    def matches(self, message):
        args = self.collect_args(message)
        return args != None and args.group(1).count('/')<=2
    def collect_args(self, message):
        return re.search(r'\bload\s*\`?((reactions|commands|plugins)\/[\w\_\/]+(?=\.py))\`?',message.content)

    def action(self, message, bot):
        try:
            # boolean variables to indicate what has to and will be done for loading
            is_reload = False
            is_download = True
            has_config = False
            config_loaded = False
            # if no attachment, try to reload add-on
            if len(message.attachments)==0:
                is_reload = True
                is_download = False
            args = self.collect_args(message)
            # info from command
            addon_type = args.group(2).lower() # either 'reactions', 'commands' or 'plugins'
            name = args.group(1)+'.py' # name of add-on file
            addon_name = name[name.rfind('/')+1:-len('.py')]
            package = name[name.find('/')+1:name.rfind('/')]# package; middle folder (<addon_type>/<middble folder>/<name>) or None

            # if add-on exists, reload it
            if os.path.exists(name):
                is_reload = True
            elif not is_download:
                yield from self.send_message(message.channel, "I can't load a non-existent "+addon_type[:-1])
                return
            elif package!=None and not os.path.exists(os.path.join(addon_type, package)):
                # if package doesn't exist, make it
                os.makedirs(package)

            # check/setup permissions
            '''Add-ons in the main folder of an add-on type have their own
            commander permissions (ie people who can modify the add-on)

            Add-ons in subfolders ("packages") have package-level commander
            permissions (ie all add-ons in a package share permissions) '''
            if package != None:
                type = self.public_namespace.PACKAGES
            else:
                type = addon_type
            if not is_reload and package==None:
                # add-on is new
                self.public_namespace.commanders[type][addon_name]=dict()
                self.public_namespace.commanders[type][addon_name][self.public_namespace.OWNER]=message.author.id
                self.public_namespace.commanders[type][addon_name][self.public_namespace.MAINTAINERS] = list()
            elif not is_reload and package not in self.public_namespace.commanders[self.public_namespace.PACKAGES]:
                # new add-on is in a new package
                self.public_namespace.commanders[type][package]=dict()
                self.public_namespace.commanders[type][package][self.public_namespace.OWNER]=message.author.id
                self.public_namespace.commanders[type][package][self.public_namespace.MAINTAINERS] = list()
            elif package==None and not(self.public_namespace.is_commander(message.author.id, addon_name, type) or message.author.id in bot.ADMINS):
                # add-on already exists and user is missing permissions
                yield from self.send_message(message.channel, "`%s` add-on already exists and you do not have permissions to modify it." % addon_name)
                return
            elif package!=None and not(self.public_namespace.is_commander(message.author.id, package, type) or message.author.id in bot.ADMINS):
                # add-on is in package and user is missing permissions for package
                yield from self.send_message(message.channel, "`%s` package already exists and you do not have permissions to modify it." % package)
                return

            # download new file (if there's one to download)
            if is_download:
                # save file to temp location, for safety before file safety is verified
                index_pyfile = None
                # find python file attachment by file extension '.py'
                for i in range(len(message.attachments)):
                    if message.attachments[i]['filename'].endswith('.py'):
                        index_pyfile=i
                        break
                filename = TEMP_START+str(datetime.datetime.now().isoformat())+'ID'+message.author.id+'.py'
                temp_file = dataloader.newdatafile(filename)
                temp_file.content = [requests.get(message.attachments[index_pyfile]["url"]).text]
                temp_file.save()
                # verification
                try:
                    verifyaddon.verify(filename, addon_type)
                except ImportError as e:
                    if '-v' in message.content:
                        yield from self.send_message(message.channel, "Your add-on failed to pass verification: \n"+"```"+traceback.format_exc()+"```")
                    else:
                        yield from self.send_message(message.channel, "Your add-on failed to pass verification: \n"+"`"+str(e)+"`")
                    return
                # save file to non-temp location
                file = dataloader.newdatafile(name)
                file.content = temp_file.content
                file.save()
                if len(message.attachments)>=2:
                    has_config = True
                    # save config file
                    index_config = None
                    # find config file
                    for i in range(len(message.attachments)):
                        if message.attachments[i]['filename'].endswith('.config'):
                            index_config=i
                            break
                    if index_config==None:
                        config_loaded = False
                    else:
                        config_file = dataloader.newdatafile(name[:-len('.py')]+'.config')
                        config_file.content = [requests.get(message.attachments[index_config]["url"]).text]
                        config_file.save()
                        config_loaded = True
                if addon_type==PLUGIN and config_loaded==False and not os.path.exists(name[:-len('.py')]+'.config'):
                    # config file is required for plugins, so load default
                    config_file = dataloader.newdatafile(name[:-len('.py')]+'.config')
                    config_file.content = dataloader.datafile(DEFAULT_PLUGIN_CONFIG, load_as='text').content
                    config_file.save(save_as='text')
                    config_loaded = True

            # load add-on
            py_filename = name[name.rfind('/')+1:]
            cmd_name = py_filename[:-len('.py')]
            if addon_type==COMMAND:
                bot.load_command(py_filename, cmd_name, package=package, reload=is_reload)
            elif addon_type==REACTION:
                bot.load_reaction(py_filename, cmd_name, package=package, reload=is_reload)
            elif addon_type==PLUGIN:
                bot.load_plugin(py_filename, cmd_name, package=package, reload=is_reload)
            else:
                return
            yield from self.send_message(message.channel, self.get_response(name, is_reload, is_download, has_config, config_loaded))
        except:
            traceback.print_exc()
            yield from self.send_message(message.channel, 'An unexpected error occurred. 🔥 Please 🔥 do 🔥 not 🔥 panic, 🔥 everything 🔥 is 🔥 under 🔥 control 🔥')

    def get_response(self, name, is_reload, is_download, has_config, config_loaded):
        response = 'Successfully '
        if is_download:
            response+='downloaded and '
        if is_reload:
            response+='reloaded '
        else:
            response+='loaded '
        response+='`'+name+'`'
        if has_config or config_loaded:
            response+='\n'
            if has_config and config_loaded:
                response+='Successfully downloaded config file'
            elif has_config and not config_loaded:
                response+='Other file was not loaded'
            elif not has_config and config_loaded:
                response+='Successfully loaded default plugin config'
        return response
