import re
from .datacleaner import *



class SnakeCase(DataCleaner):
    # the default column normalizer converts null column headers to '<blank>', but note this open happens if blank column headers do not occur at the end, as those would be stripped away
    convert_numbers=False
    data_type=str

    #convert all whitespace of any length to a single space
    def clean(self, val):
        return(super().clean(val).lower())

    def tokenize(self, val):
        return(val.split('_'))

    def join(self, values):
        return('_'.join([str(v).lower() for v in values]))

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # most of the rest of this handles transliterations to change the field to snake case.
        self.add_transliterations([
            #(r'\s+', '_'),
            (acronymre, underscorejoin),
            (camelre, underscorejoin),
            (interiornum, underscorejoin),
            (precedingnum, underscorejoin),
        # remove any preceding or succeeding underscores
            (r'[\_\s]+', '_'),
            (r'^\_+', ''),
            (r'\_+$', ''),
        ])
