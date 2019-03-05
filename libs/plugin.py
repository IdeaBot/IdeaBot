"""
Plugin is the definition of the plugin interface class as well as extensible utility interfaces
that can be used to create Plugins quickly and easily.

Plugin is designed to be similar to Command and Reaction interface classes while being more versatile.

@author: NGnius
"""

import asyncio, time, traceback
from multiprocessing import Process, Queue

from libs import dataloader, addon

# general plugin constants
PERIOD = 'period'
DEFAULT = addon.DEFAULT

# threaded constants
THREADED_PERIOD = 'threadedperiod'
END_PROCESS = 'endprocess'

# threaded process ending constants
JOIN = 'join'
TERMINATE = 'terminate'
KILL = 'kill' # new in 3.7, do not use
NONE = None
CUSTOM = None

# args constants
ARGS = 'args'
KWARGS = 'kwargs'

class Plugin(addon.AddOn):
    '''Plugin represents a plugin that the discord bot can work alongside
    to add custom functionality not present in the base bot'''

    def __init__(self, api_methods=dict(), config=None, events=dict(), namespace=None, **kwargs):
        '''(Plugin, dict, str, dict) -> Plugin
        api_methods: a dict of api methods accessible to the Plugin, so that most plugins don't have to be AdminPlugins
        kwargs: included to simplify sub-classing'''
        self.shutting_down = False
        if config:
            try:
                self.config = dataloader.datafile(config) # configuration file for the Plugin
                if self.config.type=='config':
                    self.config=self.config.content[self.DEFAULT]
            except FileNotFoundError:
                self.config = None # NOTE: This is a bad state for a Plugin to be in, since it may cause unexpected errors
                raise ImportError("No config file found")
        else:
            raise ImportError("Config file cannot be None")
        self.period = float(self.config[PERIOD]) # period for each repetition of action()
        self.send_message = api_methods[self.SEND_MESSAGE]
        self.edit_message = api_methods[self.EDIT_MESSAGE]
        self.add_reaction = api_methods[self.ADD_REACTION]
        self.remove_reaction = api_methods[self.REMOVE_REACTION]
        self.send_typing = api_methods[self.SEND_TYPING]
        self.send_file = api_methods[self.SEND_FILE]

        self.events = events
        self.public_namespace = namespace

    async def _action(self):
        '''(Plugin) -> None
        Concrete implementations should NOT override this function. Only sub-classes should override this,
        in order to expand or modify it's functionality.

        the looping async method to call action()'''
        while not self.shutting_down and self.period!=-1:
            start_time = time.perf_counter()
            try:
                await self.action()
            except Exception as e: # catch any exception that could crash the task
                # traceback.print_exc()
                self._on_action_error(e)
            sleep_time = self.period - (time.perf_counter() - start_time)
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

    def _on_action_error(self, error):
        '''(Plugin, Exception) -> None
        Concrete implementations should not override this function.

        the method to call on_action_error() '''
        self.on_action_error(error)

    def on_action_error(self, error):
        ''' (Plugin, Exception) -> None
        Called when action() raises an exception
        Use this to handle error reporting or exceptional cases'''
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
        # please note that ThreadedPlugin will create a copy of all variables
        # for the new thread, unless they're compatible with multiple threads
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
        self.process.join() # wait for process ot terminate, indefinitely if necessary

    def _threaded_action(self, queue, **kwargs):
        '''(ThreadedPlugin, Queue, dict) -> None
        Concrete implementations should NOT override this function. Only sub-classes should override this,
        in order to expand or modify it's functionality.

        Similar to _action(), the looping thread that calls threaded_action'''

        while not self.shutting_down and self.threaded_period!=-1:
            start_time = time.perf_counter()
            try:
                self.threaded_action(queue, **kwargs)
            except: # catch anything that could crash the thread
                traceback.print_exc()
                pass
            sleep_time = self.threaded_period - (time.perf_counter() - start_time)
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
                    if ARGS not in action_dict[key]:
                        action_dict[key][ARGS]=[]
                    if KWARGS not in action_dict[key]:
                        action_dict[key][KWARGS]={}

                    if key==self.SEND_MESSAGE:
                        try:
                            await self.send_message(*action_dict[key][ARGS], **action_dict[key][KWARGS])
                        except TypeError:
                            # TypeError is raised when missing arguments
                            # or when action_dict[key] is not mapping
                            # (ie **action_dict[key] is not a valid operation)
                            pass
                    elif key==self.EDIT_MESSAGE:
                        try:
                            await self.edit_message(*action_dict[key][ARGS], **action_dict[key][KWARGS])
                        except TypeError:
                            # TypeError is raised when missing arguments
                            # or when action_dict[key] is not mapping
                            # (ie **action_dict[key] is not a valid operation)
                            pass
                    elif key==self.ADD_REACTION:
                        try:
                            await self.add_reaction(*action_dict[key][ARGS], **action_dict[key][KWARGS])
                        except TypeError:
                            # TypeError is raised when missing arguments
                            # or when action_dict[key] is not mapping
                            # (ie **action_dict[key] is not a valid operation)
                            pass
                    elif key==self.REMOVE_REACTION:
                        try:
                            await self.remove_reaction(*action_dict[key][ARGS], **action_dict[key][KWARGS])
                        except TypeError:
                            # TypeError is raised when missing arguments
                            # or when action_dict[key] is not mapping
                            # (ie **action_dict[key] is not a valid operation)
                            pass
                    elif key==self.SEND_TYPING:
                        try:
                            await self.send_typing(*action_dict[key][ARGS], **action_dict[key][KWARGS])
                        except TypeError:
                            # TypeError is raised when missing arguments
                            # or when action_dict[key] is not mapping
                            # (ie **action_dict[key] is not a valid operation)
                            pass
                    elif key==self.SEND_FILE:
                        try:
                            await self.send_file(*action_dict[key][ARGS], **action_dict[key][KWARGS])
                        except TypeError:
                            # TypeError is raised when missing arguments
                            # or when action_dict[key] is not mapping
                            # (ie **action_dict[key] is not a valid operation)
                            pass

