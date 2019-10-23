# -*- coding: utf-8 -*-
import re
import html
import unicodedata

from itertools import chain
from functools import partial
from operator import itemgetter

from pynlple.processing.token import EMOJI_MODIFIERS_EXTENDED
from .emojis import UnicodeClusteredEmojiProviderV11
from .token import TOKEN_TYPES, DELIMITER_TYPES, DELIMITER_CONTEXTS, \
    EMOJIS, PUNCTUATION, SPECIAL_SYMBOLS, CURRENCY, TOKEN_DEFAULT_DELIM, PURELY_EMOJI_COMPONENTS

URL_REGEX = r'((ht|f)tps?:[\\/]+|www\d{0,3}\.)([.…]+|[^\s\\/$.?#].[^\s]*)'


class IPreprocessor(object):
    """Interface to collect modules for text string preprocessing."""

    def preprocess(self, string_):
        return None


class Replacer(IPreprocessor):
    """Preprocessor interface for modules that replace certain text entities with normalized tags, etc."""


class StackingPreprocessor(IPreprocessor):
    """Class for continuous stacking and applying preprocessors in a natural order."""

    def __init__(self, preprocessor_list=None):
        if not preprocessor_list:
            self.preprocessors = []
        else:
            self.preprocessors = list(preprocessor_list)

    def append_preprocessor(self, preprocessor):
        self.preprocessors.append(preprocessor)

    def prepend_preprocessor(self, preprocessor):
        self.preprocessors.insert(0, preprocessor)

    def insert_preprocessor(self, position, preprocessor):
        self.preprocessors.insert(position, preprocessor)

    def preprocess(self, string_):
        out_string = string_
        for preprocessor in self.preprocessors:
            out_string = preprocessor.preprocess(out_string)
        return out_string


class ToLowerer(IPreprocessor):
    """Lowers all alpha characters."""

    def preprocess(self, string_):
        return string_.lower()


class CharacterUnicodeCategoryReplacer(IPreprocessor):

    WHITESPACE = ' '
    CURRENCY_SIGN = '$'
    NEWLINE = '\n'
    decimals = set(map(str, (range(10))))

    def preprocess(self, string_):
        return ''.join(filter(None, map(self.get_code, string_)))

    def get_code(self, char):
        if char in self.decimals:
            return char
        elif char in ['\r', '\n']:
            return char

        cat = unicodedata.category(char)
        if cat in ['Zs']:
            return CharacterUnicodeCategoryReplacer.WHITESPACE
        if cat in ['Zp', 'Zl']:
            return CharacterUnicodeCategoryReplacer.NEWLINE
        elif cat in ['Sc']:
            return CharacterUnicodeCategoryReplacer.CURRENCY_SIGN
        elif cat in ['Lu', 'Lt']:
            return cat[0].upper()
        elif cat[0] in ['P', 'p']:
            return char
        elif cat in ['Mc', 'Mn']:
            return None
        else:
            return cat[0].lower()


class SoftTextScissors(Replacer):
    """Cuts the end of the string in a 'soft' manner: the first whitespace after the 'soft_length' is
    sought for in reach of 'window' size rightwards. If no whitespace is present in the window, then
    the 'soft_length' of string is taken."""

    def __init__(self, soft_length=1000, window=50, whitespace_regex=r'\s'):
        self.soft_length = soft_length
        self.window = window
        self.whitespace_regex = whitespace_regex
        self.__ws_patt = re.compile(self.whitespace_regex)
        self.max_length = self.soft_length + self.window
        self.min_length = self.soft_length - self.window

    def preprocess(self, string_):
        return _find_soft_edges(string_, self.soft_length, self.min_length, self.max_length, self.__ws_patt)


def _find_soft_edges(string_, soft_length, min_length, max_length, ws_patt):
    if len(string_) > soft_length:
        ws = ws_patt.search(string_, pos=soft_length, endpos=max_length)
        if ws:
            return string_[:ws.start()]
        else:
            r_ws = ws_patt.search(string_[min_length:soft_length][::-1])
            if r_ws:
                return string_[:soft_length-r_ws.end()]
            else:
                return string_[:soft_length]
    else:
        return string_


