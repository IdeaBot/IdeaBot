from libs import dataloader, plugin, addon
import importlib, logging
from os import listdir
from os.path import isfile, join
from collections import OrderedDict

EMOJIS_LOCATION = 'emojiloc'
PERMISSIONS_LOCATION = 'permissionsloc'
CONFIGEND = 'configend'

class CustomNamespace:
    '''For creating custom namespaces wherever necessary'''
    pass

log = logging.getLogger('main')
namespace=CustomNamespace()
sub_namespaces=dict()

config = dataloader.datafile("./data/config.config")
config.content = config.content["DEFAULT"]
perms_dir=config.content[PERMISSIONS_LOCATION]
emoji_dir=config.content[EMOJIS_LOCATION]

def init_command(filename, namespace, bot, folder, package="", reload=False, **kwargs):
    config_end=config.content[CONFIGEND]
    events = {addon.READY:bot.wait_until_ready, addon.LOGIN:bot.wait_until_login, addon.MESSAGE:bot.wait_for_message, addon.REACTION:bot.wait_for_reaction}
    api_methods = {addon.SEND_MESSAGE:bot.send_message, addon.EDIT_MESSAGE:bot.edit_message, addon.ADD_REACTION:bot.add_reaction, addon.REMOVE_REACTION:bot.remove_reaction, addon.SEND_TYPING:bot.send_typing, addon.SEND_FILE:bot.send_file}
    parameters = {'user':lambda: bot.user, 'namespace':namespace, 'always_watch_messages':bot.always_watch_messages, 'role_messages':bot.role_messages, 'api_methods':api_methods, 'events':events}
    # find config file
    if filename[:-len(".py")]+config_end in config.content:
        parameters['config']=config.content[filename[:-len(".py")]+config_end]
    elif isfile(join(folder, package, filename[:-len(".py")]+'.config')):
        parameters['config']=join(folder, package, filename[:-len(".py")]+'.config')
    else:
        parameters['config']=None
    if package:
        package=package+"."
    temp_lib = importlib.import_module("commands."+package+filename[:-len(".py")]) # import command
    if reload: # dumb way to do it, ik
        temp_lib = importlib.reload(temp_lib)
    parameters['perms_loc']=perms_dir+'c.'+package+filename[:-len(".py")]+".json"
    return temp_lib.Command(**parameters, **kwargs) # init command

def init_reaction(filename, namespace, bot, folder, package="", emoji_dir="/", reload=False, **kwargs):
    config_end=config.content[CONFIGEND]
    events = {addon.READY:bot.wait_until_ready, addon.LOGIN:bot.wait_until_login, addon.MESSAGE:bot.wait_for_message, addon.REACTION:bot.wait_for_reaction}
    api_methods = {addon.SEND_MESSAGE:bot.send_message, addon.EDIT_MESSAGE:bot.edit_message, addon.ADD_REACTION:bot.add_reaction, addon.REMOVE_REACTION:bot.remove_reaction, addon.SEND_TYPING:bot.send_typing, addon.SEND_FILE:bot.send_file}
    # user_func uses lambda to create a closure on bot. This way when bot.user
    # updates it's available to DirectOnlyCommand's without giving extra info.
    parameters = {'user':lambda: bot.user, 'namespace':namespace, 'always_watch_messages':bot.always_watch_messages, 'role_messages':bot.role_messages, 'api_methods':api_methods, 'events':events, 'all_emojis_func':bot.get_all_emojis}
    # find config file
    if filename[:-len(".py")]+config_end in config.content:
        parameters['config']=config.content[filename[:-len(".py")]+config_end]
    elif isfile(join(folder, package, filename[:-len(".py")]+'.config')):
        parameters['config']=join(folder, package, filename[:-len(".py")]+'.config')
    else:
        parameters['config']=None
    if package!="":
        package=package+"."
    temp_lib = importlib.import_module("reactions."+package+filename[:-len(".py")]) # import reaction
    if reload: # dumb way to do it, ik
        temp_lib = importlib.reload(temp_lib)
    # add reaction-specific parameters
    parameters['perms_loc']=perms_dir+'r.'+package+filename[:-len(".py")]+".json"
    parameters['emoji_loc']=emoji_dir+package+filename[:-len(".py")]+".json"
    return temp_lib.Reaction(**parameters, **kwargs) # init reaction

def init_plugin(filename, namespace, bot, folder, package="", reload=False, **kwargs):
    config_end=config.content[CONFIGEND]
    # generate parameters
    events = {addon.READY:bot.wait_until_ready, addon.LOGIN:bot.wait_until_login, addon.MESSAGE:bot.wait_for_message, addon.REACTION:bot.wait_for_reaction}
    api_methods = {addon.SEND_MESSAGE:bot.send_message, addon.EDIT_MESSAGE:bot.edit_message, addon.ADD_REACTION:bot.add_reaction, addon.REMOVE_REACTION:bot.remove_reaction, addon.SEND_TYPING:bot.send_typing, addon.SEND_FILE:bot.send_file}
    parameters = {'user':lambda: bot.user, 'namespace':namespace, 'events':events, 'api_methods':api_methods}

    # find config file
    if filename[:-len(".py")]+config_end in config.content:
        parameters['config']=config.content[filename[:-len(".py")]+config_end]
    elif isfile(join(folder, package, filename[:-len(".py")]+'.config')):
        parameters['config']=join(folder, package, filename[:-len(".py")]+'.config')
    else:
        parameters['config']=None
    # print(join(folder, package, filename[:-len(".py")]+'.config')) # config filepath
    # import plugin
    if package!="":
        package=package+"."
    temp_lib = importlib.import_module("plugins."+package+filename[:-len(".py")]) # import plugin
    if reload: # dumb way to do it, ik
        temp_lib = importlib.reload(temp_lib)
    # init plugin and return it
    return temp_lib.Plugin(**parameters, **kwargs)

