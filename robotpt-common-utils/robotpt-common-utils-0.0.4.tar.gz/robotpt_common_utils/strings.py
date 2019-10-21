import random
import string


def random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.sample(letters, length))