class HeadNTailTextScissors(Replacer):
    """Cuts out the middle of the string in a 'soft' manner."""

    def __init__(self, soft_length=1000, window=50, whitespace_regex=r'\s', connector=' ... '):
        self.soft_length = soft_length
        self.window = window
        self.whitespace_regex = whitespace_regex
        self.connector = connector
        self.__ws_patt = re.compile(self.whitespace_regex)
        self.max_length = self.soft_length + self.window + len(self.connector)
        self.__half_pos = int(self.soft_length / 2)
        self.__half_window = int(self.window / 2)
        self.__half_window_max_pos = self.__half_pos + self.__half_window + 1
        self.__half_window_min_pos = self.__half_pos - self.__half_window - 1

    def preprocess(self, string_):
        if len(string_) > self.max_length:
            l_string_ = _find_soft_edges(string_, self.__half_pos, self.__half_window_min_pos, self.__half_window_max_pos, self.__ws_patt)
            r_string_ = _find_soft_edges(string_[::-1], self.__half_pos, self.__half_window_min_pos, self.__half_window_max_pos, self.__ws_patt)[::-1]
            return l_string_ + self.connector + r_string_
            # l_ws = self.__ws_patt.search(string_, pos=self.__half_pos, endpos=self.__half_window_max_pos)
            # l_ = l_ws.start() if l_ws else self.__half_pos
            # r_ws = self.__ws_patt.search(string_[::-1], pos=self.__half_pos, endpos=self.__half_window_max_pos)
            # r_ = r_ws.start() if r_ws else self.__half_pos
            # return string_[:l_] + self.connector + string_[-r_:]
        else:
            return string_


class RegexReplacer(Replacer):
    """Preprocessor. Replaces entities described by a specific regular expression from a text string
    with a stated string. Supports \n groups usage in target string."""

    def __init__(self, regex_query_string, group_string_repl_or_method, case_sensitive, use_locale, restrict_to_ascii):
        self.target = group_string_repl_or_method
        flag_1 = re.IGNORECASE if not case_sensitive else 0
        flag_2 = re.LOCALE if use_locale else 0
        flag_3 = re.ASCII if restrict_to_ascii else 0
        self.pattern = re.compile(regex_query_string, flag_1 | flag_2 | flag_3)
        super().__init__()

    def preprocess(self, string_):
        return self.pattern.sub(self.target, string_)


class RegexReplacerAdapter(RegexReplacer):

    def __init__(self, regex_query, replace_tag_with=None, case_sensitive=False, use_locale=False, restrict_to_ascii=False):
        if not replace_tag_with:
            replace_tag_with = ''
        super().__init__(regex_query, replace_tag_with, case_sensitive, use_locale, restrict_to_ascii)


def _get_bold_replacement(repl_):
    stripd_repl_ = repl_.strip()
    if len(stripd_repl_) == 0:
        return repl_, repl_, repl_, repl_
    else:
        ind_ = repl_.index(stripd_repl_)
        ind_end_ = ind_ + len(stripd_repl_)
        return (repl_,
                ''.join([repl_[:ind_], '<b>', repl_[ind_:]]),
                ''.join([repl_[:ind_end_], '</b>', repl_[ind_end_:]]),
                ''.join([repl_[:ind_], '<b>', repl_[ind_:ind_end_], '</b>', repl_[ind_end_:]]))


bold_tag_pattern = re.compile(r'</?b>')


def replace_w_bold_tag_preserved(repl_, left_bound_repl_, right_bound_repl_, left_right_bound_repl_, match):
    match_text = match.group(0)
    if '<b>' in match_text or '</b>' in match_text:
        cnt = 0
        for match in bold_tag_pattern.finditer(match_text):
            if match.group(0) == '</b>':
                cnt -= 1
            else:
                cnt += 1
        if cnt > 0:
            return left_bound_repl_
        elif cnt < 0:
            return right_bound_repl_
        else:
            return left_right_bound_repl_
    else:
        return repl_


