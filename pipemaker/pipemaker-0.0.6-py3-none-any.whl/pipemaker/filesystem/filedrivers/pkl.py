import pickle
import logging
log = logging.getLogger()

def save(self, obj):
    """ save a pickle file """
    pickle.dump(obj, self.open("wb"))

def load(self):
    """ load a pickle file """
    return pickle.load(self.open("rb"))