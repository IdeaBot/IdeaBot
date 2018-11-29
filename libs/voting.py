class Poll():
    '''Base class for voting systems that everything below extends
    This class should never be used in a concrete implementation'''
    def __init__(self, options = ["Y", "N"], allowed_voters = None, voted=None, votes=None):
        if voted is None:
            voted = list()
        if votes is None:
            votes = dict()
        self.options = options
        self.allowed_voters = allowed_voters
        self.voted = voted
        self.votes = votes

    def addVote(self, voter, vote):
        '''(Poll, anything, str) -> bool
        If vote is an option, the vote will be added to the sef.votes.
        Otherwise, this will return False'''
        if vote in self.options and (self.allowed_voters == None or voter in self.allowed_voters) and voter not in self.voted:
            self.votes[voter] = vote
            self.voted.append(voter)
            return True
        return False

    addChoice = addVote

    def tallyVotes(self):
        '''(Poll) -> list
        this should return a list sorted from winner to loser in form [option, option's votes]'''
        pass

    def dumpVotes(self):
        '''(Poll) -> list
        this should return an unsorted list of votes, anonymised
        in a list of [anonymous voter, their vote(s)]'''
        pass

class FPTP(Poll):
    '''Implementation of First Past The Post voting system'''

    def tallyVotes(self):
        '''(FPTP) -> list
        returns a list of [option, total votes], sorted by total votes'''
        # print(self.dumpVotes())
        votes_by_option = dict(zip(self.options, [0]*len(self.options)))
        for voter in self.votes:
            votes_by_option[self.votes[voter]]+=1
        results = [[votes_by_option[x],x] for x in votes_by_option] #turn into list of [votes, option]
        results.sort()
        results = results[::-1] #reverse order so highest number is first; not last
        return [[x[1],x[0]] for x in results] #swap option with votes

    def dumpVotes(self, anonymised=True):
        '''(FPTP) -> list
        returns a list of [option, voter], unsorted'''
        if not anonymised:
            return [[x, self.votes[x]] for x in self.votes] #turn self.votes dict into list of [voter, vote]
        else:
            result = list()
            count=0
            for voter in self.votes:
                result.append([count, self.votes[voter]])
                count += 1
            return result


class STV(Poll):
    '''Implementation of Single Transferable Vote voting system'''
    def __init__(self, options = ["A", "B", "C"], allowed_voters = None, transferables=None, **kwargs):
        '''(STV [, list, list, , int, dict]) -> None
        transferables is how many ranked votes one person can make
        ie transferables=2 means a voter can have a first choice and a second choice
        transferables=5 means a voter can have a first choice up to a fifth choice'''
        super().__init__(options=options, allowed_voters=allowed_voters, **kwargs)
        if transferables is not None and isinstance(transferables, int):
            self.transferables = transferables
        else:
            self.transferables = len(self.options)
        self.votes = dict()

    def addVote(self, voter, vote):
        '''(STV, str, list)-> None
        vote should be list of options from highest priority choice (1st choice) to lowest choice
        If the length of the vote list isn't the same length as transferables or the voter isn't allowed to vote,
        this won't do anything
        Any other invalid input (ie invalid option, repeated option, etc.) will raise as error (most likely a ValueError)'''
        if len(vote) == self.transferables and (self.allowed_voters == None or voter in self.allowed_voters ) and voter not in self.voted:
            for i in vote:
                if i not in self.options:
                    raise ValueError("Invalid option: "+i)
                if vote.count(i)>1:
                    raise ValueError("Option "+i+" used more than once")
            self.votes[str(voter)]=list(vote)
            self.voted.append(str(voter))
        else:
            raise ValueError("Invalid vote or voter")

    def addChoice(self, voter, vote):
        '''(STV, str, str)-> bool
        adds votes chronologically (1st addChoice is 1st choice, 2nd addChoice is 2nd choice, etc.)'''
        if voter not in self.votes and (self.allowed_voters == None or voter in self.allowed_voters):
            self.votes[str(voter)]=[None]*self.transferables
            self.voted.append(str(voter))
        if voter in self.votes and None in self.votes[voter] and vote in self.options and vote not in self.votes[voter]:
            self.votes[str(voter)][self.votes[str(voter)].index(None)] = str(vote)
            return True
        return False

    def tallyVotes(self):
        '''Recursion: kill me now...'''
        # print(self.dumpVotes())
        self.setModifiedBordaCounts()
        return self.recursiveTallySort(self.votes, self.options)

    def dumpVotes(self, anonymised=True):
        '''(STV) -> list
        returns everyone's votes'''
        if not anonymised:
            return [[x, self.votes[x]] for x in self.votes]
        else:
            result = list()
            count = 0
            for x in self.votes:
                result.append([int(count), list(self.votes[x])])
                count += 1
            return result

    def setModifiedBordaCounts(self):
        self.MBC = dict()
        for option in self.options:
            self.MBC[option] = 0
            for voter in self.votes:
                self.MBC[option] += self._bordaCountFromSingleBallot(self.votes[voter], option)

    def _bordaCountFromSingleBallot(self, ballot, option):
        if option not in ballot:
            return 0
        if None in ballot:
            return ballot.index(None) - ballot.index(option)
        return len(ballot) - ballot.index(option)

#    Unused:
#    def countFirsts(self, votes, options):
#        optionsCount = dict(zip(options, [0]*len(options)))
#        for voter in votes:
#            if votes[voter]!= []:
#                optionsCount[votes[voter][0]]+=1
#        output = [[optionsCount[x], x] for x in optionsCount]
#        output.sort()
#        return output

    def countVotes(self, votes, options):
        counts = list() # [[0]*self.transferables]*len(options) but copies, not pointers
        # Damn it Python why you make me do dis!? ^^^ is so much nicer and easier...
        for i in range(len(options)):
            counts.append(list())
            for j in range(self.transferables):
                counts[i].append(0)
        optionsCount = dict(zip(options, counts))
        for voter in votes:
            for i in range(len(votes[voter])):
                optionsCount[votes[voter][i]][i]+=1
        output = [[optionsCount[x], x] for x in optionsCount]
        output.sort()
        return output

    def deleteNones(self, votes):
        for voter in votes:
            while None in votes[voter]:
                del(votes[voter][votes[voter].index(None)])

    def recursiveTallySort(self, votestemp, optionstemp):
        '''(dict, list) -> list
        If this works, returns a list of options sorted by highest (winner) to lowest (least voted for)'''
        votes = dict()
        for voter in votestemp: # I give up with hoping Python mem shit will work
            votes[str(voter)]=list(votestemp[voter])
        options = list(optionstemp)
        self.deleteNones(votes)
        voteCount = self.countVotes(votes, options)
        if len(options)>1:
            possible_ties = [[self.MBC[voteCount[0][1]], voteCount[0]]]
            for i in range(1, len(options)):
                if (voteCount[i][0][0] == voteCount[0][0][0]):
                    possible_ties.append([self.MBC[voteCount[i][1]], voteCount[i]])
                else:
                    break
            possible_ties.sort() # lowest MBC first
            lowest_voted = possible_ties[0][1] # lowest_voted is list in form [votes, option]
            for voter in votes:
                if lowest_voted[1] in votes[voter]:
                    del(votes[voter][votes[voter].index(lowest_voted[1])])
            del(options[options.index(lowest_voted[1])])
            return self.recursiveTallySort(votes, options) + [[lowest_voted[1],lowest_voted[0][0]]]
        elif len(options)==1:
            return [[voteCount[0][1], voteCount[0][0][0]]]
        else: # len(options) == 0
            return ["No votes recorded"]
