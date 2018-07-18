# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 07:58:54 2018

@author: 14flash
"""

import unittest
from libs import voting

class TestPoll(unittest.TestCase):
    
    def test_pollAllowsAllVoters(self):
        poll = voting.Poll(allowed_voters=None)
        
        self.assertTrue(poll.addVote('john', 'Y'))
        self.assertIn('john', poll.voted)
        self.assertEqual('Y', poll.votes['john'])
    
    def test_pollDeniesVoters(self):
        poll = voting.Poll(allowed_voters=['john', 'hank'])
        
        self.assertFalse(poll.addVote('mike', 'N'))
        self.assertNotIn('mike', poll.voted)
        self.assertNotIn('mike', poll.votes)
        
        self.assertTrue(poll.addVote('john', 'Y'))
        self.assertIn('john', poll.voted)
        self.assertEqual('Y', poll.votes['john'])
    
    def test_pollAcceptsOptions(self):
        poll = voting.Poll(options=['yes', 'maybe', 'no'])
        
        self.assertTrue(poll.addVote('john', 'maybe'))
        self.assertIn('john', poll.voted)
        self.assertEqual('maybe', poll.votes['john'])
    
    def test_pollDeniesOptions(self):
        poll = voting.Poll(options=['yes', 'maybe', 'no'])
        
        self.assertFalse(poll.addVote('john', 'Y'))
        self.assertNotIn('john', poll.voted)
        self.assertNotIn('john', poll.votes)
        
    def test_pollCannotVoteTwice(self):
        poll = voting.Poll()
        
        self.assertTrue(poll.addVote('john', 'Y'))
        self.assertIn('john', poll.voted)
        self.assertEqual('Y', poll.votes['john'])
        
        self.assertFalse(poll.addVote('john', 'N'))
        self.assertIn('john', poll.voted)
        self.assertEqual('Y', poll.votes['john'])
        
    # I'm only doing a basic test of addChoice because it points to addVote.
    # This test should cover the case where it is removed, but not behavioral
    # if it changes.
    def test_pollAddChoice(self):
        poll = voting.Poll()
        
        self.assertTrue(poll.addChoice('john', 'Y'))
        self.assertIn('john', poll.voted)
        self.assertEqual('Y', poll.votes['john'])
    
if __name__ == '__main__':
    unittest.main()