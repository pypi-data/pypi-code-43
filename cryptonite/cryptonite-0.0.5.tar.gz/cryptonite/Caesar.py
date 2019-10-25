# ONE OF THE WEAKEST FORMS OF ENCRYPTION
# ROT13 IS CAESAR ENCRYPTION WITH N=13
# ISSUES:
#   * PT structure remains intact == vulnerable to frequency analysis
#   * SMALL KEY SPACE

from bestia.output import echo
from bestia.iterate import string_to_list, iterable_to_string, LoopedList

ALPHABET = LoopedList(
    *string_to_list(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    )
)


def Alpha(c):
    return ALPHABET.index(c.upper())

def caesar(txt, n=0):
    blob = []
    for c in txt:
        if c.upper() in ALPHABET:
            if c.islower():
                c = ALPHABET[Alpha(c) + n].lower()
            else:
                c = ALPHABET[Alpha(c) + n]
        blob.append(c)

    return iterable_to_string(blob)
