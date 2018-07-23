from libs import dataloader, plugin
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

def init_command(filename, namespace, user_func, role_messages, always_watch_messages, package="", reload=False, **kwargs):
    config_end=config.content[CONFIGEND]
    parameters = {'user':user_func, 'namespace':namespace, 'always_watch_messages':always_watch_messages, 'role_messages':role_messages}
    if package:
        package=package+"."
    temp_lib = importlib.import_module("commands."+package+filename[:-len(".py")]) # import command
    if reload: # dumb way to do it, ik
        temp_lib = importlib.reload(temp_lib)
    parameters['perms_loc']=perms_dir+package+filename[:-len(".py")]+".json"
    try:
        parameters['config']=config.content[filename[:-len(".py")]+config_end]
    except KeyError:
        parameters['config']=None
    return temp_lib.Command(**parameters, **kwargs) # init command

def init_reaction(filename, namespace, user_func, role_messages, always_watch_messages, package="", emoji_dir="/", reload=False, **kwargs):
    config_end=config.content[CONFIGEND]
    parameters = {'user':user_func, 'namespace':namespace, 'always_watch_messages':always_watch_messages, 'role_messages':role_messages}
    if package!="":
        package=package+"."
    temp_lib = importlib.import_module("reactions."+package+filename[:-len(".py")]) # import reaction
    if reload: # dumb way to do it, ik
        temp_lib = importlib.reload(temp_lib)
    # add reaction-specific parameters
    parameters['perms_loc']=perms_dir+package+filename[:-len(".py")]+".json"
    parameters['emoji_loc']=emoji_dir+package+filename[:-len(".py")]+".json"
    try:
        parameters['config']=config.content[filename[:-len(".py")]+config_end]
    except KeyError:
        parameters['config']=None
    return temp_lib.Reaction(**parameters, **kwargs) # init reaction

def init_plugin(filename, namespace, bot, folder, package="", reload=False, **kwargs):
    config_end=config.content[CONFIGEND]
    # generate parameters
    events = {plugin.READY:bot.wait_until_ready, plugin.LOGIN:bot.wait_until_login, plugin.MESSAGE:bot.wait_for_message, plugin.REACTION:bot.wait_for_reaction}
    api_methods = {plugin.SEND_MESSAGE:bot.send_message, plugin.EDIT_MESSAGE:bot.edit_message, plugin.ADD_REACTION:bot.add_reaction, plugin.REMOVE_REACTION:bot.remove_reaction, plugin.SEND_TYPING:bot.send_typing, plugin.SEND_FILE:bot.send_file}
    parameters = {'events':events, 'api_methods':api_methods}
    if filename[:-len(".py")]+config_end in config.content:
        parameters['config']=config.content[filename[:-len(".py")]+config_end]
    elif isfile(join(folder, package, filename[:-len(".py")]+'.config')):
        parameters['config']=join(folder, package, filename[:-len(".py")]+'.config')
    else:
        parameters['config']=None
    print(join(folder, package, filename[:-len(".py")]+'.config'))
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

def load_commands(folder, user_func, role_messages, always_watch_messages, url_adder):
    commands = OrderedDict()
    for item in sorted(listdir(folder)):
        if isfile(join(folder, item)):
            if item[-len(".py"):] == ".py" and item[0]!="_":
                log.info("Loading command in %a " % item)
                commands[item[:-len(".py")]]=init_command(item, namespace, user_func, role_messages, always_watch_messages, url_adder=url_adder)
        elif item[0] != "_": # second level
            if item not in sub_namespaces:
                sub_namespaces[item]=CustomNamespace()
            for sub_item in sorted(listdir(join(folder, item))):
                if isfile(join(join(folder, item), sub_item)):
                    if sub_item[-len(".py"):] == ".py" and sub_item[0]!="_":
                        log.info("Loading command in %a " % join(item, sub_item))
                        commands[sub_item[:-len(".py")]]=init_command(sub_item, sub_namespaces[item], user_func, role_messages, always_watch_messages, package=item, url_adder=url_adder)
    return commands

def load_reactions(folder, user_func, role_messages, always_watch_messages, all_emojis_func):
    reactions = OrderedDict()
    for item in sorted(listdir(folder)):
        if isfile(join(folder, item)):
            if item[-len(".py"):] == ".py" and item[0]!="_":
                log.info("Loading reaction in %a " % item)
                reactions[item[:-len(".py")]]=init_reaction(item, namespace, user_func, role_messages, always_watch_messages, all_emojis_func=all_emojis_func, emoji_dir=emoji_dir)
        elif item[0] != "_": # second level
            if item not in sub_namespaces:
                sub_namespaces[item]=CustomNamespace()
            for sub_item in sorted(listdir(join(folder, item))):
                if isfile(join(folder, item, sub_item)):
                    if sub_item[-len(".py"):] == ".py" and sub_item[0]!="_":
                        log.info("Loading reaction in %a " % join(item, sub_item))
                        reactions[sub_item[:-len(".py")]]=init_reaction(sub_item, sub_namespaces[item], user_func, role_messages, always_watch_messages, package=item, all_emojis_func=all_emojis_func, emoji_dir=emoji_dir)
    return reactions

def load_plugins(folder, bot):
    plugins = OrderedDict()
    for item in sorted(listdir(folder)):
        if isfile(join(folder, item)):
            if item[-len(".py"):] == ".py" and item[0]!="_":
                log.info("Loading plugin in %a " % item)
                plugins[item[:-len(".py")]]=init_plugin(item, namespace, bot, folder)
        elif item[0] != "_": # second level
            if item not in sub_namespaces:
                sub_namespaces[item]=CustomNamespace()
            for sub_item in sorted(listdir(join(folder, item))):
                if isfile(join(folder, item, sub_item)):
                    if sub_item[-len(".py"):] == ".py" and sub_item[0]!="_":
                        log.info("Loading plugin in %a " % join(item, sub_item))
                        plugins[sub_item[:-len(".py")]]=init_plugin(sub_item, sub_namespaces[item], bot, folder, package=item)
    return plugins
