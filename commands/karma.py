# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 19:52:01 2018

@author: 14flash
"""

from commands import command
import re

class Karma():
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

class KarmaCountCommand(command.DirectOnlyCommand):
    '''KarmaCountCommand responds to direct queries about an entity's karma.'''
    
    def matches(self, message):
        return self.collect_args(message)
    
    def action(self, message, send_func):
        args_match = self.collect_args(message)
        if args_match.group(1) == 'count':
            entity = args_match.group(2)
            amount = Karma.get_karma(entity)
            yield from send_func(message.channel, '%s has %s karma' % (entity, amount))
        elif args_match.group(1) == 'top':
            yield from send_func(message.channel, 'Not yet implemented.')
        elif args_match.group(1) == 'bottom':
            yield from send_func(message.channel, 'Not yet implemented.')
    
    def collect_args(self, message):
        # would it be better to just have group 2 be a .* catch all and have
        # each command do a smaller regex?
        return re.search(r'\bkarma\s(count|top|bottom)\b\s?(\w+)?', message.content, re.I)
