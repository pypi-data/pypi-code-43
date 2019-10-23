"""
对中文段落进行：
1,分句
2,分词
3,去停用词
"""
import re
import os
import jieba
import zhon.hanzi
from mynlp.settings import BASE_DIR

sentencesp = re.compile('([﹒﹔﹖﹗．；。！？]["’”」』]{0,2}|：(?=["‘“「『]{1,2}|$))')

class ChineseSetence:
    def __init__(self, text):
        if isinstance(text, list):
            self._sentences = text
        elif isinstance(text, str):
            self._sentences = self._sent_tokenize(text)
        else:
            raise Exception("text should be list of string or string")

        self._words_full = [self._word_tokenize(sentence) for sentence in self._sentences]
        # self._words = [word for sentence in self._words_full for word in sentence if word not in self.cn_stopwords]
        self._words = [[word for word in sentence if word not in self.cn_stopwords] for sentence in self._words_full]

    @property
    def cn_stopwords(self):
        path = os.path.join(BASE_DIR, 'data', 'cn_stopwords')
        with open(path, 'r', encoding='utf-8')  as f:
            words = f.readlines()
        return [word.strip() for word in words] + [' ', '\n', ',',]

    def _word_tokenize(self, text):
        seg_list = jieba.cut(text, cut_all=False)
        return seg_list

    def _sent_tokenize(self, text):
        slist = []
        for i in sentencesp.split(text):
            if sentencesp.match(i) and slist:
                slist[-1] += i
            elif i:
                slist.append(i)
        return slist

    @property
    def words(self):
        return self._words

    @property
    def sentences(self):
        return self._sentences

    @property
    def words_full(self):
        return self._words_full

    @property
    def corpus(self):
        return [" ".join(sentence) for sentence in self._words]