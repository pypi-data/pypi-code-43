from qai.cleantext import Cleantext

def scan_tokens(token):
    return str(token.dep_) in ["auxpass", "csubjpass", "nsubjpass"]

def is_passive_voice(phrase):
    sent = Cleantext(use_spacy=True).segment_sentences(phrase)
    passive = False
    for token in sent[0]:
        if scan_tokens(token):
            passive = True
    
    return passive
