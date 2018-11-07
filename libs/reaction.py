"""
ReactionCommand is the definition of the reaction command class as well as extensible
utility reaction command classes which can be used to make concrete reaction commands

This is very similar to regular (message) commands, except for the input
is a reaction (reaction.message is equivalent to message in message command) and
a user (the person who added/removed/updated the reaction)
"""

from libs import dataloader, addon

DEFAULT = addon.DEFAULT

class ReactionCommand(addon.AddOn):
    '''ReactionAddCommand represents a command that the bot can use to take action
    based on reactions added to any discord message it listens to.'''

    def __init__(self, api_methods=dict(), all_emojis_func=None, emoji_loc=None, perms_loc=None, always_watch_messages=set(), role_messages=dict(), namespace=None, events=dict(), **kwargs):
        '''(ReactionCommand, func, str, dict) -> Command
        perms: str of users who have permission to use this command
        kwargs: included for sub-classing'''
        # associate API methods
        self.send_message = api_methods[self.SEND_MESSAGE]
        self.edit_message = api_methods[self.EDIT_MESSAGE]
        self.add_reaction = api_methods[self.ADD_REACTION]
        self.remove_reaction = api_methods[self.REMOVE_REACTION]
        self.send_typing = api_methods[self.SEND_TYPING]
        self.send_file = api_methods[self.SEND_FILE]

        self.always_watch_messages=always_watch_messages
        self.role_messages=role_messages
        self.public_namespace = namespace
        self.events = events

        self.all_emojis_func = all_emojis_func
        self.emoji_action = set()
        try:
            self.emoji_file = dataloader.datafile(emoji_loc, load_as="json")
            self.emoji = self.emoji_file.content
        except FileNotFoundError:
            self.emoji_file = dataloader.newdatafile(emoji_loc)
            self.emoji = None

        try:
            self.perms_file = dataloader.datafile(perms_loc, load_as="json")
            self.perms = self.perms_file.content
        except FileNotFoundError:
            self.perms_file = dataloader.newdatafile(perms_loc)
            self.perms = dict()

    def _matches(self, reaction, user):
        '''(ReactionCommand, discord.Reaction, discord.Member or discord.User) -> bool
        This should only be overriden by non-concrete sub-classes to modify
        functionality. This calls matches()

        Returns True if the reaction should be interpreted by the command'''
        if self.emoji != None and reaction.message.server.id in self.emoji:
            emoji_match = self.are_same_emoji(self.emoji[reaction.message.server.id], reaction.emoji)
        else:
            emoji_match = (self.emoji == None)

        return (self.perms is None or reaction.message.server is None or reaction.message.server.id not in self.perms or user.id in self.perms[reaction.message.server.id]) and emoji_match and self.matches(reaction, user)

    def matches(self, reaction, user):
        '''(ReactionCommand, discord.Reaction, discord.Member or discord.User) -> bool
        Returns True if the reaction should be interpreted by the command'''
        return self.emoji!=None # matches should always be overriden when self.emoji==None

    def _action(self, reaction, user):
        '''(ReactionCommand, discord.Reaction, discord.Member or discord.User) -> None
        This should only be overriden by non-concrete sub-classes to modify
        functionality. This calls action()

        Reacts to a Reaction '''
        yield from self.action(reaction, user)

    def action(self, reaction, user):
        '''(ReactionCommand, discord.Reaction, discord.Member or discord.User) -> None
        Reacts to a Reaction '''
        pass

    def _shutdown(self):
        '''(ReactionCommand) -> None
        Concrete implementations should NOT override this function. Only sub-classes should override this,
        in order to expand or modify it's functionality.

        the method to call shutdown()'''
        if self.emoji != None: # save emojis
            self.emoji_file.content = self.emoji
            self.emoji_file.save()

        if self.perms != None: # save permissions
            self.perms_file.content = self.perms
            self.perms_file.save()
        return self.shutdown()

    def shutdown(self):
        '''(ReactionCommand) -> None
        This is called during bot shutdown
        Use this to save any variables that need to be loaded again when the bot restarts'''
        pass

    #useful methods just in case
    def matchemoji(self, emoji_id):
        '''(ReactionCommand, str) -> discord.Emoji or chr
        matches the emoji's id with the Discord emoji '''
        #return self.emoji==None or self.emoji==reaction.emoji or self.emoji==reaction.emoji.id
        if self.all_emojis_func == None:
            return
        for e in self.all_emojis_func():
            try:
                if e.id == emoji_id:
                    return e
            except:
                if str(e) == emoji_id:
                    return e

    def are_same_emoji(self, e_id, emoji):
        '''(ReactionCommand, string, discord.Emoji or chr) -> bool
        compares id with emoji, returns True if they are the same emoji '''
        if e_id == None or len(e_id)==0:
            return True
        elif len(e_id)>1:
            try:
                return e_id == emoji.id
            except:
                pass
        else:
            return e_id == emoji
        return False


