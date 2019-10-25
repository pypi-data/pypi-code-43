# -*- coding: utf-8 -*-
"""
**Supervised classification**

Supervised classification methods are used to generate a map with each pixel
assigned to a class based on its multispectral composition. The classes are
determined based on the spectral composition of training areas defined by the
user.

Classification is supervised and need samples for fitting. The output will be
be a matrix with integer values.

Example:
    >>> from maplearn.datahandler.loader import Loader
    >>> from maplearn.datahandler.packdata import PackData
    >>> loader = Loader('iris')
    >>> data = PackData(X=loader.X, Y=loader.Y, data=loader.aData)
    >>> lst_algos = ['knn', 'lda', 'rforest']
    >>> dir_out = os.path.join('maplean_path', 'tmp')
    >>> clf = Classification(data=data, dirOut=dir_out, algorithm=lst_algos)
    >>> clf.run()

"""
from __future__ import print_function

import os
import re

import numpy as np
import pandas as pd

from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, f1_score

from maplearn.ml.machine import Machine
from maplearn.ml.algos_classification import ALGOS
from maplearn.ml.confusion import Confusion
from maplearn.datahandler.plotter import Plotter
from maplearn.ml.distance import Distance
from maplearn.app.reporting import str_table, str_synthesis, str_prop, icon_msg

from maplearn import logger


def lcs_kernel(x, y):
    """
    Custom kernel based on LCS (Longest Common Substring)

    Args:
        * x and y (matrices)

    Returns:
        matrix of float values
    """
    dist = Distance(x, y)
    return dist.run(meth='lcs')

def svm_kernel(x, y):
    """
    Custom Kernel based on DTW

    Args:
        * x and y (matrices)

    Returns:
        matrix of float values
    """
    dist = Distance(x, y)
    return dist.run(meth='dtw')

# LISTE DES ALGOS EN STOCK
TUNE_ALGO = dict(
    knn={'n_neighbors': [3, 5, 10],
         'weights': ['uniform', 'distance'],
         'algorithm': ['auto', 'ball_tree', 'kd_tree'],
         'leaf_size': [15, 30, 50]},
    tree={'max_features': ['sqrt', 'log2', None]},
    log={'penalty': ['l1', 'l2'], 'C': [0.1, 1, 10, 100]},
    svm=[{'kernel': ['rbf'], 'gamma': np.logspace(-6, -1, 6),
          'C': [0.1, 1, 10, 100, 1000]},
         {'kernel': ['linear', 'poly', 'sigmoid'],
          'C': [0.1, 1, 10, 100, 1000]}],
    nearestc={'shrink_threshold': [None, 0.1, 0.2, 0.5]},
    lda={'solver': ['lsqr', 'eigen'],
          'shrinkage':[None, 0.1, 0.2, 0.5, 'auto'],
          'tol':[0.1, 0.2, 0.5]},
    rforest={'n_estimators': [5, 10, 25, 50, 100, 200],
             'max_features': ['sqrt', 'log2', None]},
    mlp={'alpha': list(np.logspace(-5,3,5)),
         'hidden_layer_sizes':[(100,), (50, 2), (20, 5), (10, 10)]})

def skreport_md(report):
    """
    Convert a classification report given by scikit-learn into a markdown table
    TODO: replaced by a pandas dataframe

    Arg:
        * report (str): classification report

    Returns:
        str_table: a table formatted as markdown
    """
    report = report.replace('\n\n', '\n').replace('class ', '      ')
    report = report.replace('avg / total', 'avg/total').replace(' avg', '-avg')
    test_s = [i.strip() for i in report.split('\n')]
    test_s = [i for i in test_s if len(i) > 0]
    test_s.pop(0)
    for i, v in enumerate(test_s):
        test_s[i] = re.findall( r'\d+\.*\d*', v)
        test_s[i] = [j for j in v.split(' ') if len(j) >0]
    dct_report = dict()
    __header = ['class', 'accuracy', 'recall', 'f1-score', 'support']
    for i, v in enumerate(__header):
        try:
            dct_report[v] = [s[i] for s in test_s]
        except IndexError:
            logger.warning('Classification report: %s is missing', v)
            return report
    return str_table(__header, 50, **dct_report)


