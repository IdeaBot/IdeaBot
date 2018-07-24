"""
Plugin is the definition of the plugin interface class as well as extensible utility interfaces
that can be used to create Plugins quickly and easily.

Plugin is designed to be similar to Command and Reaction interface classes while being more versatile.

@author: NGnius
"""

import asyncio, time
from multiprocessing import Process, Queue

from libs import dataloader

# general plugin constants
PERIOD = 'period'
DEFAULT = 'DEFAULT'

# bot api methods accessible to a regular Plugin
# if more functionality is required, consider using an AdminPlugin
SEND_MESSAGE = 'send_message'
EDIT_MESSAGE = 'edit_message'
ADD_REACTION = 'add_reaction'
REMOVE_REACTION = 'remove_reaction'
SEND_TYPING = 'send_typing'
SEND_FILE = 'send_file'

# threaded constants
THREADED_PERIOD = 'threadedperiod'
END_PROCESS = 'endprocess'

# threaded process ending constants
JOIN = 'join'
TERMINATE = 'terminate'
KILL = 'kill' # new in 3.7, do not use
NONE = None
CUSTOM = None

# event constants
READY = 'ready'
LOGIN = 'login'
MESSAGE = 'message'
REACTION = 'reaction'

class Plugin():
    '''Plugin represents a plugin that the discord bot can work alongside
    to add custom functionality not present in the base bot'''

    def __init__(self, api_methods=dict(), config=None, **kwargs):
        '''(Plugin, dict, str, dict) -> Plugin
        api_methods: a dict of api methods accessible to the Plugin, so that most plugins don't have to be AdminPlugins
        kwargs: included to simplify sub-classing'''
        self.shutting_down = False
        try:
            self.config = dataloader.datafile(config).content[DEFAULT] # configuration file for the Plugin
        except FileNotFoundError:
            self.config = None # NOTE: This is a bad state for a Plugin to be in, since it may cause unexpected errors
            raise ImportError("No config file found")
        self.period = float(self.config[PERIOD]) # period for each repetition of action()
        self.send_message = api_methods[SEND_MESSAGE]
        self.edit_message = api_methods[EDIT_MESSAGE]
        self.add_reaction = api_methods[ADD_REACTION]
        self.remove_reaction = api_methods[REMOVE_REACTION]
        self.send_typing = api_methods[SEND_TYPING]
        self.send_file = api_methods[SEND_FILE]

    async def _action(self):
        '''(Plugin) -> None
        Concrete implementations should NOT override this function. Only sub-classes should override this,
        in order to expand or modify it's functionality.

        the looping async method to call action()'''
        while not self.shutting_down:
            start_time = time.time()
            await self.action()
            sleep_time = self.period - (time.time() - start_time)
            if sleep_time<0:
                sleep_time=0
            await asyncio.sleep(sleep_time) # account for execution time of self.action() in asyncio.sleep()

    async def action(self):
        '''(Plugin) -> None
        the method to be run alongside the discord bot
        This will be looped externally'''
        pass

    def _shutdown(self):
        '''(Plugin) -> None
        Concrete implementations should NOT override this function. Only sub-classes should override this,
        in order to expand or modify it's functionality.

        the method to call shutdown()'''
        self.shutting_down=True
        self.shutdown()

    def shutdown(self):
        '''(Plugin) -> None
        called during bot shutdown/logout
        Use this to save any information that needs to be kept for the next time the bot starts up'''
        pass

