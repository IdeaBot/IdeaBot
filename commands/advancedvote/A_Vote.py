from libs import command, savetome

DEFAULT='DEFAULT'
VOTE_DICT_LOCATION='votedictloc'
BALLOT_LOCATION='ballotloc'

class Command(command.Multi, command.Dummy, command.Config):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config.content = self.config.content[DEFAULT]
        self.public_namespace.vote_dict=savetome.load_vote_dict(self.config.content[VOTE_DICT_LOCATION])
        self.public_namespace.ballot=savetome.load_ballot(self.config.content[BALLOT_LOCATION])

    def shutdown(self):
        savetome.save_vote_dict(self.config.content[VOTE_DICT_LOCATION], self.public_namespace.vote_dict)
        savetome.save_ballot(self.config.content[BALLOT_LOCATION], self.public_namespace.ballot)
