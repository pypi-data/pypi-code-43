import operator
import spacy
from .util import parseClause
from .config import get


def identify(text, model_name=get("model_name", "en_core_web_sm")):
    nlp = spacy.load(model_name)
    doc = nlp(text)
    propositions = []
    for sent in doc.sents:
        propositions = operator.add(propositions, parseClause(sent.root))
    return list(map(lambda s: s.text, propositions))
