#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-cloudml.
# @File         : demo
# @Time         : 2019-06-24 00:28
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

from tql.algo_ml.oof.LGB import LGB
from sklearn.datasets import load_iris
from sklearn.metrics import roc_auc_score

X, y = load_iris(True)
clf = LGB()
clf.fit(X[:100], y[:100], X[:100] + 1, roc_auc_score)