class ThreadedPlugin(Plugin):
    '''ThreadedPlugin is an extension of the Plugin interface for an independent task to run in another thread.

    This is quite useful for scrapers and other slow tasks that block the main thread and don't require access to bot variables'''

    def spawn_process(self):
        self.process = Process(target = self._threaded_action, args = (self.queue, ), kwargs = self.threaded_kwargs) # secondary thread
        self.process.start()

    def __init__(self, should_spawn_thread=True,**kwargs):
        '''(ThreadedPlugin, dict) -> ThreadedPlugin'''
        super().__init__(**kwargs)
        self.end_process = self.config[END_PROCESS] # method of ending process. Valid options are 'join', 'terminate' and 'kill' (Python3.7+ only for kill)
        self.threaded_period = float(self.config[THREADED_PERIOD]) # like self.period, except for for the threaded action
        self.queue = Queue() # queue object for sending information to and from the ThreadedPlugin's secondary thread
        try: # ensure threaded_kwargs exists, but don't overwrite
            self.threaded_kwargs
        except AttributeError:
            self.threaded_kwargs = dict()
        if should_spawn_thread:
            self.spawn_process()

    def _shutdown(self):
        '''(ThreadedPlugin) -> None
        Exits the secondary thread and does everything Plugin's _shutdown() does'''
        super()._shutdown()
        if self.process.is_alive():
            if self.end_process == JOIN:
                self.process.join()
            elif self.end_process == TERMINATE:
                self.process.terminate()
            elif self.end_process == KILL:
                self.process.kill()
            elif self.end_process == NONE or self.end_process == CUSTOM:
                pass # assume user has defined shutdown() and it has already handled ending the thread

    def _threaded_action(self, queue, **kwargs):
        '''(ThreadedPlugin, Queue, dict) -> None
        Concrete implementations should NOT override this function. Only sub-classes should override this,
        in order to expand or modify it's functionality.

        Similar to _action(), the looping thread that calls threaded_action'''

        while not self.shutting_down:
            start_time = time.time()
            self.threaded_action(queue, **kwargs)
            sleep_time = self.threaded_period - (time.time() - start_time)
            if sleep_time<0:
                sleep_time=0
            time.sleep(sleep_time) # account for execution time of self.action() in asyncio.sleep()

    def threaded_action(self, queue, **kwargs):
        '''(ThreadedPlugin, Queue, dict) -> None
        the method to be run in the secondary thread
        This will be looped externally'''
        pass

    async def action(self):
        '''(ThreadedPlugin) -> None
        A standard action method to interpret dictionaries in queue
        This method uses the standard plugin constants (SEMD_MESSAGE, EDIT_MESSAGE, etc.)
        to interpret dictionaries to use the discord API to do the appropriate actions.

        Use a dictionary, with the appropriate keys, associated to the API action
        to send parameters to the API function (send_message(**kwargs), edit_message(**kwargs), etc.).
        The keys are the same as the API parameters.

        this method overrides Plugin's action method'''

        while not self.queue.empty():
            action_dict = self.queue.get() # hopefully it's a dict object
            if isinstance(action_dict, dict): # make sure it's a dict object
                for key in action_dict:
                    if key==SEND_MESSAGE:
                        try:
                            await self.send_message(**action_dict[key])
                        except TypeError:
                            # TypeError is raised when missing arguments
                            # or when action_dict[key] is not mapping
                            # (ie **action_dict[key] is not a valid operation)
                            pass
                    elif key==EDIT_MESSAGE:
                        try:
                            await self.edit_message(**action_dict[key])
                        except TypeError:
                            # TypeError is raised when missing arguments
                            # or when action_dict[key] is not mapping
                            # (ie **action_dict[key] is not a valid operation)
                            pass
                    elif key==ADD_REACTION:
                        try:
                            await self.add_reaction(**action_dict[key])
                        except TypeError:
                            # TypeError is raised when missing arguments
                            # or when action_dict[key] is not mapping
                            # (ie **action_dict[key] is not a valid operation)
                            pass
                    elif key==REMOVE_REACTION:
                        try:
                            await self.remove_reaction(**action_dict[key])
                        except TypeError:
                            # TypeError is raised when missing arguments
                            # or when action_dict[key] is not mapping
                            # (ie **action_dict[key] is not a valid operation)
                            pass
                    elif key==SEND_TYPING:
                        try:
                            await self.send_typing(**action_dict[key])
                        except TypeError:
                            # TypeError is raised when missing arguments
                            # or when action_dict[key] is not mapping
                            # (ie **action_dict[key] is not a valid operation)
                            pass
                    elif key==SEND_FILE:
                        try:
                            await self.send_file(**action_dict[key])
                        except TypeError:
                            # TypeError is raised when missing arguments
                            # or when action_dict[key] is not mapping
                            # (ie **action_dict[key] is not a valid operation)
                            pass


class EventPlugin(Plugin):
    '''Subclass for catching the events dict.
    This probably shouldn't be used on it's own, since it adds no (concrete) functionality.'''
    def __init__(self, events, **kwargs):
        super().__init__(**kwargs)
        self.events = events

class OnReadyPlugin(EventPlugin):
    async def _action(self):
        await self.events[READY]()
        await super()._action()

class OnLoginPlugin(EventPlugin):
    async def _action(self):
        await self.events[LOGIN]()
        await super()._action()

class OnMessagePlugin(EventPlugin):
    async def _action(self):
        while not shutting_down:
            message = await self.events[MESSAGE]() # this is the difference
            start_time = time.time()
            await self.action(message)
            await asyncio.sleep(self.period - (time.time() - start_time)) # account for execution time of self.action() in asyncio.sleep()

    def action(self, message):
        pass

class OnReactionPlugin(EventPlugin):
    async def _action(self):
        while not shutting_down:
            reaction, user = await self.events[REACTION]() # this is the difference
            start_time = time.time()
            await self.action(reaction, user)
            await asyncio.sleep(self.period - (time.time() - start_time)) # account for execution time of self.action() in asyncio.sleep()

    def action(self, reaction, user):
        pass

class AdminPlugin(Plugin):
    '''Similar to a regular Plugin, but has access to the client/bot's class.
    This is a security risk, yay! Use wisely and sparingly '''
    def add_client_variable(self, client_var):
        self.client = self.bot = client_var
