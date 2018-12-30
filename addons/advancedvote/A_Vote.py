from libs import command, savetome

VOTE_DICT_LOCATION='votedictloc'
BALLOT_LOCATION='ballotloc'

class Command(command.Dummy, command.Config):
    '''Dummy voting command for initializing the namespace

Why are you reading this?

Please ignore'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.public_namespace.vote_dict=savetome.load_vote_dict(self.config[VOTE_DICT_LOCATION])
        self.public_namespace.ballot=savetome.load_ballot(self.config[BALLOT_LOCATION])

    def shutdown(self):
        savetome.save_vote_dict(self.config[VOTE_DICT_LOCATION], self.public_namespace.vote_dict)
        savetome.save_ballot(self.config[BALLOT_LOCATION], self.public_namespace.ballot)
