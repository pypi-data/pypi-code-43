#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from aiPool.text_classification.CorpusBunch import CorpusBunch
from aiPool.text_classification.CorpusSegment import Segment
from aiPool.text_classification.TFIDFSpace import TF
from aiPool.text_classification.NBayesPredict import NBayesPredict
from aiPool.text_classification.OSSUpload import *


class Classification:
    def segment(self, filePath):
        segment = Segment()
        # 对预测数据进行分词
        corpus_path = filePath + "/"  # 未分词分类语料库路径
        seg_path = filePath + "_seg/"  # 分词后分类语料库路径
        if not os.path.exists(seg_path):
            os.makedirs(seg_path)
        segment.corpus_segment(corpus_path, seg_path)

    def bunch(self, filePath):
        bunch = CorpusBunch()
        # 对测试集进行Bunch化操作：
        seg_path = filePath + "_seg/"  # 分词后分类语料库路径
        path = filePath + "_word_bag/"
        if not os.path.exists(path):
            os.makedirs(path)
        wordbag_path = path + "/test_set.dat"  # Bunch存储路径
        bunch.corpus2Bunch(wordbag_path, seg_path)

    def space(self, filePath):
        tf = TF()
        stopword_path = "train_word_bag/hlt_stop_words.txt"
        bunch_path = "train_word_bag/train_set.dat"
        space_path = "train_word_bag/tfdifspace.dat"

        tf.vector_space(stopword_path, bunch_path, space_path)
        path = filePath + "_word_bag/"
        bunch_path = path + "test_set.dat"
        space_path = path + "testspace.dat"
        train_tfidf_path = "train_word_bag/tfdifspace.dat"
        tf.vector_space(stopword_path, bunch_path, space_path, train_tfidf_path)

    def run(self, filePath):
        download_train_word_bag()
        self.segment(filePath)
        self.bunch(filePath)
        self.space(filePath)

        NBayesPredict().predict(filePath, 0.0001)

    def trainModel(self):
        download_train_corpus()
        bunch = CorpusBunch()
        segment = Segment()
        # 对训练集进行分词
        corpus_path = "train_corpus/"  # 未分词分类语料库路径
        seg_path = "train_corpus_seg/"  # 分词后分类语料库路径
        if not os.path.exists(seg_path):
            os.makedirs(seg_path)
        segment.corpus_segment(corpus_path, seg_path)
        # 对训练集进行Bunch化操作：
        wordbag_path = "train_word_bag/train_set.dat"  # Bunch存储路径
        seg_path = "train_corpus_seg/"  # 分词后分类语料库路径
        bunch.corpus2Bunch(wordbag_path, seg_path)


if __name__ == "__main__":
    classification = Classification()
    # classification.trainModel() ##训练模型
    # upload() ##上传模型
    # download_train_word_bag() ##下载并解压模型
    classification.run("spider_corpus")  ##预测
