import random
import string
from Crypto.Random import random as cryptorandom

import logging
logger = logging.getLogger(__name__)


def random_string(size=8, upper=True, lower=False, digits=True , secure=False):
    space = []
    if upper:
        space += string.ascii_uppercase
    if lower:
        space += string.ascii_lowercase
    if digits:
        space += string.digits
    if  len(space) == 0:
        raise ValueError("At least one of (upper, lower, digits) should be True!")
    if secure:
        _random = cryptorandom
    else:
        _random = random
    return ''.join(_random.choice(space) for i in range(size))


def random_secure_string(size=64):
    return random_string(size, upper=True, lower=True, digits=True , secure=True)
