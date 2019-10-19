from .code import get_file as __get_file

def lexicon():
    return __get_file("words.json")

def feature_lists():
    return __get_file("featurelists.json")

def feature_types():
    return __get_file("featuretypes.json")

def lexicon_pos():
    return __get_file("lexicon_lf.json")

def ontology():
    return __get_file("ontology.json")

def syntax_templates():
    return __get_file("syntax_templates.json")
