"""
Utils for Word2Vec wrapper
"""
import json


def read_files(filenames):
    """
    Reads a file line by line
    Args:
        filenames : list of str
            a list of string containing the paths to the files used to learn the
            embeddings
    Returns:
        sents : list of list of str
            a list containing the words, line per line
    """
    sents = []
    for file in filenames:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                sents.append(line.replace("\n", "").split(" "))
    return sents


def open_vocab(vocab_path):
    """
    Opens the json containing the vocabulary used for the word2vec
    Args:
        vocab_path : str
            the path where the vocab json file is stored
    Returns:
        vocab_dic : dic
            the vocab dictionnary
    """
    with open(vocab_path, "r", encoding="utf-8") as vo:
        vocab_dic = json.load(vo, encoding="utf-8")
    return vocab_dic