class OnReadyPlugin(Plugin):
    async def _action(self):
        await self.events[self.READY]()
        await super()._action()

class OnLoginPlugin(Plugin):
    async def _action(self):
        await self.events[self.LOGIN]()
        await super()._action()

class OnMessagePlugin(Plugin):
    async def _action(self):
        while not self.shutting_down:
            message = await self.events[self.MESSAGE]() # this is the difference
            start_time = time.perf_counter()
            await self.action(message)
            await asyncio.sleep(self.period - (time.perf_counter() - start_time)) # account for execution time of self.action() in asyncio.sleep()

    def action(self, message):
        pass

class OnReactionPlugin(Plugin):
    async def _action(self):
        while not self.shutting_down:
            reaction, user = await self.events[self.REACTION]() # this is the difference
            start_time = time.perf_counter()
            await self.action(reaction, user)
            await asyncio.sleep(self.period - (time.perf_counter() - start_time)) # account for execution time of self.action() in asyncio.sleep()

    def action(self, reaction, user):
        pass

class AdminPlugin(Plugin):
    '''Similar to a regular Plugin, but has access to the client/bot's class.
    This is a security risk, yay! Use wisely and sparingly '''
    def add_client_variable(self, client_var):
        self.client = self.bot = client_var
        self._on_client_add()

    def _on_client_add(self):
        '''() -> None
        wrapper for on_client_add method '''
        self.on_client_add()

    def on_client_add(self):
        '''() -> None
        A method called when the bot client variable is passed to the AdminPlugin.

        This is always called after the plugin is initialized but before the action() task is created.
        This may be useful for overriding bot variables or methods instead
        of directly and permanently modifying the bot.py file'''
        pass
