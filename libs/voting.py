class Poll():
    '''Base class for voting systems that everything below extends
    This class should never be used in a concrete implementation'''
    def __init__(self, options = ["Y", "N"], allowed_voters = None):
        self.options = options
        self.allowed_voters = allowed_voters
        self.voted = set()

    def addVote(self, voter, vote):
        '''(Poll, anything, str)
        If vote is an option, the vote will be added to the sef.votes.
        Otherwise, this will raise a ValueError'''
        if vote in self.options and (self.allowed_voters == None or voter in self.allowed_voters) and voter not in self.voted:
            self.votes[vote] += 1
            self.voted.add(voter)
        else:
            raise ValueError("Invalid voter or vote option")

    addChoice = addVote

    def tallyVotes(self):
        '''(Poll) -> list
        this should return a list sorted from winner to loser in form [option, option's votes]'''
        pass

    def dumpVotes(self):
        '''(Poll) -> list
        this should return an unsorted list of votes'''
        pass

class FPTP(Poll):
    '''Implementation of First Past The Post voting system'''
    def __init__(self, options = ["Y", "N"], allowed_voters = None, **kwargs):
        '''(FPTP [, list, list, dict]) -> None '''
        super().__init__(options=options, allowed_voters=allowed_voters)
        self.votes = dict(zip(self.options, [0]*len(self.options)))

    def tallyVotes(self):
        '''(FPTP) -> list
        returns a list of [option, total votes], sorted by total votes'''
        results = [[self.votes[x],x] for x in self.votes] #turn into list of [votes, option]
        results.sort()
        return [[x[1],x[0]] for x in results] #swap option with votes

    def dumpVotes(self):
        '''(FPTP) -> list
        returns a list of [option, total votes], unsorted'''
        return [[self.votes[x],x] for x in self.votes] #turn self.votes dict into list of [votes, options]

class STV(Poll):
    '''Implementation of Single Transferable Vote voting system'''
    def __init__(self, options = ["A", "B", "C"], allowed_voters = None, transferables=3, **kwargs):
        '''(STV [, list, list, , int, dict]) -> None
        transferables is how many ranked votes one person can make
        ie transferables=2 means a voter can have a first choice and a second choice
        transferables=5 means a voter can have a first choice up to a fifth choice'''
        super().__init__(options=options, allowed_voters=allowed_voters)
        self.transferables = transferables
        self.votes = dict()

    def addVote(self, voter, vote):
        '''(STV, anything, list)-> None
        vote should be list of options from highest priority choice (1st choice) to lowest choice
        If the length of the vote list isn't the same length as transferables or the voter isn't allowed to vote,
        this won't do anything
        Any other invalid input (ie invalid option, repeated option, etc.) will raise as error (most likely a ValueError)'''
        if len(vote) == self.transferables and (self.allowed_voters == None or voter in self.allowed_voters ) and voter not in self.voted:
            for i in vote:
                if i not in self.options:
                    raise ValueError("Invalid option: "+i)
                if self.options.count(i)>1:
                    raise ValueError("Option "+i+" used more than once")
            self.votes[voter]=vote
            self.voted.add(voter)
        else:
            raise ValueError("Invalid vote or voter")

    def addChoice(self, voter, vote):
        '''(STV, anything, str)-> None
        adds votes chronologically (1st addChoice is 1st choice, 2nd addChoice is 2nd choice, etc.)'''
        if voter not in self.votes and (self.allowed_voters == None or voter in self.allowed_voters):
            self.votes[voter]=[None]*self.transferables
            self.voted.add(voter)
        if voter in self.votes and None in self.votes[voter] and vote in self.options and vote not in self.votes[voter]:
            self.votes[voter][self.votes[voter].index(None)] = vote

    def tallyVotes(self):
        '''kill me now...'''
        print(self.votes)
        return self.dumpVotes()
        #recursiveTallySort(self.votes, self.options):

    def dumpVotes(self, anonymised=True):
        '''(STV) -> list
        returns everyone's votes'''
        if not anonymised:
            return [[x, self.votes[x]] for x in self.votes]
        else:
            result = list()
            count = 0
            for x in self.votes:
                result.append([count, self.votes[x]])
                count += 1
            return result

    def countFirsts(self, votes, options):
        optionsCount = dict(zip(options, [0]*len(options)))
        for voter in votes:
            if votes[voter]!= []:
                optionsCount[votes[voter][0]]+=1
        output = [[optionsCount[x], x] for x in optionsCount]
        output.sort()
        return output

    def recursiveTallySort(self, votes, options):
        '''(dict, list) -> list
        If this works, returns a list of options sorted by highest (winner) to lowest (least voted for)'''
        votes = dict(votes)
        options = list(options)
        if len(options)>1:
            first_choices = self.countFirsts(votes, options)
            lowest_voted = firstChoices[-1] # lowerest_voted is list in form [option, votes]
            for voter in votes:
                if lowest_voted[0] in votes[voter]:
                    del(votes[voter][votes[voter].index(lowest_voted[0])])
            del(options[options.index(lowest_voted[0])])
            return self.recursiveTallySort(votes, options) + lowest_voted
        else:
            return first_choices[0][0]
