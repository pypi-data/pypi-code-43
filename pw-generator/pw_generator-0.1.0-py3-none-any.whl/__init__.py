#!/usr/bin/env python3

try:
    from secrets import choice
except ImportError:
    from random import choice

from .wordlist_4k import wordlist_4k
from .charlists import charsets, separators

from pwgen.exception import WeakPasswordException

#----------------------------------------------------------------------#
def passphrase_gen(wcount = 3):
    if wcount < 3:
        raise WeakPasswordException("Too weak password: {} words".format(wcount))

    password_list = []

    while True:
        wcount -= 1
        password_list.append(choice(wordlist_4k))
        if wcount:
            password_list.append(choice(separators))
        if not wcount:
            break

    return "".join(password_list)

def password_gen(ccount):
    if ccount < 8:
        raise WeakPasswordException("Too weak password: {} characters".format(ccount))

    charlist = "".join(charsets)
    password = ""
    
    while True:
        cs_missed = (1 << len(charsets)) - 1
        password = "".join(choice(charlist) for i in range(ccount))

        i = 0
        for cs in charsets:
            if any(c in cs for c in password):
                cs_missed ^= (1 << i)
                i += 1
        if not cs_missed:
            break

    return password

#----------------------------------------------------------------------#
if __name__ == '__main__':
    print("Don't use it directly!")
