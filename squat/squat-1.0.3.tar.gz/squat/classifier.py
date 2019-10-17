#!/usr/bin/env python
# coding: utf8
"""SQUAT Text classifier usecase.

__author__ = "Binay Kumar Ray"
__copyright__ = "Copyright 2019, Standard Chartered Bank"
__version__ = "0.1.9"
__email__ = "binaykumar.ray@sc.com"
__status__ = "Hackathon"

This is an usecase for loading the ML model and
using it directly instead of training every time we want to use it:
* Training: https://spacy.io/usage/training

Compatible with: spaCy v2.0.0+
"""
from __future__ import unicode_literals, print_function
import spacy


def main(text):
    output_dir = "Classifier/out"
    # test the saved model
    print("Loading from", output_dir)
    nlp2 = spacy.load(output_dir)
    # for text, _ in TRAIN_DATA:
    doc = nlp2(text)
    print(text, doc.cats)


if __name__ == "__main__":
    main("CASH DEPOSIT")