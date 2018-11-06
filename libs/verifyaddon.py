from libs import dataloader, plugin, command, reaction
import re, os, importlib
from multiprocessing import Process

COMMAND = 'commands'
REACTION = 'reactions'
PLUGIN = 'plugins'

TEMP_FILE = 'data/temp.py'
PROCESS_TIMEOUT = 10 # max time, in seconds, to wait for the sandboxed checker to complete

def verify(filepath, addon_type):
    ''' (str, str) -> bool

    '''
    file = dataloader.datafile(filepath)
    if addon_type not in (COMMAND, REACTION, PLUGIN):
        raise ValueError('Invalid value for parameter addon_type')
    return is_secure(file.content, addon_type) and follows_rules(file.content, addon_type)

def is_secure(filelines, addon_type):
    ''' (iterable of str, str) -> bool
    Checks to make sure the Add-On is secure

    This applies some conditions before an add-on can be loaded to ensure that add-on
    won't affect the normal operation of Idea'''
    file_no_continues = re.sub(re.compile(r'\\\s+'), '', ''.join(filelines))
    file_no_blanks = re.sub(re.compile(r'\s+'), '', file_no_continues)
    file_only_words = re.sub(re.compile(r'\W+'), '', ''.join(filelines))
    # no accessing credentials.config
    if 'credentialsconfig' in file_only_words:
        raise AddOnSecurityError('Explicit access to credentials.config detected. This is forbidden.')

    results = re.finditer(r'open\(([\w\-\_]+|[\'\"]{1,3}[^\'\"]+[\'\"]{1,3}),([\w\-\_]+|[\'\"]{1,3}[^\'\"]+[\'\"]{1,3})', file_no_blanks)
    for i in results:
        filename, access = get_value_from_match(i.group(1), file_no_blanks), get_value_from_match(i.group(2), file_no_blanks)
        if filename and access:
            # no writing to **.config
            if filename.lower().endswith('.config'):
                # check to make sure not opening **.config with write access
                if 'w' in access.lower():
                    raise AddOnSecurityError('Write access to **.config files detected. This is forbidden. Please use a different filetype to save data.')

            # no access to files outside of data/ and package
            if not ( filename.startswith('data/') or filename.startswith('./data/') or filename.startswith(os.path.join(os.getcwd(), 'data'))\
                or filename.startswith(addon_type+'s/') or filename.startswith('./'+addon_type+'s/') or filename.startswith(os.path.join(os.getcwd(), addon_type+'s/'))):
                raise AddOnSecurityError('Access to files outside of `data/` and `%s` detected. This is forbidden.' % addon_type+'s/')

    # stuff run on import is secure
    # save file to temp file location
    with open(TEMP_FILE, 'w') as file:
        file.write('\n'.join(filelines))
    # --- test import (in seperate thread)---
    # import completes
    # not admin add-on
    # add-on is subclass of base interface (bases: command.Command, reaction.Reaction, etc.)
    test_proc = Process(target=sandboxed_checker, args=(addon_type,))
    test_proc.start()
    test_proc.join(PROCESS_TIMEOUT)
    if test_proc.exitcode != 0:
        raise AddOnSecurityError('Sandboxed import failed. Either there is an error in your code or your addon failed to pass all it\'s checks')
    return True

def follows_rules(filelines, addon_type):
    ''' (iterable of str, str) -> bool
    Checks to make sure the Add-On follows the rules set out

    This applies the rules set forth here:
    https://github.com/NGnius/IdeaBot/wiki/Rules-&-Suggestions-for-Good-Add-Ons
    '''
    file_no_continues = re.sub(re.compile(r'\\\s+'), '', ''.join(filelines))
    file_no_blanks = re.sub(re.compile(r'\s+'), '', file_no_continues)
    file_only_words = re.sub(re.compile(r'\W+'), '', ''.join(filelines))

    results = re.finditer(r'(\S+)\s*\(([\w\-\_]+|[\'\"]{1,3}[^\'\"]+[\'\"]{1,3})', file_no_continues)
    for i in results:
        val = get_value_from_match(i.group(2), file_no_blanks)
        if val != None:
            filename = val.strip()
            # uses relative filepath
            if not (filename.startswith('./') or not filename.startswith('/')):
                raise AddOnRuleError('Non-relative filepath detected. Please always use relative filepaths.')

    # doesn't overwrite wrappers (_action, _matches, etc.)
    # matches() and action() are overwritten (defined)
    inside_class = file_no_blanks[file_no_blanks.find('class'+addon_type.capitalize()):]
    match_str = r'def\_'
    match_matches = re.search(match_str+r'matches\(', file_no_blanks)
    match_action = re.search(match_str+r'action\(', file_no_blanks)
    if match_matches!=None:
        raise AddOnRuleError('Matches wrapper is defined. `_matches` should not be overriden in concrete implementations.')
    if match_action!=None:
        raise AddOnRuleError('Action wrapper is defined. `_action` should not be overriden in concrete implementations.')
    return True

def get_value(variable_name, file_no_blanks):
    result = re.search(variable_name+r'=([\'\"]{1,3}[^\'\"]+[\'\"]{1,3})', file_no_blanks)
    return result.group(1) if result != None else None

def get_value_from_match(match_group, file_no_blanks):
    if (match_group.startswith('\'') or match_group.startswith('\"')) and ( match_group.endswith('\'') or match_group.endswith('\"') ):
        val = match_group.strip('\'\"')
    else:
        val = get_value(match_group, file_no_blanks)

    return val

def sandboxed_checker(addon_type):
    # trial import
    temp_lib = importlib.import_module(TEMP_FILE.strip('/').replace('/', '.')[:-len(".py")])
    # dummy variables
    if addon_type==COMMAND:
        test = temp_lib.Command
        # check addon is subclass of base class and not subclass of admin class
        assert issubclass(test, command.Command) and not issubclass(test, command.AdminCommand)
    elif addon_type==REACTION:
        test = temp_lib.Reaction
        # check addon is subclass of base class and not subclass of admin class
        assert (issubclass(test, reaction.ReactionAddCommand) or issubclass(test, reaction.ReactionRemoveCommand)) and not issubclass(test, reaction.AdminReactionCommand)
    else: # plugin
        test = temp_lib.Plugin
        # check addon is subclass of base class and not subclass of admin class
        assert issubclass(test, plugin.Plugin) and not issubclass(test, plugin.AdminPlugin)

class AddOnSecurityError(ImportError):
    pass

class AddOnRuleError(ImportError):
    pass
