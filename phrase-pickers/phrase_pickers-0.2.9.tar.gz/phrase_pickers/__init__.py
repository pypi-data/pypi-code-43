try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print('Downloading language model for the spaCy POS tagger\n'
          "(don't worry, this will only happen once)")
    from spacy.cli import download
    download("en_core_web_sm")
