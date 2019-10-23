"""
对英文文档进行预处理包括：
1,分句
2,标准化
3,分词(to be done)
4,去停用词
5,提取词干
6,提取地名
"""
import nltk
import string
import unicodedata
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

__all__ = ['EnglishSentence']
en_stopwords = list(stopwords.words('english')) + \
                    [punc for punc in string.punctuation.split() if punc not in [
                                                               '-']] + ["."]
stemmer = nltk.stem.SnowballStemmer('english')


class EnglishSentence:
    def __init__(self, text=None):
        if isinstance(text, list):
            self._sentences = [self._normalize(sentence) for sentence in text]
        elif isinstance(text, str):
            self._sentences = [self._normalize(sentence) for sentence in sent_tokenize(text)]
        else:
            raise Exception("text should be list of string or string")

        self._words_full = [self._word_tokenize(
            sentence) for sentence in self._sentences]
        self._words = [[word for word in sentence if word not in en_stopwords]
            for sentence in self._words_full]
        # self._words = [ word for sentence in self._words_full for word in sentence if word not in en_stopwords]
        # self._stems = [stemmer.stem(word) for sentence in self._words for word in sentence]
        self._stems = [[stemmer.stem(word) for word in sentence]
                                     for sentence in self._words]

    def _word_tokenize(self, sentence):
        if isinstance(sentence, list):
            return sentence
        elif isinstance(sentence, str):
            return word_tokenize(sentence)
        else:
            raise Exception("sentence should be list of str or str")

    def _normalize(self, c_str):
        if not c_str:
            return ''
        c_str = unicodedata.normalize('NFD', c_str)
        return ''.join(c for c in c_str if not unicodedata.combining(c))

    @property
    def words(self):
        """获取单词
        """
        return self._words

    @property
    def words_full(self):
        """全部单词
        """
        return self._words_full

    @property
    def sentences(self):
        """获取句子
        """
        return self._sentences

    @property
    def stems(self):
        """获取词干
        """
        return self._stems

    # to be done
    @property
    def places(self):
        """获取地点
        """
        pass

    # to be done
    @property
    def entities(self):
        """获取实体
        """
        pass

    @property
    def corpus(self):
        return self._sentences