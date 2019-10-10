import random
import string


def get_random_string(charset=None, require_length=10):
    if charset is None:
        charset = string.ascii_letters + string.digits
    return ''.join([random.choice(charset) for _ in range(require_length)])
