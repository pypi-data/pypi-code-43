"""

"""

import csv
import codecs

__author__ = ["Clément Besnier <clemsciences@aol.com>", ]


def read_export(filename):
    with codecs.open(filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        return {row[1]: [tokenize(sent) for sent in sentence_delimit(row[2])] for row in reader if len(row) > 2}


def sentence_delimit(text):
    return [token for token in text.split("·")]


def tokenize(text):
    return [token for token in text.split(" ") if token]


def render_text():
    pass
