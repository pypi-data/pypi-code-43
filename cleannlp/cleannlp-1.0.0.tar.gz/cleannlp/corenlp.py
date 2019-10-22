# -*- coding: utf-8 -*-
"""Use the coreNLP library to extract linguistic features.
"""

import os
import sys
from warnings import catch_warnings, simplefilter

import stanfordnlp


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


class corenlpCleanNLP:
    """A class to call spacy and output normalized tables"""

    def __init__(self, lang='en', models_dir=None):
        if models_dir is None:
            models_dir = default_model_dir()

        with HiddenPrints():
            with catch_warnings():
                simplefilter("ignore")
                try:
                    self.nlp = stanfordnlp.Pipeline(
                        lang=lang,
                        models_dir=models_dir
                    )
                except KeyError as e:
                    self.nlp = None

    def parseDocument(self, text, doc_id):
        with catch_warnings():
            simplefilter("ignore")
            doc = self.nlp(text)

        token = get_token(doc, doc_id)

        return {"token": token}


def get_token(doc, doc_id):
    token = {
        "doc_id": [],
        "sid": [],
        "tid": [],
        "token": [],
        "lemma": [],
        "upos": [],
        "xpos": [],
        "feats": [],
        "tid_source": [],
        "relation": []
    }

    sid = 1
    for x in doc.sentences:

        # Now, parse the actual tokens, starting at 1
        tid = 1
        for word in x.words:

            token['doc_id'].append(doc_id)
            token['sid'].append(sid)
            token['tid'].append(tid)
            token['token'].append(word.text)
            token['lemma'].append(word.lemma)
            token['upos'].append(word.upos)
            token['xpos'].append(word.pos)
            token['feats'].append(word.feats)
            token['tid_source'].append(word.governor)
            token['relation'].append(word.dependency_relation)

            tid += 1

        sid += 1

    return token


def default_model_dir():
    return stanfordnlp.utils.resources.DEFAULT_MODEL_DIR