def _get_target_func(repl_):
    return partial(replace_w_bold_tag_preserved, *_get_bold_replacement(repl_))


class BoldPreservingRegexReplacerAdapter(RegexReplacerAdapter):

    def __init__(self, regex_query, replace_tag_with=None, case_sensitive=False, use_locale=False, restrict_to_ascii=False, preserve_bold=False):
        if not preserve_bold:
            target = replace_tag_with
        else:
            target = _get_target_func(replace_tag_with)
        super().__init__(regex_query, target, case_sensitive, use_locale, restrict_to_ascii)


class MultiWhitespaceReplacer(RegexReplacerAdapter):
    """Replace numerous whitespaces (\s+) in an input string with a default single space ' '."""

    def __init__(self, replace_tag_with=' '):
        regex_query = r'\s+'
        super().__init__(regex_query, replace_tag_with)


class MultiNewLineReplacer(RegexReplacerAdapter):
    """Replace numerous newlines ([\r\n]+) in an input string with a default single newline '\r\n'."""

    def __init__(self, replace_tag_with='\r\n'):
        regex_query = r'[\r\n]+'
        super().__init__(regex_query, replace_tag_with)


class NewLineSpaceReplacer(RegexReplacerAdapter):
    """Replace numerous newlines ([\r\n]+) in an input string with a default single space ' '."""

    def __init__(self, replace_tag_with=' '):
        regex_query = r'[\r\n]+'
        super().__init__(regex_query, replace_tag_with)


class MultiInLineWhitespaceReplacer(RegexReplacerAdapter):
    """Replace numerous in-line whitespaces ([\f   \t\v]+) in an input string with a default single space ' '.
    Note: there are 3 types of spaces as represented here: https://en.wikipedia.org/wiki/Punctuation"""

    def __init__(self, replace_tag_with=' '):
        regex_query = r'[\f   \t\v]+'
        super().__init__(regex_query, replace_tag_with)


class Trimmer(Replacer):
    """Trims (or strips) heading and trailing whitespaces."""

    def preprocess(self, string_):
        return string_.strip()


class HtmlTagReplacer(RegexReplacerAdapter):
    """Replaces all tags of format <tag> and </tag> including tags with attributes and inner values: <a href='..'>."""

    def __init__(self, replace_tag_with=None):
        regex_query = r'<.*?>'
        super().__init__(regex_query, replace_tag_with)


class VKMentionReplacer(RegexReplacerAdapter):
    """Replaces the inner VK links and user mention of type '[<id>|<name>]'."""

    def __init__(self, replace_tag_with=None):
        regex_query = r'\[[\w_\-:]+\|.*?\]'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class AtReferenceReplacer(RegexReplacerAdapter):
    """Replaces the inner VK links and user mention of type '@<id>' (or '@<name>'?).
    This replacer finds only such entities which are separate words (start the line or
    have blank whitespace)"""

    def __init__(self, replace_tag_with=None):
        regex_query = r'((?<=\s)|(?<=^))@[\w_-]+'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class URLReplacer(BoldPreservingRegexReplacerAdapter):
    """Research https://mathiasbynens.be/demo/url-regex and https://gist.github.com/dperini/729294
    Since we need to increase recall of link-a-like entities in text, we adopt the algorithm with
    some possible erroneous cases.
    I used regexp from https://mathiasbynens.be/demo/url-regex by @stephenhay
    and extended with ftps, www, wwwDDD prefixes, and "\" variant of slash ("/")"""

    def __init__(self, replace_tag_with=None, preserve_bold_tag=False):
        super().__init__(URL_REGEX, replace_tag_with, False, False, False, preserve_bold_tag)