'''All loading functions work similarly
All python files (files ending in .py) will be loaded from the appropriate folder, and any .py file in immediate sub-folder (eg for commands, any python files
in commands/ and any python files in commands/*/, where * can be any folder name).
This means you can "hide" functions by putting them into a deeper folder. Anything starting with an underscore ("_") will also be ignored (folders *and* files).
'''

def load_commands(folder, bot, register=False):
    commands = OrderedDict()
    for item in sorted(listdir(folder)):
        if isfile(join(folder, item)):
            if item[-len(".py"):] == ".py" and item[0]!="_":
                log.info("Loading command in %a " % item)
                if register:
                    commands[item[:-len(".py")]]=bot.load_command(item, item[:-len(".py")], package=None)
                else:
                    bot.register_package(bot.COMMANDS, item, None)
                    commands[item[:-len(".py")]]=init_command(item, namespace, bot, folder)
        elif item[0] != "_": # second level
            if item not in sub_namespaces:
                sub_namespaces[item]=CustomNamespace()
            for sub_item in sorted(listdir(join(folder, item))):
                if isfile(join(join(folder, item), sub_item)):
                    if sub_item[-len(".py"):] == ".py" and sub_item[0]!="_":
                        log.info("Loading command in %a " % join(item, sub_item))
                        if register:
                            commands[item[:-len(".py")]]=bot.load_command(sub_item, sub_item[:-len(".py")], package=item)
                        else:
                            bot.register_package(bot.COMMANDS, sub_item[:-len(".py")], item)
                            commands[sub_item[:-len(".py")]]=init_command(sub_item, sub_namespaces[item], bot, folder, package=item)
    return commands

def load_reactions(folder, bot, register=False):
    reactions = OrderedDict()
    for item in sorted(listdir(folder)):
        if isfile(join(folder, item)):
            if item[-len(".py"):] == ".py" and item[0]!="_":
                log.info("Loading reaction in %a " % item)
                if register:
                    reactions[item[:-len(".py")]]=bot.load_reaction(item, item[:-len(".py")], package=None)
                else:
                    bot.register_package(bot.REACTIONS, item, None)
                    reactions[item[:-len(".py")]]=init_reaction(item, namespace, bot, folder, emoji_dir=emoji_dir)
        elif item[0] != "_": # second level
            if item not in sub_namespaces:
                sub_namespaces[item]=CustomNamespace()
            for sub_item in sorted(listdir(join(folder, item))):
                if isfile(join(folder, item, sub_item)):
                    if sub_item[-len(".py"):] == ".py" and sub_item[0]!="_":
                        log.info("Loading reaction in %a " % join(item, sub_item))
                        if register:
                            reactions[sub_item[:-len(".py")]]=bot.load_reaction(sub_item, sub_item[:-len(".py")], package=item)
                        else:
                            bot.register_package(bot.REACTIONS, sub_item[:-len(".py")], item)
                            reactions[sub_item[:-len(".py")]]=init_reaction(sub_item, sub_namespaces[item], bot, folder, package=item, emoji_dir=emoji_dir)
    return reactions

def load_plugins(folder, bot, register=False):
    plugins = OrderedDict()
    for item in sorted(listdir(folder)):
        if isfile(join(folder, item)):
            if item[-len(".py"):] == ".py" and item[0]!="_":
                log.info("Loading plugin in %a " % item)
                if register:
                    plugins[item[:-len(".py")]]=bot.load_plugin(item, item[:-len(".py")], package=None)
                else:
                    bot.register_package(bot.PLUGINS, item, None)
                    plugins[item[:-len(".py")]]=init_plugin(item, namespace, bot, folder)
        elif item[0] != "_": # second level
            if item not in sub_namespaces:
                sub_namespaces[item]=CustomNamespace()
            for sub_item in sorted(listdir(join(folder, item))):
                if isfile(join(folder, item, sub_item)):
                    if sub_item[-len(".py"):] == ".py" and sub_item[0]!="_":
                        log.info("Loading plugin in %a " % join(item, sub_item))
                        if register:
                            plugins[item[:-len(".py")]]=bot.load_plugin(sub_item, sub_item[:-len(".py")], package=item)
                        else:
                            bot.register_package(bot.PLUGINS, sub_item[:-len(".py")], item)
                            plugins[sub_item[:-len(".py")]]=init_plugin(sub_item, sub_namespaces[item], bot, folder, package=item)
    return plugins
