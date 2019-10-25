# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 19:23:07 2018

@author: thomas_a
"""
from sklearn import neighbors, linear_model, svm, tree, neural_network
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.ensemble import AdaBoostClassifier, BaggingClassifier
#from sklearn.manifold.isomap import Isomap
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import SGDClassifier
from sklearn.semi_supervised import LabelPropagation, LabelSpreading
from sklearn.linear_model import Perceptron, PassiveAggressiveClassifier

ALGOS = dict(
            knn=neighbors.KNeighborsClassifier(),
            log=linear_model.LogisticRegression(),
            tree=tree.DecisionTreeClassifier(),
            gnb=GaussianNB(),
            mnb=MultinomialNB(),
            lda=LinearDiscriminantAnalysis(),
            nearestc=neighbors.NearestCentroid(),
            svm=svm.SVC(kernel='rbf'),
            svc=svm.SVC(kernel='linear'),
            gboost=GradientBoostingClassifier(),
            bag=BaggingClassifier(warm_start=True),
            rforest=RandomForestClassifier(oob_score=True),
            extra=ExtraTreesClassifier(),
            sgd=SGDClassifier(),
            propag=LabelPropagation(),
            spreading=LabelSpreading(),
            ada=AdaBoostClassifier(),
            perceptron=Perceptron(),
            passive=PassiveAggressiveClassifier(),
            mlp=neural_network.MLPClassifier(),
            )