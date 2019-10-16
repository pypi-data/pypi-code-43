#!/usr/bin/env python
# -*- coding: utf-8 -*-


from sekg.term.abbr import AbbrExtractor

if __name__ == "__main__":
    extractor = AbbrExtractor()
    terms, pairs = extractor.extract("For example, feed forward neural networks are comprised of dense layers, while recurrent neural networks can include Graves LSTM (long short-term memory) layers.")
    print(terms, pairs)