"""
Plugin is the definition of the plugin interface class as well as extensible utility interfaces
that can be used to create Plugins quickly and easily.

Plugin is designed to be similar to Command and Reaction interface classes while being more versatile.

@author: NGnius
"""

import asyncio, time
from multiprocessing import Process, Queue

from libs import dataloader

PERIOD = 'period'
THREADED_PERIOD = 'threadedperiod'
DEFAULT = 'DEFAULT'
END_PROCESS = 'endprocess'

# process ending constants
JOIN = 'join'
TERMINATE = 'terminate'
KILL = 'kill'
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

    def __init__(self, config=None, **kwargs):
        '''(Plugin, dict) -> Plugin
        kwargs: included to simplify sub-classing'''
        self.shutting_down = False
        self.config = dataloader.datafile(config).content[DEFAULT] # configuration file for the Plugin
        self.period = float(self.config[PERIOD]) # period for each repetition of action()

    async def _action(self):
        '''(Plugin) -> None
        Concrete implementations should NOT override this function. Only sub-classes should override this,
        in order to expand or modify it's functionality.

        the looping async method to call action()'''
        while not shutting_down:
            start_time = time.time()
            self.action()
            await asyncio.sleep(self.period - (time.time() - start_time)) # account for execution time of self.action() in asyncio.sleep()

    def action(self):
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

    def __init__(self, **kwargs):
        '''(ThreadedPlugin, dict) -> ThreadedPlugin'''
        super().__init__(**kwargs)
        self.end_process = self.config[END_PROCESS] # method of ending process. Valid options are 'join', 'terminate' and 'kill'
        self.threaded_period = float(self.config[THREADED_PERIOD]) # like self.period, except for for the threaded action
        self.queue = Queue() # queue object for sending information to and from the ThreadedPlugin's secondary thread
        try: # ensure threaded_kwargs exists, but don't overwrite
            self.threaded_kwargs
        except AttributeError:
            self.threaded_kwargs = dict()
        self.process = Process(target = self._threaded_action, args = (self.queue, ), kwargs = self.threaded_kwargs) # secondary thread
        self.process.start()

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
            time.sleep(self.period - (time.time() - start_time)) # account for execution time of self.action() in asyncio.sleep()

    def threaded_action(self, queue, **kwargs):
        '''(ThreadedPlugin, Queue, dict) -> None
        the method to be run in the secondary thread
        This will be looped externally'''
        pass

class EventPlugin(Plugin):
    '''Subclass for catching the events dict.
    This probably shouldn't be used on it's own, since it adds no (concrete) functionality.'''
    def __init__(self, events, **kwargs):
        self.events = events

class OnReadyPlugin(EventPlugin):
    async def _action(self):
        await self.events[READY]()
        while not shutting_down:
            start_time = time.time()
            self.action()
            await asyncio.sleep(self.period - (time.time() - start_time)) # account for execution time of self.action() in asyncio.sleep()

class OnLoginPlugin(EventPlugin):
    async def _action(self):
        await self.events[LOGIN]()
        while not shutting_down:
            start_time = time.time()
            self.action()
            await asyncio.sleep(self.period - (time.time() - start_time)) # account for execution time of self.action() in asyncio.sleep()

class OnMessagePlugin(EventPlugin):
    async def _action(self):
        while not shutting_down:
            message = await self.events[MESSAGE]()
            start_time = time.time()
            self.action(message)
            await asyncio.sleep(self.period - (time.time() - start_time)) # account for execution time of self.action() in asyncio.sleep()

    def action(self, message):
        pass

class OnReactionPlugin(EventPlugin):
    async def _action(self):
        while not shutting_down:
            reaction, user = await self.events[REACTION]()
            start_time = time.time()
            self.action(reaction, user)
            await asyncio.sleep(self.period - (time.time() - start_time)) # account for execution time of self.action() in asyncio.sleep()

    def action(self, reaction, user):
        pass
