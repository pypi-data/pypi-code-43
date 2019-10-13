import operator
import spacy
from .util import parseClause
from .config import get

nlp = spacy.load(get("model_name", "en_core_web_sm"))


def identify(text):
    propositions = []
    doc = nlp(text)
    for token in doc:
        if token.dep_ == "ROOT":
            propositions = operator.add(propositions, parseClause(token))
    return propositions
