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

class TestFPTP(unittest.TestCase):
    
    # Order may change. For now there is a guaranteed order.
    def test_tallyVotesNoVotes(self):
        poll = voting.FPTP()
        tally = poll.tallyVotes()
        
        self.assertEqual('Y', tally[0][0])
        self.assertEqual(0, tally[0][1])
        self.assertEqual('N', tally[1][0])
        self.assertEqual(0, tally[1][1])
        
    def test_tallyVotesWinnerFirst(self):
        poll = voting.FPTP()
        poll.addVote('john', 'N')
        tally = poll.tallyVotes()
        
        self.assertEqual('N', tally[0][0])
        self.assertEqual(1, tally[0][1])
    
    def test_tallyVotesSameLengthAsOptions(self):
        opt = ['a', 'b', 'c', 'd']
        poll = voting.FPTP(options=opt)
        tally = poll.tallyVotes()
        
        self.assertEqual(len(opt), len(tally))

class TestSTV(unittest.TestCase):
    
    def test_STVAutoSetTransferables(self):
        poll = voting.STV(options=['yes', 'maybe', 'no'])
        self.assertEqual(3, poll.transferables)
    
    def test_STVSetTransferables(self):
        poll = voting.STV(transferables=5)
        self.assertEqual(5, poll.transferables)
    
    def test_STVTransferablesTypeCheck(self):
        poll = voting.STV(options=['A', 'B', 'C'], transferables="three")
        self.assertEqual(3, poll.transferables)
    
    def test_addVoteWrongLengthRaisesError(self):
        poll = voting.STV(transferables=2)
        self.assertRaises(ValueError, poll.addVote, 'john', ['A'])
    
    def test_addVoteVoterNotAllowedRaisesError(self):
        poll = voting.STV(allowed_voters=['john', 'hank'])
        self.assertRaises(ValueError, poll.addVote, 'mike', ['C', 'B', 'A'])
    
    def test_addVoteDuplicateVoteRaisesError(self):
        poll = voting.STV()
        self.assertRaises(ValueError, poll.addVote, 'john', ['A', 'B', 'A'])
    
    def test_addVoteInvalidOptionRaisesError(self):
        poll = voting.STV()
        self.assertRaises(ValueError, poll.addVote, 'john', ['A', 'B', 'not-a-choice'])
    
    def test_addVoteVotingAgainRaissesError(self):
        poll = voting.STV()
        poll.addVote('john', ['A', 'B', 'C'])
        self.assertRaises(ValueError, poll.addVote, 'john', ['B', 'A', 'C'])
    
    def test_addVoteSavesVote(self):
        poll = voting.STV()
        poll.addVote('john', ['A', 'B', 'C'])
        self.assertIn('john', poll.voted)
        self.assertEqual(['A', 'B', 'C'], poll.votes['john'])
    
    def test_addChoiceVoterNotAllowed(self):
        poll = voting.STV(allowed_voters=['john', 'hank'])
        self.assertFalse(poll.addChoice('mike', 'A'))
        self.assertNotIn('mike', poll.voted)
        self.assertNotIn('mike', poll.votes)
    
    def test_addChoiceAddFirst(self):
        poll = voting.STV()
        self.assertTrue(poll.addChoice('john', 'A'))
        self.assertIn('john', poll.voted)
        self.assertEqual(['A', None, None], poll.votes['john'])
    
    def test_addChoiceAddDuplicateNotAllowed(self):
        poll = voting.STV()
        poll.addChoice('john', 'A')
        self.assertFalse(poll.addChoice('john', 'A'))
        self.assertEqual(['A', None, None], poll.votes['john'])
    
    def test_addChoiceNoMoreThanTransferablesAllowed(self):
        poll = voting.STV(transferables=1)
        poll.addChoice('john', 'A')
        self.assertFalse(poll.addChoice('john', 'B'))
        self.assertEqual(['A'], poll.votes['john'])
    
    # This doesn't exactly match my expectation for the API, but oh well,
    # documenting it is good.
    def test_addChoiceInvalidOptionNotAllowed(self):
        poll = voting.STV()
        self.assertFalse(poll.addChoice('john', None))
        self.assertIn('john', poll.voted)
        self.assertEqual([None, None, None], poll.votes['john'])
    
    def test_tallyVotesNoOptionsNoVotes(self):
        poll = voting.STV(options=[])
        tally = poll.tallyVotes()
        self.assertEqual(['No votes recorded'], tally)
    
    # Order may be changed on this test.  For now, there is a guaranteed order.
    def test_tallyVotesNoVotesNoTieBreaks(self):
        poll = voting.STV()
        tally = poll.tallyVotes()
        self.assertEqual(len(tally), len(poll.options))
        self.assertEqual(['C', 0], tally[0])
        self.assertEqual(['B', 0], tally[1])
        self.assertEqual(['A', 0], tally[2])
    
    # I, once again, don't understand the meaning of the vote count in this api
    # so I'm documenting it with unit tests rather than trying to change it.
    def test_tallyVotesClearWinner(self):
        poll = voting.STV()
        poll.addVote('john', ['A', 'B', 'C'])
        poll.addVote('hank', ['B', 'A', 'C'])
        poll.addVote('mike', ['A', 'C', 'B'])
        tally = poll.tallyVotes()
        self.assertEqual(['A', 3], tally[0])
        self.assertEqual(['B', 1], tally[1])
        self.assertEqual(['C', 0], tally[2])
    
    # This test should fail unitl MBC tie-breaking is written into the bot
    def test_tallyVotesTieBroken(self):
        poll = voting.STV(options=['a', 'b', 'c', 'd'])
        # I really want to clean up addVote's API just to make this unit test cleaner to setup...
        poll.addChoice('john', 'a')
        poll.addChoice('hank', 'b')
        poll.addChoice('hank', 'c')
        poll.addChoice('hank', 'a')
        poll.addChoice('mike', 'a')
        poll.addChoice('mike', 'd')
        poll.addVote('olly', ['b', 'd', 'a', 'c'])
        # At this point, 'a' and 'b' are tied for most votes, but MBC('a') = 6,
        # MBC('b') = 7 so 'b' should always be top of the list
        tally = poll.tallyVotes()
        self.assertEqual(['b', 2], tally[0])
        self.assertEqual(['a', 3], tally[1])
    
if __name__ == '__main__':
    unittest.main()