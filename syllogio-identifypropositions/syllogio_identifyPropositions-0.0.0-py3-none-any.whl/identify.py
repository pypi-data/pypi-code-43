import operator
import spacy
from .util import parseClause


# TODO: make this configurable.
nlp = spacy.load("en_core_web_sm")


def identify(text):
    propositions = []
    doc = nlp(text)
    for token in doc:
        if token.dep_ == "ROOT":
            propositions = operator.add(propositions, parseClause(token))
    return propositions
