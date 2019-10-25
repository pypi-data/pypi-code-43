"""
This module provides functions to pick noun phrases from sentence in
dependency parse tree format
"""

import itertools
import os
import gzip

STOPWORDS_FN = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    'res',
                    'stopwords.txt.gz'
                )

with gzip.open(STOPWORDS_FN,'rb') as f:
    stop = set([x.strip().lower() for x in f])

def get_modifiers(token):
    '''
    Collects everything that modifies the token in question, grouped by the way
    they are conjugaged. For instance, "We sell red and blue cars" would return
    [[red], [blue]] when given "cars" as token.

    Args:
        token: a spacy token, the noun being considered
    Returns:
        a list of lists  of spacy tokens
    '''
    conj_groups = get_conj_groups(token)
    # compounds should be attached to the token in every distribution of
    # conjunct modifiers
    compounds = get_compounds(token)
    out = []
    if conj_groups:
        # distribute over conjunctions
        for modifiers in itertools.product(*conj_groups):
            # creates the output, i.e. a list of lists where all of the
            # modifiers in each conjunction group are stuck together
            out += [compounds + list(modifiers) + mod_modifiers for modifier in modifiers for mod_modifiers in get_modifiers(modifier)]
    else:
        return [compounds]
    return out

def remove_postpositives(root_token, mod_group):
    '''
    Removes modifiers (e.g. adjectives) that appear after the noun that they
    modify in the sentence (root_token).

    Args:
        root_token: a spacy token
        mod_group: a list of spacy tokens
    Returns:
        A list of spacy tokens
    '''
    return [mod for mod in mod_group if mod.i <= root_token.i]

def get_conj_groups(token):
    '''
    Takes a token and returns its modifiers, grouped by their conjunction
    structure. This informs how they ought to be distributed.

    For example, in the sentence "We build big and small racing and consumer
    cars," the conj groups would be [[big, small], [racing, consumer]], because
    the phrases you want to pick out are "big racing cars," "small racing
    cars," "big consumer cars," and "small consumer cars."

    Args:
        token: a spacy token
    Returns:
        a list of listss of spacy tokens
    '''
    conj_groups = []
    for child in token.children:
        if modifies_parent(child, stop_token=token):
            conj_children = [subchild for subchild in child.children if subchild.dep_ == 'conj']
            conj_group = [child]
            while conj_children:
                conj_group.append(conj_children[0])
                conj_children = [subchild for subchild in conj_group[-1].children if subchild.dep_ == 'conj']
            if len(conj_group) > 1:
                conj_groups.append(conj_group)
    return conj_groups

def get_compounds(token):
    '''
    For a token, returns a list of compounds, i.e. modifiers that should stick
    with the root token when distributing over conjunctions

    For example, in the sentence "We build big and small oil rigs," the only
    compound for "rigs" should be "oil" because the phrases you should pick out
    are "big oil rigs" and "small oil rigs".

    Args:
        token: a spacy token
    Returns:
        A list of spacy tokens
    '''
    out = []
    conj_groups = get_conj_groups(token)
    for child in token.children:
        # https://spacy.io/api/annotation#dependency-parsing
        if child.dep_.lower() in ['compound', 'amod', 'advmod', 'npadvmod', 'nn']:
            if child.text.lower() not in stop:
                if not any([child in conj_group for conj_group in conj_groups]):
                    out.append(child)
                    out += get_compounds(child)
    return out

def tokens_to_indices(tokens):
    '''
    Converts a list of spacy tokens to a list of their indices in the sentence
    as ints

    Args:
        tokens: a lits of spacy tokens
    Returns:
        a list of ints
    '''
    return tuple([token.i for token in tokens])

def deconj_dep(token, stop_token=None):
    '''
    If a token is conjunct to another token, it gets the "conj" dependency,
    which hides the relationship it has with the token outside of the
    conjunction group. This function traces up all of the "conj" dependencies
    to find that relationship.

    Args:
        token, stop_token: spacy tokens
    Returns:
        a string representing the dependency type
    '''
    while token.dep_ in ['conj'] and token.head is not stop_token:
        token = token.head
    return token.dep_

def modifies_parent(token, stop_token=None):
    '''
    Determines whether the given token modifies its parent, i.e. its dependency
    type is one of a handful of pre-selected modifier types.

    Args:
        token, stop_token: spacy tokens
    Returns:
        boolean
    '''
    # https://spacy.io/api/annotation#dependency-parsing
    return deconj_dep(token, stop_token) in ['nmod', 'compound', 'amod', 'advmod', 'npadvmod', 'nn'] and token.text.lower() not in stop

def get_np_indices(sentence):
    '''
    Picks out noun phrases from a sentence using the spacy parse tree
    Args:
        sentence: a list of spacy parsed tokens
    Returns:
        A list of tuples where each tuple represents a noun phrase in the sentence.
        The numbers within the tuple indicate the indices of the tokens that
        comprise the tuple.
    '''
    out = []
    for root_token in sentence:
        # Look for top level nouns
        # https://spacy.io/api/annotation#section-pos-tagging
        if root_token.pos_ == 'NOUN':
            if not modifies_parent(root_token):
                modifiers = get_modifiers(root_token)
                modifiers = [remove_postpositives(root_token, mod_group) for mod_group in modifiers]
                if modifiers:
                    out += [[root_token] + modifier_group for modifier_group in modifiers]
                else:
                    out.append([root_token])

    # sort tokens within phrases
    out = [[token for token in sentence if token in phrase] for phrase in out]
    # strip NERTS from the phrase
    out = [[token for token in phrase if not token.ent_type_] for phrase in out]
    if out:
        # convert to indices
        out = [tokens_to_indices(phrase) for phrase in out]
        # remove duplicates
        out = set(map(tuple, out))
    return out
