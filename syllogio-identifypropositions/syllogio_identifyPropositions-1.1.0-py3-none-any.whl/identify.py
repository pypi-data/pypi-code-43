import operator
import spacy
from .util import parseClause
from .config import get


def identify(text, model_name=get("model_name", "en_core_web_sm")):
    nlp = spacy.load(model_name)
    propositions = []
    doc = nlp(text)
    for token in doc:
        if token.dep_ == "ROOT":
            propositions = operator.add(propositions, parseClause(token))
    return propositions