class ReactionAddCommand(ReactionCommand):
    '''Extending ReactionAddCommand will make the command's matches() run whenever a Reaction is added'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.emoji_action.add("add")

class ReactionRemoveCommand(ReactionCommand):
    '''Extending ReactionAddCommand will make the command's matches() run whenever a Reaction is removed'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.emoji_action.add("remove")

class AdminReactionCommand(ReactionCommand):
    '''Extending AdminReactionCommand will make the command have access to the bot object (discord.Client object)'''

    def _action(self, reaction, user, client):
        '''(AdminReactionCommand, discord.Reaction, discord.Member or discord.User, discord.Client) -> None
        This calls action()'''
        yield from self.action(reaction, user, client)

    def action(self, reaction, user, client):
        '''(AdminReactionCommand, discord.Reaction, discord.Member or discord.User, discord.Client) -> None
        Reacts to a Reaction '''
        pass

class AdminReactionAddCommand(AdminReactionCommand, ReactionAddCommand):
    '''Extending AdminReactionAddCommand will make the command have access to the bot object (discord.Client object)
    and will make the command's matches() run whenever a Reaction is added'''

    pass

class AdminReactionRemoveCommand(AdminReactionCommand, ReactionRemoveCommand):
    '''Extending AdminReactionRemoveCommand will make the command have access to the bot object (discord.Client object)
    and will make the command's matches() run whenever a Reaction is removed'''

    pass

class PrivateReactionCommand(ReactionCommand):
    '''Extending PrivateReactionCommand will make the command's action() only run when the reaction
    is to a message in a private message (ie severless)'''

    def _matches(self, reaction, user):
        return reaction.message.server == None and super()._matches()

class WatchReactionCommand(ReactionCommand):
    '''Extending WatchCommand will make it possible for the command
    to add discord.Messages for the bot to always keep track of

    To add a message to the watchlist, use self.always_watch_messages.add(<discord.Message object>)
    self.always_watch_messages is a set()'''

    pass

class Dummy(ReactionCommand):
    '''Extending Dummy will make the command a dummy command (ie the command won't do anything)

    Great for setting up the data structure of the public_namespace in Multi'''

    def _matches(self, *args):
        return False

    def _action(self, *args):
        pass

class Config(ReactionCommand):
    '''Extending Config will make the command "catch" the configuration file for the command in self.config
    The usage of self.config is the same as any other dataloader.datafile class'''

    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        if config:
            try:
                self.config = dataloader.datafile(config) # configuration file for the Reaction
                if self.config.type=='config':
                    self.config=self.config.content[self.DEFAULT]
            except FileNotFoundError:
                self.config = None # NOTE: This is a bad state for a Config Reaction to be in, since it will cause unexpected errors
                raise ImportError("No config file found")
        else:
            raise ImportError("Config file cannot be None")
