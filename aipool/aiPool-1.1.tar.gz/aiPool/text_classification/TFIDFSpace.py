#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@version: python3.6
@author: XiangguoSun
@contact: sunxiangguodut@qq.com
@file: TFIDFSpace.py
@time: 2018/1/23 16:12
@software: PyCharm
"""
from sklearn.datasets.base import Bunch
from sklearn.feature_extraction.text import TfidfVectorizer
from aiPool.text_classification.Tools import *

logging.basicConfig(level=logging.DEBUG)
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='my.log', level=logging.DEBUG, format=LOG_FORMAT)


class TF:
    def vector_space(self, word_path, bunch_path, space_path, train_tfidf_path=None):
        stpwrdlst = readfile(word_path).splitlines()
        bunch = readbunchobj(bunch_path)
        tfidfspace = Bunch(target_name=bunch.target_name, label=bunch.label, filenames=bunch.filenames, tdm=[],
                           vocabulary={})

        if train_tfidf_path is not None:
            trainbunch = readbunchobj(train_tfidf_path)
            tfidfspace.vocabulary = trainbunch.vocabulary
            vectorizer = TfidfVectorizer(stop_words=stpwrdlst, sublinear_tf=True, max_df=0.5,
                                         vocabulary=trainbunch.vocabulary)
            tfidfspace.tdm = vectorizer.fit_transform(bunch.contents)
        else:
            vectorizer = TfidfVectorizer(stop_words=stpwrdlst, sublinear_tf=True, max_df=0.5)
            tfidfspace.tdm = vectorizer.fit_transform(bunch.contents)
            tfidfspace.vocabulary = vectorizer.vocabulary_

        writebunchobj(space_path, tfidfspace)
        logging.info("if-idf词向量空间实例创建成功！！！")


if __name__ == '__main__':
    tf = TF()
    stopword_path = "train_word_bag/hlt_stop_words.txt"
    bunch_path = "train_word_bag/train_set.dat"
    space_path = "train_word_bag/tfdifspace.dat"
    tf.vector_space(stopword_path, bunch_path, space_path)

    bunch_path = "test_word_bag/test_set.dat"
    space_path = "test_word_bag/testspace.dat"
    train_tfidf_path = "train_word_bag/tfdifspace.dat"
    tf.vector_space(stopword_path, bunch_path, space_path, train_tfidf_path)