class EmailReplacer(RegexReplacerAdapter):
    """Replaces all e-mail-like entities, non-latin including. Includes length check for each entity part."""

    def __init__(self, replace_tag_with=None):
        regex_query = r'[\w0-9][\w0-9._%+-]{0,63}@(?:[\w0-9](?:[\w0-9-]{0,62}[\w0-9])?\.){1,8}[\w]{2,63}'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class UserWroteRuReplacer(RegexReplacerAdapter):
    """Replaces automatically generated sequences of citing found on forums. Grammar belike: <user> wrote <date?>:"""
# ((\d\d\s\w\w\w\s\d\d\d\d|\w+)(,\s\d\d:\d\d)?)?
    def __init__(self, replace_tag_with=None):
        regex_query = r'[^\s]+\s(\(\d\d\.\d\d\.\d\d\s\d\d:\d\d\)\s)?писал\((а|a)\)\s?((\d\d\s\w\w\w\s\d\d\d\d|\w+)(,\s\d\d:\d\d)?\s?)?:'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class DigitsReplacer(RegexReplacerAdapter):
    """Replaces all series of digits."""

    def __init__(self, multi, replace_tag_with=None):
        regex_query = r'\d+' if multi else r'\d'
        super().__init__(regex_query, replace_tag_with, False)


class CommaReplacer(RegexReplacerAdapter):
    """Replaces variations of comma taken from https://en.wikipedia.org/wiki/Punctuation.
    Symbols replaced: [,،、，] to the default ','. Please, ref to http://unicode-table.com to decode symbols."""

    DEFAULT_REPLACEMENT = ","

    def __init__(self, replace_tag_with=DEFAULT_REPLACEMENT):
        regex_query = r'[,،、，]'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class QuotesReplacer(RegexReplacerAdapter):
    """Replaces variations of single qoute (actually there are not much of them,
    but there are some look-alike symbols from the top of the unicode table
    that resemble single quotes and may be used in its function.
    So, take care when using this class. Symbols replaced: ['`ʹʻʼʽ՚‘’‚‛′‵] to the
    default [']. Please, ref to http://unicode-table.com to decode symbols."""

    DEFAULT_REPLACEMENT = '\''

    def __init__(self, replace_tag_with=DEFAULT_REPLACEMENT):
        # Some of the symbols are taken from other than punctuation.txt section
        regex_query = r'[\'`ʹʻʼʽ՚‘’‚‛′‵]'
        # This section does not contain quotes from not-punctuation.txt section
        # regex_query = r'[\'‘’‚‛′‵]'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class DoubleQuotesReplacer(RegexReplacerAdapter):
    """Replaces variations of double qoute (actually there are not much of them,
    but there are some look-alike symbols from the top of the unicode table
    that resemble double quotes and may be used in its function.
    So, take care when using this class. Symbols replaced: ["«»ʺ“”„‟″‶] to the
    default [\"]. Please, ref to http://unicode-table.com to decode symbols."""

    DEFAULT_REPLACEMENT = "\""

    def __init__(self, replace_tag_with=DEFAULT_REPLACEMENT):
        regex_query = r'["«»ʺ“”„‟″‶]'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class DoubleQuotesEscaper(RegexReplacerAdapter):
    """Escapes the double qoutes symbol with the corresponding string tag"""

    DEFAULT_REPLACEMENT = "DQTS"

    def __init__(self, replace_tag_with=DEFAULT_REPLACEMENT):
        regex_query = r'\"'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class DashAndMinusReplacer(RegexReplacerAdapter):
    """Replaces variations of dash/minus (actually there are not much of them,
    but there are some look-alike symbols from the top of the unicode table
    that resemble dash and minus and may be used in its function.
    So, take care when using this class. Symbols replaced: [-‐‑‒–—―－−] to the
    default [-]. Please, ref to http://unicode-table.com to decode symbols."""

    def __init__(self, replace_tag_with='-'):
        regex_query = r'[-‐‑‒–—―－−]'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class SoftHyphenReplacer(RegexReplacerAdapter):
    """Removes soft hyphen."""

    def __init__(self, replace_tag_with=''):
        regex_query = r'[­]'
        super().__init__(regex_query, replace_tag_with, False)


