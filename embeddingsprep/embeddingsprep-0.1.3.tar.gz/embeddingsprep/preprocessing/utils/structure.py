"""
#                                Structure Utils

Functions changing the text data structure
"""

from nltk import ngrams
from collections import Counter


def melt_vocab_dic(vocab1, vocab2):
    """Melts vocab dictionnary by adding the counts of each words.
    Vocab dictionnaries must be s.t.:
    vocab = {'word' : count_occurencies_word}
    Args:
        vocab1 : dic
        vocab2 : dic
    Returns:
        vocab : dic
    """
    for word in vocab2:
        if word in vocab1:
            vocab1[word] = vocab1[word] + vocab2[word]
        else:
            vocab1[word] = vocab2[word]
    return vocab1


def get_unigram_voc(text):
    """
    Builds a dictionnary, batch per batch, of unique unigrams & their
    occurences.
    Args:
        text : str
            a text that is assumed to be cleaned with the preprocessors cleaning
            method
    Returns:
        vocabulary : dic
            a dictionnary {'word' : count_word}
    """
    words = text.split(" ")  # That's where we assume the text has been
    # cleaned with the cleaning method, otherwise the 'split' leads to bad
    # tokenisation
    vocabulary = dict(Counter(words))
    del words  # Avoids out of memory problems while multiprocessing
    return vocabulary


def get_bigram_voc(text, parsing_char):
    """
    Builds a dictionnary, of unique bigrams & their occurences.
    Args:
        text : str
            a text that is assumed to be cleaned with the preprocessor cleaning
            method
    Returns:
        vocab : dic
            a dictionnary {'bigram' : count_bigram}
    """
    words = text.split(" ")
    bigrams = ngrams(words, 2)
    big_list = []
    for i in bigrams:
        big_list.append(parsing_char.join(i))
    vocabulary = dict(Counter(big_list))
    del bigrams
    del words
    del big_list
    return vocabulary
