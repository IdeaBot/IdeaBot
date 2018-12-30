from libs import command, dataloader
import re

class Command(command.Dummy, command.Config):
    '''This initializes the dictionary of entity karma, and utils for editting it easily.

Dummy command; please ignore'''
    # karma is static, so this basically works like a singleton
    karma = dict()

    def add_karma(self, entity, amount):
        '''(str, int) -> int
        Gives amount karma to entity, and returns how much karma entity now has.'''
        try:
            self.public_namespace.karma[entity] += amount
        except KeyError:
            self.public_namespace.karma[entity] = amount
        return self.public_namespace.karma[entity]

    def get_karma(self, entity):
        '''(str) -> int
        Returns how much karma entity has.'''
        return self.public_namespace.karma.get(entity, 0)

    # Why is it called slice? Because I'm too used to golang.
    def get_sorted_slice(self, num, key):
        '''(int, func) -> list
        Returns a sorted list of the top num entities in the karma dict
        sorted by the key func.

        key is function that takes one value and returns a sortable value.'''
        if num <= 0:
            return list()
        return sorted(self.public_namespace.karma, key=key)[:num]

    def get_top(self, num):
        '''(int) -> list
        Returns a list of the top num karma holders (or less than that if there
        are less than num total karma holders.)'''
        return self.public_namespace.get_sorted_slice(num, lambda x: -self.public_namespace.get_karma(x))

    def get_bottom(self, num):
        '''(int) -> list
        Returns a list of the bottom num karma holders (or less than that if
        there are less than num total karma holders.)'''
        return self.public_namespace.get_sorted_slice(num, lambda x: self.public_namespace.get_karma(x))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.public_namespace.karma = self.karma
        self.public_namespace.add_karma = self.add_karma
        self.public_namespace.get_karma = self.get_karma
        self.public_namespace.get_sorted_slice = self.get_sorted_slice
        self.public_namespace.get_top = self.get_top
        self.public_namespace.get_bottom = self.get_bottom
        self.public_namespace.config = self.config

    def shutdown(self):
        karma_entity_sum = 0
        for key in self.karma:
            karma_entity_sum += len(key)
        # I can't decide how this should be logged - making a log just for this seems unnecessary
        # log.info("karma would take about %d bytes to save" % karma_entity_sum)'''
