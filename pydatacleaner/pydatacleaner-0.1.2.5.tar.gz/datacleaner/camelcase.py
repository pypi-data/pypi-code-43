import re
from .datacleaner import *


# for tokenizing
#humps = re.compile(r'([a-z])([A-Z0-9]+)')
#numletter = re.compile(r'(\d)([a-zA-Z]+)')
#letternum = re.compile(r'([a-zA-Z])(\d)')
#acronym = re.compile(r'([A-Z]+)([A-Z]([a-r,t-z]|s(?:[a-zA-Z])))')
#alternate_acronym_re = re.compile(r'([A-Z]{2,})(\b|[a-z0-9\_])')

# for the actual creating of CamelCase, which is easy
typicalbreaks = re.compile(r'[_\s]+(\w)')

# to break apart camel case:
#[1] ACRONYM/Single Cap + s,
#[2] ACRONYM including single cap letter (not followed by a lowercase letter, because that is supposed to be #3, e.g. IDCard -> [ID, Card]),
#[3] Capitalized word ( CAP + lowercase),
#[4] initial word if it is lowerecase
tokenre = re.compile(r'([A-Z]+s(?![a-r,t-z])|[A-Z]+(?![a-z])|[A-Z][a-z_]+|[a-z_]+|[^A-Za-z_]+)(.*)')

# alternate acronym regex to break apart camel case
alttokenre = re.compile(r'([A-Z]+s(?![a-r,t-z])|[A-Z]{2,}|[A-Z][a-z_]+|[A-Z]\b|[a-z_]+|[^A-Za-z_]+)(.*)')
# Same as the above except the exclusion to being followed by a lowercase letter in #2 is eliminated, so that IDCard -> [IDC, ard], or, to use this correctly, IDcard -> [ID, card]


class CamelCase(DataCleaner):
    data_type=str
    alternate_acronym=False

    def tokenize(self, val):

        if self.alternate_acronym:
            tokenizer = alttokenre
        else:
            tokenizer = tokenre

        val = val.strip()
        result = []
        while len(val):
            m = tokenizer.match(val)
            if m:
                result.append(m.group(1))
                val = m.group(2)
            else:
                raise Exception("tokenre failed to match for " + val)
        return(result)

    def join(self, values):
        result = values[0]
        for val in values[1:]:
            result += val[0].upper() + val[1:]
        return(result)

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.add_transliterations([
                (typicalbreaks, lambda m: m.group(1).upper()),
                # what about special characters?
        ])