class TripledotReplacer(RegexReplacerAdapter):
    """Replaces triple dot one-symbol expression with 3 separate fullstops."""

    def __init__(self, replace_tag_with='...'):
        regex_query = r'[…]'
        super().__init__(regex_query, replace_tag_with, False)


class OpenParenthesisReplacer(RegexReplacerAdapter):

    def __init__(self, replace_tag_with='('):
        regex_query = r'[（]'
        super().__init__(regex_query, replace_tag_with, False)


class CloseParenthesisReplacer(RegexReplacerAdapter):

    def __init__(self, replace_tag_with=')'):
        regex_query = r'[）]'
        super().__init__(regex_query, replace_tag_with, False)


class QuestionMarkReplacer(RegexReplacerAdapter):

    def __init__(self, replace_tag_with='?'):
        regex_query = r'[？]'
        super().__init__(regex_query, replace_tag_with, False)


class ExclamationMarkReplacer(RegexReplacerAdapter):

    def __init__(self, replace_tag_with='!'):
        regex_query = r'[！]'
        super().__init__(regex_query, replace_tag_with, False)


class BoldTagReplacer(RegexReplacerAdapter):

    def __init__(self, replace_tag_with=''):
        regex_query = r'</?b>'
        super().__init__(regex_query, replace_tag_with, False)


class MultiPunctuationReplacer(RegexReplacerAdapter):
    """Replaces all multiple punctuation and special symbols (default keyboard set + some additional:
    ref to data/punctuation.txt, data/special_symbols.txt, data/currency.txt) with single corresponding symbol."""

    def __init__(self, replace_tag_with='\\1', max_punctuation_allowed=2, reduce_to=2):
        self.max = max_punctuation_allowed
        self.leave = reduce_to
        regex_query = r'([' + ''.join(map(re.escape, chain(PUNCTUATION, SPECIAL_SYMBOLS, CURRENCY))) + r'])\1{' + str(self.max) + ',}'
        super().__init__(regex_query, replace_tag_with * self.leave, False, False, False)


class MultiLetterReplacer(RegexReplacerAdapter):
    """Replaces multiple consecutive letters ([^\W\d_]) with a number letters of this type (thus preserving possible
    doubling/tripling of letters but reducing possible exhaustive lettterrring."""

    def __init__(self, replace_tag_with='\\1', max_letters_allowed=3, reduce_to=3):
        self.max = max_letters_allowed
        self.leave = reduce_to
        regex_query = r'([^\W\d_])\1{' + str(self.max) + ',}'
        super().__init__(regex_query, replace_tag_with * self.leave, False, False, False)


class NonWhitespaceAlphaNumPuncSpecSymbolsAllUnicodeReplacer(RegexReplacerAdapter):
    """Removes all unicode NON alpha-numeric, punctuation and special symbols (default keyboard set + some additional:
    ref to data/punctuation.txt, data/special_symbols.txt, data/currency.txt), whitespaces and emojis."""

    def __init__(self, replace_tag_with=''):
        regex_query = r'[^\s\w' + ''.join(map(re.escape, chain(PUNCTUATION, SPECIAL_SYMBOLS, CURRENCY, PURELY_EMOJI_COMPONENTS))) + ']'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class NonWordOrNumberOrWhitespaceAllUnicodeReplacer(RegexReplacerAdapter):
    """This cannot handle _ correctly. This also cannot handle soft hyphen correctly."""

    def __init__(self, replace_tag_with=' '):
        parts = [
            r'(?<=\d)[,:\.](?!\d)|(?<!\d)[,:\.](?=\d)|(?<!\d)[,:\.](?!\d)',  # this leaves out digital sequences with , : . in middle
            r'(?<=[\w\d])[\'\-](?![\w\d])|(?<![\w\d])[\'\-](?=[\w\d])|(?<![\w\d])[\'\-](?![\w\d])',  # this leaves out alphanumeric tokens with - and ' in middle
            r'[^\s\w\d\'\-,:\.]+',  # all other non-whitespace, non-alpha and non-digits
            r'_',
            ]
        regex_query = r'(' + r'|'.join(parts) + r')+'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class WordTokenizer(RegexReplacer):
    """"""

    PRESPLIT_PAT = re.compile(r' +')

    def __init__(self, token_delim=TOKEN_DEFAULT_DELIM):
        # token_types = TOKEN_TYPES
        self.token_regex = r'|'.join(TOKEN_TYPES)
        self.delimiter = token_delim
        self.pattern = re.compile(self.token_regex)

    def __tokenize_substr(self, str_):
        for matches in self.pattern.finditer(str_):
            span = matches.span()
            yield matches.string[span[0]:span[1]]

    def preprocess(self, string_):
        return self.delimiter.join(chain.from_iterable(map(self.__tokenize_substr, WordTokenizer.PRESPLIT_PAT.split(string_))))


