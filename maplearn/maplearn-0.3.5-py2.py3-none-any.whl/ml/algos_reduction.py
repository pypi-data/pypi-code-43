# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 19:16:20 2018

@author: thomas_a
"""
from sklearn.svm import SVC
from sklearn import feature_selection
from sklearn import decomposition
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import StratifiedKFold


estimator = SVC(kernel="linear", cache_size=2000)

ALGOS = dict(
            pca=decomposition.PCA(),
            kbest=feature_selection.SelectKBest(feature_selection.f_classif),
            kbest_chi2=feature_selection.SelectKBest(feature_selection.chi2),
            lda=LinearDiscriminantAnalysis(),
            rfe=feature_selection.RFE(estimator=estimator, step=1),
            rfecv=feature_selection.RFECV(estimator=estimator, step=1,
                                          cv=StratifiedKFold(3),
                                          scoring='accuracy'),
            kernel_pca=decomposition.KernelPCA(kernel="rbf",
                                               fit_inverse_transform=True))