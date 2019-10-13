import operator
import spacy
import os
from .util import parseClause
from configparser import ConfigParser

configParser = ConfigParser()
configParser.read([os.path.join(os.getcwd(), "setup.cfg")])
modelName = configParser.get("syllogio-identifyPropositions", "model_name")


nlp = spacy.load(modelName)


def identify(text):
    propositions = []
    doc = nlp(text)
    for token in doc:
        if token.dep_ == "ROOT":
            propositions = operator.add(propositions, parseClause(token))
    return propositions
