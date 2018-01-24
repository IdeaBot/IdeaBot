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

    def __init__(self, perms=None, **kwargs):
        '''(Command, str, dict) -> Command
        perms: str of users who have permission to use this command
        kwargs: included for sub-classing'''
        self.perms = perms
        self.emoji_action = set()

    def _matches(self, reaction, user):
        '''(Command, discord.Reaction, discord.Member or discord.User) -> bool
        This should only be overriden by non-concrete sub-classes to modify
        functionality. This calls matches()

        Returns True if the reaction should be interpreted by the command'''
        return (self.perms is None or message.author.id in self.perms) and self.matches(reaction, user)

    def matches(self, reaction, user):
        '''(Command, discord.Reaction, discord.Member or discord.User) -> bool
        Returns True if the reaction should be interpreted by the command'''
        return False

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


class ReactionAddCommand(ReactionCommand):
    def __init__(self, perms=None, **kwargs):
        super().__init__(perms, **kwargs)
        self.emoji_action.add("add") # this is the only difference

class ReactionRemoveCommand(ReactionCommand):
    def __init__(self, perms=None, **kwargs):
        super().__init__(perms, **kwargs)
        self.emoji_action.add("remove") # this is the only difference

class AdminReactionAddCommand(ReactionAddCommand):
    '''Extending AdminReactionAddCommand will make the command have access to the bot object (discord.Client object)'''

    def _action(self, reaction, user, client):
        '''(AdminReactionAddCommand, discord.Reaction, discord.Member or discord.User, discord.Client) -> None
        This calls action()

        Reacts to a Reaction '''
        yield from self.action(reaction, user, client)

    def action(self, reaction, user, client):
        '''(AdminReactionAddCommand, discord.Reaction, discord.Member or discord.User, discord.Client) -> None
        Reacts to a Reaction '''
        pass

class AdminReactionRemoveCommand(ReactionRemoveCommand):
    '''Extending AdminReactionRemoveCommand will make the command have access to the bot object (discord.Client object)'''

    def _action(self, reaction, user, client):
        '''(AdminReactionRemoveCommand, discord.Reaction, discord.Member or discord.User, discord.Client) -> None
        This calls action()

        Reacts to a Reaction '''
        yield from self.action(reaction, user, client)

    def action(self, reaction, user, client):
        '''(AdminReactionRemoveCommand, discord.Reaction, discord.Member or discord.User, discord.Client) -> None
        Reacts to a Reaction '''
        pass
