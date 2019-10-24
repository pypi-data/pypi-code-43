#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sekg.term import abbr_rules


class AbbrExtractor:
    def __init__(self, **cfg):
        rule_names = cfg.get("rules", ["Rule4Bracket", "Rule4Colon"])
        self.RULES = []
        for r in rule_names:
            if not hasattr(abbr_rules, r):
                print("Has no rule:", r)
                continue
            self.RULES.append(getattr(abbr_rules, r)())

    def extract(self, sentence):
        terms = set()
        pairs = set()
        for rule in self.RULES:
            _terms, _pairs = rule.extract(sentence)
            terms.update(_terms)
            pairs.update(_pairs)
        return terms, pairs

    def process(self, sentences):
        terms = set()
        pairs = set()
        for sent in sentences:
            _terms, _pairs = self.extract(sent)
            terms.update(_terms)
            pairs.update(_pairs)

        return terms, pairs
