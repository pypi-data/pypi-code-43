import nltk
from mynlp.utils import check_lang
from mynlp.preprocess.englishprocess import EnglishSentence
from mynlp.preprocess.chineseprocess import ChineseSetence

__all__ = ['english_sentence', 'chinese_sentence']


def english_sentence(text):
    return EnglishSentence(text)


def chinese_sentence(text):
    return ChineseSetence(text)


def sentence(text):
    """根据语言类型，返回对应的文档结构
    """
    if isinstance(text, str):
        _lang = check_lang(text)
    elif isinstance(text, list):
        if not text:
            raise Exception("text is empty")
        _lang = check_lang(text[0])
    elif isinstance(text, ChineseSetence) or isinstance(text, EnglishSentence):
        return text
    else:
        raise Exception("text should be str or list of str")

    if _lang == 'cn':
        _document = chinese_sentence(text)
    elif _lang == 'en':
        _document = english_sentence(text)
    else:
        raise Exception("unknown language")
    return _document
