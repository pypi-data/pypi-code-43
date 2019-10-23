# -*- coding: utf-8 -*-
import re
from itertools import chain
from .token import TOKEN_TYPES, EXTENDED_TOKEN_TYPES


class ITokenizer(object):

    def tokenize(self, sentence):
        return None


class RegexTokenizer(ITokenizer):

    def __init__(self, regex_query, ignore_case=False):
        self.__p = re.compile(regex_query, re.IGNORECASE if ignore_case else 0)

    def tokenize(self, sentence):
        return self.__p.split(sentence)


class WSTokenizer(RegexTokenizer):

    def __init__(self, regex_query=r'[\f   \t\v]+'):
        super().__init__(regex_query=regex_query)


class RuleTokenizer(ITokenizer):

    PRESPLIT_PAT = re.compile(r' +')

    def __init__(self):
        self.token_regex = r'|'.join(TOKEN_TYPES)
        self.pattern = re.compile(self.token_regex)

    def __tokenize_substr(self, str_):
        for matches in self.pattern.finditer(str_):
            span = matches.span()
            yield matches.string[span[0]:span[1]]

    def tokenize(self, string_):
        return list(chain.from_iterable(map(self.__tokenize_substr, RuleTokenizer.PRESPLIT_PAT.split(string_))))


class ExtendedRuleTokenizer(ITokenizer):

    PRESPLIT_PAT = re.compile(r' +')

    def __init__(self):
        self.token_regex = r'|'.join(EXTENDED_TOKEN_TYPES)
        self.pattern = re.compile(self.token_regex)

    def __tokenize_substr(self, str_):
        for matches in self.pattern.finditer(str_):
            span = matches.span()
            yield matches.string[span[0]:span[1]]

    def tokenize(self, string_):
        return list(chain.from_iterable(map(self.__tokenize_substr, ExtendedRuleTokenizer.PRESPLIT_PAT.split(string_))))


class TokenTagger(object):

    def get_tagged_entities(self, tokens, all_=True):
        return None


class DictionaryBasedTagger(TokenTagger):

    def __init__(self, dictionary_look_up):
        self.lookup = dictionary_look_up

    def get_classes(self):
        return sorted(list(self.lookup.get_known_classes()))

    def get_tagged_entities(self, tokens, all_=False):
        max_ = self.lookup.get_longest_sequence()
        entities = list()
        toks = list(tokens)
        len_ = len(toks)
        i = 0
        while i < len_:
            j = i + max_ if i + max_ <= len_ else len_
            while j > i:
                class_ = self.lookup[toks[i:j]]
                if class_ is not None:
                    entities.append((i, j, class_))
                    if not all_:
                        i = j - 1
                        break
                j -= 1
            i += 1
        return entities


class TokenFilter(object):

    def filter(self, tokens):
        """
        Filter out tokens according to specific rules.

        :param list tokens: string list of tokens to filter
        :return: filtered list of tokens
        :rtype: list
        """
        return None


class StackingFilter(TokenFilter):
    """Class for continuous stacking and applying filters in a natural order."""

    def __init__(self, filter_list=list()):
        self.filters = list(filter_list)

    def append_filter(self, filter):
        self.filters.append(filter)

    def prepend_filter(self, filter):
        self.filters.insert(0, filter)

    def filter(self, tokens):
        for filter in self.filters:
            tokens = filter.filter(tokens)
        return tokens


class ClassTokenFilter(TokenFilter):

    def __init__(self, tagger, filtered_classes=None):
        self.__tagger = tagger
        self.filtered_classes = filtered_classes

    def filter(self, tokens):
        toks = list(tokens)
        tags = self.__tagger.get_tagged_entities(toks, all_=False)
        if self.filtered_classes:
            tags = filter(lambda t: t[2] in self.filtered_classes, tags)
        invalid_ids = set(i for start, end, _ in tags for i in range(start, end))
        return [toks[i] for i in range(0, len(toks)) if i not in invalid_ids]