class MinimalWordTokenizer(IPreprocessor):
    """"""

    PRESPLIT_PAT = re.compile(r' +')

    def __init__(self, token_delim=TOKEN_DEFAULT_DELIM):
        regex = r'|'.join(TOKEN_TYPES[:-1])
        self.pattern = re.compile(regex)
        self.delimiter = token_delim

    def __find_tokens(self, str_):
        offset = 0
        length = len(str_)
        for matches in self.pattern.finditer(str_):
            span = matches.span()
            start = span[0]
            if offset != start:
                for c in str_[offset:start]:
                    yield c
            end = span[1]
            offset = end
            yield str_[start:end]
        if offset != length:
            for c in str_[offset:length]:
                yield c

    def preprocess(self, string_):
        return self.delimiter.join(chain.from_iterable(map(self.__find_tokens, self.PRESPLIT_PAT.split(string_))))


class DelimiterTokenizer(IPreprocessor):
    """"""

    TOKEN_DEFAULT_DELIM = ' '
    PRESPLIT_PAT = re.compile(r' +')

    def __init__(self, token_delim=TOKEN_DEFAULT_DELIM):
        delims = DELIMITER_TYPES
        regex_query = r'(' + '|'.join(delims) + ')'
        self.pattern = re.compile(regex_query)
        self.delimiter = token_delim

    def preprocess(self, string_):
        return self.delimiter.join(
            chain.from_iterable(
                map(
                    partial(filter, None),
                    map(self.pattern.split, self.PRESPLIT_PAT.split(string_))
                )
            )
        )


class DelimiterFindingTokenizer(IPreprocessor):

    PRESPLIT_PAT = re.compile(r' +')

    def __init__(self, token_delim=TOKEN_DEFAULT_DELIM):
        delims = DELIMITER_CONTEXTS
        regex_query = r'|'.join(delims)
        self.pattern = re.compile(regex_query)
        self.delim=token_delim

    def __find_tokens(self, str_):
        splits = {0, len(str_)}
        for matches in self.pattern.finditer(str_):
            for i in range(1, len(matches.regs)):
                span = matches.span(i)
                if span != (-1,-1):
                    splits.add(span[0])
                    splits.add(span[1])
        splits = list(sorted(splits))
        for s, e in zip(splits[:-1], splits[1:]):
            yield str_[s:e]

    def preprocess(self, string_):
        return self.delim.join(
            chain.from_iterable(
                map(
                    partial(filter, None),
                    map(self.__find_tokens, self.PRESPLIT_PAT.split(string_))
                )
            )
        )


class HtmlEntitiesEscaper(Replacer):

    def preprocess(self, string_):
        return html.escape(string_)


class HtmlEntitiesUnescaper(Replacer):

    def preprocess(self, string_):
        return html.unescape(string_)


