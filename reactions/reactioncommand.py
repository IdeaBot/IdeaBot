"""
Command is the definition of the reaction command class as well as extensible
utility reaction command classes which can be used to make concrete reaction commands

This is very similar to regular (message) commands, except for the input
is a reaction (reaction.message is equivalent to message in message command) and
a user (the person who added/removed/updated the reaction)
"""

class ReactionCommand():
    '''ReactionAddCommand represents a command that the bot can use to take action
    based on reactions added to any discord messeage it listens to.'''

    def __init__(self, all_emojis_func=None, emoji=None, perms=None):
        '''(ReactionCommand, func, str, dict) -> Command
        perms: str of users who have permission to use this command
        kwargs: included for sub-classing'''
        self.all_emojis_func = all_emojis_func
        self.perms = perms
        self.emoji_action = set()
        self.emoji = emoji

    def _matches(self, reaction, user):
        '''(Command, discord.Reaction, discord.Member or discord.User) -> bool
        This should only be overriden by non-concrete sub-classes to modify
        functionality. This calls matches()

        Returns True if the reaction should be interpreted by the command'''
        return (self.perms == None or user.id in self.perms) and self.are_same_emoji(self.emoji, reaction.emoji) and self.matches(reaction, user)

    def matches(self, reaction, user):
        '''(Command, discord.Reaction, discord.Member or discord.User) -> bool
        Returns True if the reaction should be interpreted by the command'''
        return True

    def _action(self, reaction, user):
        '''(Command, discord.Reaction, discord.Member or discord.User) -> None
        This should only be overriden by non-concrete sub-classes to modify
        functionality. This calls action()

        Reacts to a Reaction '''
        yield from self.action(reaction, user)

    def action(self, reaction, user):
        '''(Command, discord.Reaction, discord.Member or discord.User) -> None
        Reacts to a Reaction '''
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

    def __init__(self, always_watch_messages, **kwargs):
        super().__init__(**kwargs)
        self.always_watch_messages=always_watch_messages
