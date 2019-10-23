# -*- coding: utf-8 -*-
from pynlple.module import abs_path
from pynlple.processing.dictionary import DictionaryLookUp, FileFolderTokenMapping
from pynlple.processing.text import ClassTokenFilter, TokenFilter, DictionaryBasedTagger
import re
from operator import contains
from functools import partial


class MustContainTokenFilter(TokenFilter):

    def __init__(self, all_substring_set=None, any_substring_set=None,):
        self.all_set = all_substring_set
        self.any_set = any_substring_set

    def filter(self, list_):
        return filter(self.__contains, list_)

    def __contains(self, string_):
        return any(map(partial(contains, self.any_set), string_)) if self.any_set else True and \
            all(map(partial(contains, self.all_set), string_)) if self.all_set else True


class DictionaryStopwordsFilter(ClassTokenFilter):

    def __init__(self, stopwords_provider, prep=None):
        self.__stopwords_provider = stopwords_provider
        self.__dictionary = DictionaryLookUp(self.__stopwords_provider, preprocessing_method=prep)
        self.__tagger = DictionaryBasedTagger(self.__dictionary)
        super().__init__(self.__tagger)


class PunctuationFilter(DictionaryStopwordsFilter):
    """
    Dictionary-based punctuation filter. Uses punctuation from `data/punctuation.txt`.

    Example usage::

    >>> filter_ = PunctuationFilter()
    >>> filter_.filter('Some , tokens ! and . punctuation !'.split())
    ['Some', 'tokens', 'and', 'punctuation']

    """

    def __init__(self, prep=None):
        self.__stopwords_provider = FileFolderTokenMapping(
            ['punctuation.txt'],
            data_folder=abs_path(__file__, 'data'),
            recursive=False)
        super().__init__(self.__stopwords_provider, prep)


class SpecialSymbolFilter(DictionaryStopwordsFilter):

    def __init__(self, prep=str.lower):
        self.__stopwords_provider = FileFolderTokenMapping(
            ['special_symbols.txt'],
            data_folder=abs_path(__file__, 'data'),
            recursive=False)
        super().__init__(self.__stopwords_provider, prep)


class BaseSymbolFilter(DictionaryStopwordsFilter):

    def __init__(self, prep=None):
        self.__stopwords_provider = FileFolderTokenMapping(
            ['punctuation.txt', 'special_symbols.txt'],
            data_folder=abs_path(__file__, 'data'),
            recursive=True)
        super().__init__(self.__stopwords_provider, prep)


class CurrencyFilter(DictionaryStopwordsFilter):

    def __init__(self, prep=str.lower):
        self.__stopwords_provider = FileFolderTokenMapping(
            ['currency.txt'],
            data_folder=abs_path(__file__, 'data'),
            recursive=False)
        super().__init__(self.__stopwords_provider, prep)


class SpecialTagFilter(DictionaryStopwordsFilter):

    def __init__(self, prep=str.lower):
        self.__stopwords_provider = FileFolderTokenMapping(
            ['special_tags.txt'],
            data_folder=abs_path(__file__, 'data'),
            recursive=False)
        super().__init__(self.__stopwords_provider, prep)


class SymbolFilter(DictionaryStopwordsFilter):

    def __init__(self, prep=None):
        self.__stopwords_provider = FileFolderTokenMapping(
            ['punctuation.txt', 'special_symbols.txt', 'currency.txt'],
            data_folder=abs_path(__file__, 'data'),
            recursive=True)
        super().__init__(self.__stopwords_provider, prep)


class DefaultRussianStopwordsFilter(DictionaryStopwordsFilter):

    def __init__(self, prep=None):
        self.__stopwords_provider = FileFolderTokenMapping(
            {'rus/pos': ['conjunctions.txt', 'particles.txt', 'prepositions.txt', 'pronouns.txt']},
            data_folder=abs_path(__file__, 'data'),
            recursive=True)
        super().__init__(self.__stopwords_provider, prep)


class RegexFilter(TokenFilter):

    def __init__(self, regex):
        self.__regex = regex
        self.__pattern = re.compile(self.__regex)

    def filter(self, tokens):
        return list(filter(lambda t: not self.__pattern.match(t), tokens))


class NumberTokenFilter(RegexFilter):

    def __init__(self, num_regex=r'^[\.]?[\d][\d\.,\-:]*$'):
        super().__init__(num_regex)


class LengthTokenFilter(TokenFilter):

    def __init__(self, min_length):
        self.min_length = min_length
        self.__b = self.min_length - 1

    def filter(self, tokens):
        return list(filter(lambda x: len(x) > self.__b, tokens))