class PhoneNumberReplacer(RegexReplacerAdapter):
    """Replaces the phone-number-looking entities."""

    def __init__(self, replace_tag_with=' phoneNumberTag '):
        regex_query = r'(?<!\d)(\+?\d{1,3})?[\(\- ]+\d{3,4}[\)\- ]+\d{2,3}[\- ]?[\d\- ]{4}\d(?!\d)'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class PriceReplacer(RegexReplacerAdapter):
    """Replaces the money entities with a corresponding tag. Encircles the name of the currency."""

    def __init__(self, replace_tag_with=' moneyAmountTag '):
        regex_query = r'[\d.]+(\s)?(?:р|грн|руб|рублей|рубля|EUR|' + '|'.join(map(re.escape, CURRENCY)) + r')\s*[\s.]'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class EmojiLemmatizer(RegexReplacerAdapter):

    def __init__(self,):
        super().__init__(r'[' + ''.join(map(re.escape, EMOJI_MODIFIERS_EXTENDED)) + r']', '', False, False, False)


class EmojiReplacer(RegexReplacerAdapter):
    """Replaces emojis (from unicode table) with the corresponding tag.
    Emoji list is taken from https://github.com/carpedm20/emoji"""
    def __init__(self, replace_tag_with=' emojiTag '):
        super().__init__(r'(' + '|'.join(map(re.escape, EMOJIS)) + r')', replace_tag_with, False, False, False)


class EmojiClusterReplacer(RegexReplacerAdapter):
    """Replaces emojis (from unicode table) with the corresponding tag and cluster name.
    Note the name of the cluster is a number."""

    def __init__(self, tag_prefix=' emojiTag '):
        self.raw_tag_prefix = tag_prefix
        self.tag_prefix = tag_prefix.strip()
        s = tag_prefix.index(self.tag_prefix)
        e = s + len(self.tag_prefix)

        self.emoji_tags = dict((emoji, self.raw_tag_prefix[:s] + cluster + self.raw_tag_prefix[e:]) for emoji, cluster in UnicodeClusteredEmojiProviderV11(self.tag_prefix))

        def select_tag(match):
            match_text = match.group(0)
            return self.emoji_tags.get(match_text, self.raw_tag_prefix)

        super().__init__(r'(' + '|'.join(map(re.escape, map(itemgetter(0), self.emoji_tags.items()))) + r')', select_tag)


class DefaultPreprocessorStack(StackingPreprocessor):
    def __init__(self, preserve_newlines=True, soft_cut=None):
        self.preserve_nl = preserve_newlines
        stack = [
            HtmlEntitiesUnescaper(),
            BoldTagReplacer(),
            HtmlTagReplacer(' '),
            URLReplacer(' urlTag '),
            VKMentionReplacer(' vkMentionTag '),
            EmailReplacer(' emailTag '),
            PhoneNumberReplacer(' phoneNumberTag '),
            AtReferenceReplacer(' atRefTag '),
            UserWroteRuReplacer(' userWroteRuTag '),
            CommaReplacer(),
            QuotesReplacer(),
            DoubleQuotesReplacer(),
            SoftHyphenReplacer(),
            DashAndMinusReplacer(),
            OpenParenthesisReplacer(),
            CloseParenthesisReplacer(),
            QuestionMarkReplacer(),
            ExclamationMarkReplacer(),
            TripledotReplacer(),
            NonWhitespaceAlphaNumPuncSpecSymbolsAllUnicodeReplacer(''),
            ToLowerer(),
            DigitsReplacer(False, '0'),
            MultiPunctuationReplacer(),
            MultiLetterReplacer(),
            MultiNewLineReplacer(),
            MultiInLineWhitespaceReplacer() if self.preserve_nl else MultiWhitespaceReplacer(),
            WordTokenizer(),
            Trimmer(),
            # Any other?
        ]
        if soft_cut:
            stack.insert(3, soft_cut)
        super().__init__(stack)


class ExtendedReplacerStack(DefaultPreprocessorStack):
    """
    Creates an extended (by appending to the end) instance of preprocessor.DefaultPreprocessorStack.

    @:param list list_extension_replacers: a list of preplacers to extend the default set with
    """
    def __init__(self, list_extension_replacers):
        super().__init__()
        self.extension_replacers = list_extension_replacers
        for replacer in self.extension_replacers:
            super().append_preprocessor(replacer)

