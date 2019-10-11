#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
@version: python3.6
@author: XiangguoSun
@contact: sunxiangguodut@qq.com
@file: NBayesPredict.py
@time: 2018/1/23 16:12
@software: PyCharm
"""
import datetime
import logging
import logging.handlers

from sklearn.naive_bayes import MultinomialNB  # 导入多项式贝叶斯算法
from sklearn import metrics
from aiPool.text_classification.Tools import readbunchobj

logger = logging.getLogger('NBayes_predict')
logger.setLevel(logging.DEBUG)

rf_handler = logging.handlers.TimedRotatingFileHandler('all.log', when='midnight', interval=1, backupCount=7,
                                                       atTime=datetime.time(0, 0, 0, 0))
rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

f_handler = logging.FileHandler('error.log')
f_handler.setLevel(logging.ERROR)
f_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))

logger.addHandler(rf_handler)
logger.addHandler(f_handler)


class NBayesPredict:
    def predict(self, filepath, alpha):
        # 导入训练集
        trainpath = "train_word_bag/tfdifspace.dat"
        train_set = readbunchobj(trainpath)

        # 导入测试集
        testpath = filepath + "_word_bag/testspace.dat"
        test_set = readbunchobj(testpath)

        # 训练分类器：输入词袋向量和分类标签，alpha:0.001 alpha越小，迭代次数越多，精度越高
        clf = MultinomialNB(alpha=alpha).fit(train_set.tdm, train_set.label)

        # 预测分类结果
        predicted = clf.predict(test_set.tdm)

        for flabel, file_name, expct_cate in zip(test_set.label, test_set.filenames, predicted):
            logging.info(file_name + ": 实际类别:" + flabel + " -->预测类别:" + expct_cate)
        logging.info("预测完毕!")


# 计算分类精度：

def metrics_result(actual, predict):
    logging.info('精度:{0:.4f}'.format(metrics.precision_score(actual, predict, average='weighted')))
    logging.info('召回:{0:0.4f}'.format(metrics.recall_score(actual, predict, average='weighted')))
    logging.info('f1-score:{0:.4f}'.format(metrics.f1_score(actual, predict, average='weighted')))

# metrics_result(test_set.label, predicted)
if __name__ == '__main__':
    # 导入训练集
    trainpath = "train_word_bag/tfdifspace.dat"
    train_set = readbunchobj(trainpath)

    # 导入测试集
    testpath = "test_word_bag/testspace.dat"
    test_set = readbunchobj(testpath)

    # 训练分类器：输入词袋向量和分类标签，alpha:0.001 alpha越小，迭代次数越多，精度越高
    clf = MultinomialNB(alpha=0.001).fit(train_set.tdm, train_set.label)

    # 预测分类结果
    predicted = clf.predict(test_set.tdm)

    for flabel, file_name, expct_cate in zip(test_set.label, test_set.filenames, predicted):
        if flabel != expct_cate:
            print(file_name, ": 实际类别:", flabel, " -->预测类别:", expct_cate)

    print("预测完毕!!!")