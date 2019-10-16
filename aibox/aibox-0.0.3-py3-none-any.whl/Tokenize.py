#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: Tokenize.py
# Author: Junyi Li
# Mail: cheneyjunyi@gmail.com
# Created Time: 2019-10-16 13:08:50 AM
#############################################


import re
import nltk
import string


# to replace punctuation with blank
pat_letter = re.compile(r'[^a-zA-Z0-9 ,.?!]')

# to find the 's following the pronouns. re.I is refers to ignore case
pat_is = re.compile(r"\b(it|he|she|that|this|there|here)(\'s)\b", re.I)

# to find can't
pat_can = re.compile(r'\b(can\'t)\b')

# to find won't
pat_won = re.compile(r'\b(won\'t)\b')

# to find the abbreviation of not
pat_not = re.compile(r"(?<=[a-zA-Z])n\'t\b")

# to find the abbreviation of would
pat_would = re.compile(r"(?<=[a-zA-Z])\'d\b")

# to find the abbreviation of will
pat_will = re.compile(r"(?<=[a-zA-Z])\'ll\b")

# to find the abbreviation of am
pat_am = re.compile(r"(?<=[I|i])\'m\b")

# to find the abbreviation of are
pat_are = re.compile(r"(?<=[a-zA-Z])\'re\b")

# to find the abbreviation of have
pat_ve = re.compile(r"(?<=[a-zA-Z])\'ve\b")

special_string = \
    ['&#34;', '&quot;', '&amp;', '&iexcl;', '&deg;', '&nbsp;', '&yuml;', '&para;', '&copy;', '&bull;', '&ETH;', '&reg;',
     '&oacute;', '&otilde;', '&dagger;', '&egrave;', '&scaron;', '&aacute;', '&not;', '&lrm;', '&iuml;', '&OElig;',
     '&agrave;', '&euml;', '&plusmn;', '&middot;', '&Acirc;', '&gt;', '&pound;', '&szlig;', '&iacute;', '&uacute;',
     '&euro;', '&fnof;', '&acute;', '&ordm;', '&ocirc;', '&Agrave;', '&Aacute;', '&Auml;', '&uuml;', '&Uuml;', '&shy;',
     '&Omega;', '&uml;', '&Prime;', '&ecirc;', '&Ecirc;', '&iquest;', '&laquo;', '&eacute;', '&Atilde;',
     '&alpha;', '&lt;', '&curren;', '&lsaquo;', '&rdquo;', '&acirc;', '&Ouml;', '&aring;', '&atilde;',
     '&trade;', '&Oslash;', '&Oacute;', '&Eacute;', '&ordf;', '&sect;', '&ndash;', '&rlm;', '&times;',
     '&brvbar;', '&Uacute;', '&Aring;', '&ccedil;', '&Yacute;', '&cent;', '&micro;', '&ntilde;',
     '&auml;', '&igrave;', '&oslash;', '&AElig;', '&Phi;', '&ucirc;', '&rsquo;', '&aelig;',
     '&ouml;', '&raquo;', '&Ntilde;']


def tokenize_sentence(
        sentence,
        remove_string=[],
        maintain_punctuation=[",", ".", "!", "?"]
):
    """
        :param sentence: string, the text that needs to be tokenized;
        :param remove_string: list, the string contained will be removed from the sentence;
        :param maintain_punctuation: list, the punctuation character contained will be maintained in the sentence;
        :return: string, the new sentence after tokenizing.
    """

    new_sentence = sentence

    # string remove
    remove_string = remove_string + special_string
    for rm_string in remove_string:
        new_sentence = new_sentence.replace(rm_string, " ")

    # abbreviation reduction
    new_sentence = pat_is.sub(r"\1 is ", new_sentence)
    new_sentence = pat_can.sub("can not", new_sentence)
    new_sentence = pat_won.sub("will not", new_sentence)
    new_sentence = pat_not.sub(" not", new_sentence)
    new_sentence = pat_would.sub(" would", new_sentence)
    new_sentence = pat_will.sub(" will", new_sentence)
    new_sentence = pat_am.sub(" am", new_sentence)
    new_sentence = pat_are.sub(" are", new_sentence)
    new_sentence = pat_ve.sub(" have", new_sentence)

    # punctuation maintain
    remove_punctuation = [char for char in string.punctuation if char not in maintain_punctuation]
    for rm_punc in remove_punctuation:
        new_sentence = new_sentence.replace(rm_punc, " ")

    new_sentence = new_sentence.split()
    new_words = []
    for token in new_sentence:
        words = nltk.tokenize.word_tokenize(token)
        for word in words:
            new_words.append(word.lower())

    new_sentence = ' '.join(new_words)

    return new_sentence


