"""
This module provides functions to pick verb words from sentence in
dependency parse tree format
"""
import csv
import json
import os
import gzip

#TODO check that this works
from phrase_pickers.np_picker import modifies_parent

UNDESIRBALE_WORDS_FN = os.path.join(
                            os.path.dirname(os.path.abspath(__file__)),
                            'res',
                            'undesirable_words.json.gz'
                        )

MORPHO_WORDS_FN = os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        'res',
                        'morpho_semantic_words.csv.gz'
                    )

### Load undesirable words ###
with gzip.open(UNDESIRBALE_WORDS_FN, 'rb') as f:
    _undesirable_words = json.load(f)
    undesirable_verbs = set(_undesirable_words['verbs'])
    undesirable_gerunds = set(_undesirable_words['gerunds'])

### Load nominalized verbs
nominalized = set()
desirable_nom_verb_types = set(["agent", "event", "by-means-of", "undergoes", "vehicle", "instrument", "added"])
with gzip.open(MORPHO_WORDS_FN, 'rt') as f:

    #TODO make this dictreader

    nm = csv.reader(f)
    next(nm)
    for row in nm:
        # column 2 is the relationship between verb and noun
        # column 3 is the verb, column 4 is the noun?
        if row[2] in desirable_nom_verb_types:
            # append the nominalized word (verby noun) to set
            nominalized.add(row[4])


# https://spacy.io/api/annotation#pos-tagging
VERB_TAGS = set(['VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VB'])
NOUN_TAGS = set(['NN', 'NNS', 'NNP', 'NNPS' ])

def get_vp_indices(dep_parse_tree):
    '''
    Finds the indices of verbs in a sentence

    Args:
        dep_parse_tree: a spacy Doc object
    Returns:
        a list of the word indices of verbs in the sentence.

    '''
    indices = []
    # loop through dependency parse tree and pick verbs
    for token_num, token in enumerate(dep_parse_tree):
        word = token.text
        lemma = token.lemma_
        pos = token.tag_
        # Include nominalized verbs, good gerunds, exclude undesirable words,
        # and verbs that are noun modifiers.
        if ((pos in VERB_TAGS and lemma not in undesirable_verbs) or
            (pos in NOUN_TAGS and lemma in nominalized) or
            (pos in NOUN_TAGS and word.endswith("ing") and lemma not in undesirable_gerunds)) \
            and not modifies_parent(token):
            indices.append(token_num)
    return indices
