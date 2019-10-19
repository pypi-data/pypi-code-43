""" this is a dummy pipeline for testing """

import logging
log = logging.getLogger()

############## model pipeline ##############################################

def make_textents():
    return "textents"

def make_nlp(textents):
    return "=>".join([textents, "make_nlp"])

############### media pipeline ####################################

def make_urls(domain, searchtext="", startperiod=0):
    return "=>".join([domain, "urls"])

def make_articles(urls):
    return "=>".join([urls, "articles"])

def make_texts(articles, textents):
    return "=>".join([articles, "texts"])

def make_docs(nlp, texts):
    return "=>".join([texts, "docs"])

def make_docents(docs, textents, media):
    return "=>".join([docs, "docents"])
