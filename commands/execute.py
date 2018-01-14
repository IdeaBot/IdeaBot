# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 10:07:23 2018

@author: 14flash
"""

from commands import command
import re
import sys

class ExecuteCommand(command.DirectOnlyCommand, command.BenchmarkableCommand):
    """ExecuteCommand tries to execute a passed in piece of code and responds
    with the result of the execution."""
    
    def matches(self, message):
        return self.collect_args(message)
        
    def action(self, message, send_func):
        args_match = self.collect_args(message)
        code = args_match.group(3)
        try:
            result = eval(code)
            if result is None:
                result = 'Execution completed successfully'
            yield from send_func(message.channel, result)
        except KeyboardInterrupt:
            raise
        except:
            exception = sys.exc_info()
            yield from send_func(message.channel, 'I\'m sure it\'s a feature that your code crashes, right? ' + self.exception_message(exception))
    
    def collect_args(self, message):
        # tested: https://regexr.com/3j6hc
        return re.search(r'\b(execute|evaluate)\s+(`{1}|`{3})([^`]+)\2', message.content, re.I)
    
    def exception_message(self, exception):
        return "Your code raised this: " + str(exception[0]).replace("'>", "").replace("<class '", "") + ":" + str(exception[1])