# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 19:52:01 2018

@author: 14flash
"""

from commands import command
import re

class Karma():
    '''TODO(14flash): Add description.'''
    # karma is static, so this basically works like a singleton
    karma = dict()
    
    def add_karma(entity, amount):
        try:
            Karma.karma[entity] += amount
        except KeyError:
            Karma.karma[entity] = amount
        return Karma.karma[entity]
    
    def get_karma(entity):
        return Karma.karma.get(entity, 0)
        
    # Why is it called slice? Because I'm too used to golang.
    def get_sorted_slice(num, key):
        '''(func, int) -> list
        Returns a sorted list of the top num entities in the karma dict
        sorted by the key func.
        
        key is function that takes one value and returns a sortable value.'''
        if num <= 0:
            return list()
        return sorted(Karma.karma, key=key)[:num]
    
    def get_top(num):
        return Karma.get_sorted_slice(num, lambda x: -Karma.get_karma(x))
    
    def get_bottom(num):
        return Karma.get_sorted_slice(num, lambda x: Karma.get_karma(x))

class KarmaAdderCommand(command.Command):
    '''KarmaAdderCommand finds ++ and -- messages and adjusts the karma
    appropriately.'''
    
    def matches(self, message):
        return len(self.collect_args(message)) > 0
    
    def action(self, message, send_func):
        args_match = self.collect_args(message)
        for args in args_match:
            entity = args[0]
            if args[1] == '++':
                amount = 1
                karma_message = '%s rocks! (karma: %d)'
            else:
                amount = -1
                karma_message = '%s sucks! (karma: %d)'
            new_amount = Karma.add_karma(entity, amount)
            yield from send_func(message.channel, karma_message % (entity, new_amount))
            
    
    def collect_args(self, message):
        # An enitity must be more than 1 character so I can tlak about how
        # great C++ is without the bot going crazy.
        return re.findall(r'(\w{2,})(\+\+|--)', message.content, re.I)

class KarmaValueCommand(command.DirectOnlyCommand):
    '''KarmaCountCommand responds to direct queries about an entity's karma.'''
    
    TOP_MIN = 1
    TOP_MAX = 10
    TOP_DEF = 5
    
    def matches(self, message):
        return self.collect_args(message)
    
    def action(self, message, send_func):
        send_wrapper = lambda text: send_func(message.channel, text)
        args_match = self.collect_args(message)
        if args_match.group(1) == 'count':
            yield from self.count(args_match.group(2), send_wrapper)
        elif args_match.group(1) == 'top':
            yield from self.top(args_match.group(2), send_wrapper)
        elif args_match.group(1) == 'bottom':
            yield from self.bottom(args_match.group(2), send_wrapper)
    
    def collect_args(self, message):
        # would it be better to just have group 2 be a .* catch all and have
        # each command do a smaller regex?
        return re.search(r'\bkarma\s(count|top|bottom)\b\s?(\w*)', message.content, re.I)
    
    def count(self, entity, send_func):
        if not entity:
            yield from send_func('What do you want me to count silly human?')
        else:
            amount = Karma.get_karma(entity)
            yield from send_func('%s has %d karma' % (entity, amount))
    
    def top(self, entity, send_func):
        num = self.parse_and_validate_number(entity)
        entities = Karma.get_top(num)
        yield from send_func('The top %d karma holders are:' % num)
        for entity in entities:
            yield from send_func('%s: %d' % (entity, Karma.get_karma(entity)))
    
    def bottom(self, entity, send_func):
        num = self.parse_and_validate_number(entity)
        entities = Karma.get_bottom(num)
        yield from send_func('The bottom %d karma holders are:' % num)
        for entity in entities:
            yield from send_func('%s: %d' % (entity, Karma.get_karma(entity)))
    
    def parse_and_validate_number(self, num_string):
        if not num_string:
            num = KarmaValueCommand.TOP_DEF
        else:
            try:
                num = int(num_string)
            except ValueError:
                num = KarmaValueCommand.TOP_DEF
        if num < KarmaValueCommand.TOP_MIN:
            num = KarmaValueCommand.TOP_MIN
        if num > KarmaValueCommand.TOP_MAX:
            num = KarmaValueCommand.TOP_MAX
        return num