class Classification(Machine):
    """
    Apply supervised classification onto a dataset:

    * samples needed for fitting
    * data to predict

    Args:
        * data (PackData): data to play with
        * algorithm (list or str): name of an algorithm or list of algorithm(s)
        * **kwargs: other parameters like kfold
    """
    # available scoring options for optimization(many of them do not concern
    # classification purposes:
    #
    #'accuracy', 'adjusted_rand_score', 'average_precision', 'f1', 'f1_macro',
    #'f1_micro', 'f1_samples', 'f1_weighted', 'neg_log_loss',
    #'neg_mean_absolute_error', 'neg_mean_squared_error',
    #'neg_median_absolute_error', 'precision', 'precision_macro',
    #'precision_micro', 'precision_samples', 'precision_weighted', 'r2',
    #'recall', 'recall_macro', 'recall_micro', 'recall_samples',
    #'recall_weighted', 'roc_auc'
    __SCORING = "precision_weighted"
    def __init__(self, data=None, algorithm=None, **kwargs):
        """
        Initialiaze
        """
        Machine.ALL_ALGOS = ALGOS
        # Cross-Validation => Definition of folds
        self.kfold = 3 if 'kfold' not in kwargs else kwargs['kfold']
        self.__skf = None
        self.__folds = None

        self.__dct_scores = dict(Algorithm=[], Accuracy=[], Recall=[], F1=[],
                                 Kappa=[])
        Machine.__init__(self, algorithm=algorithm, data=data, **kwargs)

        self.algorithm = algorithm

        if 'metric' in kwargs:
            if kwargs['metric'] == 'dtw':
                dist = Distance()
                metric = dist.dtw
                kernel = svm_kernel
            elif kwargs['metric'] == 'lcs':
                dist = Distance()
                metric = dist.lcs
                kernel = lcs_kernel
            else:
                metric = kwargs['metric']
                # TODO : avoir un kernel propre a chaque distance
                kernel = 'linear'
            for clf in self._algorithm:
                if 'metric' in self._algorithm[clf].get_params():
                    self._algorithm[clf].set_params(metric=metric)
                elif 'kernel' in self._algorithm[clf].get_params():
                    self._algorithm[clf].set_params(kernel=kernel)

    def load(self, data):
        """
        Loads necessary data for supervised classification:

        * samples (X and Y): necessary for fitting
        * other (unknwon) data to predict, after fitting

        Args:
            * data (PackData)
        """
        Machine.load(self, data)
        if self._data.Y is None:
            raise AttributeError('No samples available')
        if self._data.data is None:
            self._data.data = self._data.X

        # analyse de l'echantillon en fonction de la cross-validation
        frq = self._data.classes
        if min(frq.values()) < self.kfold:
            i = 0
            __classes = []
            for k, v in frq.items():
                if v < self.kfold:
                    self._data.X = self._data.X[self._data.Y != k, :]
                    self._data.Y = self._data.Y[self._data.Y != k]
                    logger.debug("Class %i has too few ind. (%i) -> ignored",
                                 k, v)
                    i += 1
                    __classes.append(k)
            logger.warning('%i classes ignored due to too few members', i)
            print(icon_msg("%i classe(s) exclue(s) par manque d'individus : %s"\
                           % (i, str(__classes)), nature="warning"))
        self.__split()
        return 0

    def predict_1(self, algo, proba=True):
        """
        Predict classes using a fitted algorithm applied to unknown data

        Args:
            * algo (str): name of the algorithme to apply
            * proba (bool): should probabilities be added to result
        """
        Machine.predict_1(self, algo)
        if proba:
            try:
                self.algo.set_params(probability=True)
            except ValueError:
                logger.warning('Probabilities may not be computed with %s',
                               algo)
        # 1. CLASSIFICATION (k-fold)
        print('\n####%s - Prediction ####' % algo)
        # classification sur tous les donnees
        self.algo.fit(self._data.X, self._data.Y)
        logger.info('Algorithm %s trained on whole dataset', algo)

        result = self.algo.predict(self._data.data).astype(np.int16)
        __counts = np.unique(result, return_counts=True)
        print(str_prop(__counts, outdir=self.dir_out,
                       outfile='cnt_pred_%s.png' % algo))
        logger.info('Prediction on whole dataset with %s', algo)

        __attr = ['feature_importances_', ]
        for i in __attr:
            if hasattr(self.algo, i):
                if i == 'feature_importances_':
                    __plt = Plotter(output=self.dir_out)
                    __tmp = pd.DataFrame({'features':self._data.features,
                                         'importance':getattr(self.algo, i)})
                    __tmp.to_csv(os.path.join(self.dir_out, 'results',
                                 "%s_%s.csv" % (algo, i)), index=False)
                    print(__plt.barplot(data=__tmp, y='importance',
                                        x='features',
                                        title="importance of features",
                                        file='imp_feat_%s.png' % algo))
        self.result[algo] = result
        if proba:
            __proba = None
            # Get probabilities of output classes
            if hasattr(self.algo, 'predict_proba'):
                try:
                    __proba = np.round(np.max(self.algo.predict_proba(
                             self._data.data).astype(np.float16), 1), 5)
                except (NotImplementedError, AttributeError):
                    logger.error('Unable to compute probabilities with %s',
                                 algo)
                else:
                    logger.info('Got probabilities using %s', algo)
                    self.proba[algo] = __proba
            else:
                logger.warning('No probabilities available with %s', algo)
        print('\n\n<div style="clear:both;">\n</div>\n')

    def __split(self):
        """
        Splits samples (X) in k folds
        """
        #NB: StratifiedKFold can only be used with classes
        self.__skf = StratifiedKFold(n_splits=self.kfold, shuffle=True)
        self.__folds = []
        for t, v in self.__skf.split(X=self._data.X, y=self._data.Y):
            self.__folds.append([t, v])
        logger.info('Dataset is splitted into %i folds', len(self.__folds))

    def fit_1(self, algo):
        """
        Fits a classifier using cross-validation

        Arg:
            * algo (str): name of the classifier
        """
        Machine.fit_1(self, algo)
        # 1. CLASSIFICATION (k-fold)
        print('\n####%s - Entrainement classification####' % algo)

        k = np.zeros(shape=self.kfold)
        for i in range(self.kfold):
            t, v = self.__folds[i]
            print('\n#####%s (%i/%i)#####' % (algo, i + 1, self.kfold))
            # fitting on some samples (k-1 folds)
            try:
                self.algo.fit(self._data.X[t, :], self._data.Y[t])
            except ValueError:
                logger.error('%s cannot be fitted', algo)
                return None
            except (AttributeError, TypeError):
                logger.error('ERROR with %s classifier => Exclusion', algo)
                # self._algorithm.pop(name) # exclusion de la classification
                return None

            # predicting other samples (1 fold)
            result_clf = self.algo.predict(self._data.X[v, :])
            mat_confusion = Confusion(self._data.Y[v], result_clf)
            mat_confusion.calcul_matrice()
            str_file = os.path.join(self.dir_out,
                                    '_'.join((algo, str(i), 'cm')))
            print(mat_confusion.export(fTxt=str_file + '.txt',
                                 fPlot=str_file + '.png'))
            k[i] = mat_confusion.kappa

            # Underfitting/Overfitting : scores of classification
            __f1 = [f1_score(self._data.Y[t],
                             self.algo.predict(self._data.X[t, :]),
                             average="weighted"),
                    f1_score(self._data.Y[v],
                             self.algo.predict(self._data.X[v, :]),
                             average="weighted")]
            # training vs. test
            print('\n**Score (F1) :**')
            print('* Entrainement = %.2f' % __f1[0])
            print('* Validation = %.2f' % __f1[1])
            print("*NB: Un score eleve sur les echantillons d'entrainement et \
                    faibles pour ceux de la validation -> signe de \
                    surentrainement*")

            # Classification report
            str_report = str(classification_report(self._data.Y[v], result_clf))
            print(skreport_md(str_report))
            print('\n\n<div style="clear:both;">\n</div>\n')
        # summarize statistical results
        try:
            accuracy = cross_val_score(self.algo, self._data.X, self._data.Y,
                                     cv=self.__skf, scoring='accuracy')
            recalls = cross_val_score(self.algo, self._data.X, self._data.Y,
                                     cv=self.__skf, scoring='recall_weighted')
            f1s = cross_val_score(self.algo, self._data.X, self._data.Y,
                         cv=self.__skf, scoring='f1_weighted')
        except ValueError:
            logger.warning('%s - Cross-validation score not computable',
                           algo)
        else:
            self._fitted = True
            self.__dct_scores['Algorithm'].append(algo)
            self.__dct_scores['Accuracy'].append(str_synthesis(accuracy))
            self.__dct_scores['Recall'].append(str_synthesis(recalls))
            self.__dct_scores['F1'].append(str_synthesis(f1s))
            self.__dct_scores['Kappa'].append(str_synthesis(k))
            print('\n**%s - Cross-Validation %i-fold :**' % (algo, self.kfold))
            print("* Accuracy: %s" % self.__dct_scores['Accuracy'][-1])
            print("* Kappa : %s\n" % self.__dct_scores['Kappa'][-1])

    def export_tree(self, out_file=None):
        """
        Exports a decision tree

        Args:
            * out_file (str): path to the output file
        """
        if out_file is None or out_file == '':
            out_file = os.path.join(self.dir_out, 'decision_tree.dot')
        clf = self.algo.DecisionTreeClassifier()
        clf.fit(X=self._data.X, y=self._data.Y)
        with open(out_file, 'w') as file_:
            file_ = self.algo.export_graphviz(clf, out_file=file_)
        logger.info("Decision tree saved to %s", out_file)

    def run(self, predict=False):
        """
        Applies every classifiers specified in 'algorithm' property

        Args:
            predict (bool): should be the classifier only fitted or also used
            to predict?
        """
        Machine.run(self, predict)
        print(icon_msg('Cross-Validation %i-fold' % self.kfold))
        size = 20
        header = ['Algorithm', 'Accuracy', 'Recall', 'F1', 'Kappa']
        print(str_table(header=header, size=size, **self.__dct_scores))

        lst_exclu = list(set(self.algorithm) ^ set(self.__dct_scores['Algorithm']))
        if len(lst_exclu) > 0:
            print(icon_msg("\%i classifications avec erreurs : %s"
                  % (len(lst_exclu), ','.join(lst_exclu))), nature="warning")

    def optimize(self, algo):
        """
        Optimize parameters of a classifier

        Args:
            * algo (str): name of the classifier to use
        """
        if algo not in TUNE_ALGO:
            logger.warning('No available optimization available for %s', algo)
            return None

        # normalisation des donnees => accelere GridSearchCV
        if np.mean(self._data.X) < 0.9 or np.mean(self._data.X) > 1.1:
            self._data.scale()
        score_name = self.__SCORING[:-6]
        print("####Optimisation de %s (but : best %s)####\n"
              % (algo, score_name))
        gs = GridSearchCV(self._algorithm[algo],
             param_grid=TUNE_ALGO[algo],
             n_jobs=4, cv=self.kfold, scoring=self.__SCORING)

        gs.fit(self._data.X, self._data.Y)
        y_true, y_pred = self._data.Y, gs.predict(self._data.X)

        print("\n * Meilleurs parametres : " + str(gs.best_params_))
        print("\n * Meilleur estimateur: " + str(gs.best_estimator_))
        print("\n * Meilleur score : %.3f \n" % gs.best_score_)
        print(classification_report(y_true, y_pred))

        self._algorithm[algo + '.optim'] = gs.best_estimator_
