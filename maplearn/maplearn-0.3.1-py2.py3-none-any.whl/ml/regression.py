# -*- coding: utf-8 -*-
"""
**Regression**

In statistical modeling, regression analysis is a statistical process for
estimating the relationships among variables. It includes many techniques for
modeling and analyzing several variables, when the focus is on the
relationship between a dependent variable and one or more independent
variables.

Regression analysis is supervised and need samples for fitting. The output will
be a matrix with float values.

Example:

    >>> from maplearn.datahandler.loader import Loader
    >>> from maplearn.datahandler.packdata import PackData
    >>> from maplearn.ml.regression import Regression
    >>> loader = Loader('boston')
    >>> data = PackData(X=loader.X, Y=loader.Y, data=loader.aData)
    >>> reg = Regression(data=data, dirOut=os.path.join('maplearn_path', 'tmp'))
    >>> reg.fit_1(self.__algo)
"""
from __future__ import print_function
import os

import numpy as np
import pandas as pd

from statsmodels.stats import api as sms
from sklearn.model_selection import KFold
from sklearn import metrics
from sklearn.model_selection import GridSearchCV

from maplearn.ml.machine import Machine
from maplearn.ml.algos_regression import ALGOS
from maplearn.datahandler.plotter import Plotter
from maplearn.app.reporting import str_table, str_synthesis

from maplearn import logger

pd.set_option('display.precision', 2)
pd.set_option('display.max_columns', 30)
pd.set_option('display.width', 700)

# parameters used to tune algorithm(s)
# SVR: epsilon should be tuned (gamma useful?)
# epsilon: 0.1..0.2..0.3..1? cf. thomas
TUNE_ALGO = dict(
    lm={'fit_intercept': [True, False], 'normalize': [True]},
    svr=[{'kernel': ['rbf'], 'gamma': np.logspace(-6, -1, 6),
          'C': [0.1, 1, 10, 100, 1000]},
         {'kernel': ['linear', 'poly', 'sigmoid'],
          'C': [0.1, 1, 10, 100, 1000]}],
    ridge={'alpha': [0.1, 0.5, 1, 2],
           'tol': [0.0005, 0.001, 0.05, 0.01],
           'fit_intercept': [True, False],
           'solver':['svd', 'cholesky', 'lsqr']},
    kr=[{'kernel': ['rbf'], 'gamma': np.logspace(-6, -1, 6),
          'alpha': [0.1, 1, 10, 100, 1000]},
         {'kernel': ['linear', 'poly', 'sigmoid'],
          'alpha': [0.1, 1, 10, 100, 1000]}],
    tree={'max_depth': [None, 2, 5]},
    rforest={'n_estimators': [5, 10, 25, 50, 100, 200],
             'max_features': ['sqrt', 'log2', None],
             'max_depth': [None, 2, 5]},
    mlp={'alpha': list(np.logspace(-5,3,5)),
         'learning_rate_init': [0.001, 0.01, 0.1],
         'hidden_layer_sizes':[(100,), (50, 2), (20, 5), (10, 10),
                               (5, 5, 5), (5, 5, 5, 5)]})


class Regression(Machine):
    """
    Applies regression using 1 or several algorithm(s) onto a specified dataset

    Args:
        * data (PackData): dataset to play with
        * algorithm (list or str): name of the algorithm(s) to use
        * **kwargs: more parameters like k-fold

    Attributes and properties are inherited from `Machine` class
    """
    __SCORING = 'neg_mean_squared_error'
    def __init__(self, data=None, algorithm=None, **kwargs):
        """
        Initialisation
        """
        Machine.ALL_ALGOS = ALGOS

        self.kfold = 3 if 'kfold' not in kwargs else kwargs['kfold']
        self.__folds = None
        Machine.__init__(self, algorithm=algorithm, data=data, **kwargs)

        self.algorithm = algorithm
        self.__dct_scores = {'Algorithm':[], 'Abs Error':[], 'MSE':[], 'R2':[]}

    def load(self, data):
        """
        Loads necessary data for regression, with samples (labels are float
        values).

        Arg:
            * data (PackData): data to play with

        Returns:
            * int: did data load correctly (returns 0) or not (<> 0) ?

        TODO:
            * checks a few things when loading...
        """
        Machine.load(self, data)
        if self._data.Y is None:
            raise AttributeError('Aucun échantillon spécifié')
        if self._data.data is None:
            self._data.data = self._data.X
        self.__split()
        return 0

    def predict_1(self, algo, proba=False):
        """
        Predicts Y using one regressor (specified by algo)

        Args:

            * algo (str): key of the regressor to use
            * proba (bool): should probabilities (if available) given by
              algorithm be added to result?
        """
        Machine.predict_1(self, algo)

        # apply regression to every samples (not a fold) and then to data
        self.algo.fit(self._data.X, self._data.Y)
        logger.info('Algorithm %s trained on whole dataset', algo)
        result = self.algo.predict(self._data.data)
        logger.info('Prediction on whole dataset with %s', algo)

        # Results are stored in a dataframe (1 column = 1 algorithm's
        # prediction)
        if self.result is None:
            self.result = pd.DataFrame(data=result, columns=[algo, ],
                                       dtype=np.float64)
        else:
            self.result[algo] = result

    def __split(self):
        """
        Splits samples (X) in k folds
        """
        #NB: StratifiedKFold can only be used with classes
        __skf = KFold(n_splits=self.kfold, shuffle=True)
        self.__folds = []
        for t, v in __skf.split(self._data.X):
            self.__folds.append([t, v])
        logger.info('Dataset is splitted into %i folds', self.kfold)

    def fit_1(self, algo):
        """
        Fits one regression algorithm

        Arg:
            * algo (str): name of the algorithm to fit
        """
        Machine.fit_1(self, algo)
        # Train the model using the training sets
        print('\n####%s - Entrainement Regression####' % algo)

        rtwo, mae, mse = [], [], []
        __plt = Plotter(self.dir_out)
        for i in range(self.kfold):
            t, v = self.__folds[i]
            print('\n#####%s (%i/%i)#####' % (algo, i + 1, self.kfold))
            # entrainement sur un k-fold
            try:
                self.algo.fit(self._data.X[t, :], self._data.Y[t])
            except ValueError as e:
                logger.error('%s ne peut être appliqué', algo)
                logger.error(e.message)
                return None
            except (AttributeError, TypeError):
                logger.error('ERREUR dans Regression %s => Exclusion',
                             algo)
                # self._algorithm.pop(name) # exclusion de la classification
                return None

            # Rendu Graphique
            y_pred = self.algo.predict(self._data.X[v, :])
            y_true = self._data.Y[v]
            __res = pd.DataFrame({'Mesures':y_true, 'Prediction':y_pred,
                                  'Residues':y_true-y_pred})
            __plt.regression(__res, file='%s_%i.png' % (algo, i))

            print('\n**Resultats statistiques :**')
            # Explained variance score: 1 is perfect prediction
            rtwo.append(metrics.r2_score(self._data.Y[v], y_pred))
            print('* R2 (%% Variance expliquee) : %.2f' % rtwo[-1])
            mae.append(metrics.mean_absolute_error(self._data.Y[v], y_pred))
            print('* Erreur moyenne Abs. : %.2f' % mae[-1])
            mse.append(metrics.mean_squared_error(self._data.Y[v], y_pred))
            print('* Erreur quadratique moy. : %.2f' % mse[-1])

            # Underfitting/Overfitting : scores of classification
            # training vs. test
            print('\n**Score (F1) :**')
            print('* Entrainement = %.2f' % self.algo.score(self._data.X[t, :],
                                                           self._data.Y[t]))
            print('* Validation = %.2f' % self.algo.score(self._data.X[v, :],
                                                         self._data.Y[v]))
            print("*NB: Un score eleve sur les echantillons d'entrainement et \
                    faibles pour ceux de la validation -> signe de \
                    surentrainement*")
            print('\n\n<div style="clear:both;">\n</div>\n')

            # Analysis of Residuals
            name = ['Jarque-Bera', 'Chi^2 two-tail prob.', 'Skew', 'Kurtosis']
            __plt.qqplot(data=__res['Residues'],
                         file='qq_%s_%i.png' % (algo, i))

            print('\n**Normalite des residus :**')
            test = sms.jarque_bera(__res['Residues'])
            for index in range(len(name)):
                print('* %s = %.3f' % (name[index], test[index]))
            print('\n\n<div style="clear:both;">\n</div>\n')

        # Computations based on cross-validation
        self.__dct_scores['Algorithm'].append(algo)
        self.__dct_scores['Abs Error'].append(str_synthesis(mae))
        self.__dct_scores['MSE'].append(str_synthesis(mse))
        self.__dct_scores['R2'].append(str_synthesis(rtwo))

        self._fitted = True

    def run(self, predict=False):
        """
        Applies every regressors specified in 'algorithm' property

        Args:
            * predict (bool): should be the regressor only fitted or also used
                              to predict?
        """
        Machine.run(self, predict)
        print('*Cross-Validation %i-fold*\n' % self.kfold)
        size = 30
        header = ['Algorithm', 'Abs Error', 'MSE', 'R2']
        print(str_table(header=header, size=size, **self.__dct_scores))

        lst_exclu = list(set(self.algorithm) ^ set(self.__dct_scores['Algorithm']))
        if len(lst_exclu) > 0:
            print("\n+ %i regression(s) avec erreurs : %s"
                  % (len(lst_exclu), ','.join(lst_exclu)))

        if predict:
            __stats = self.result.describe()
            print("\n###Statistiques descriptives des predictions###\n")
            print('<pre>%s</pre>' % str(__stats))
            __stats.to_csv(os.path.join(self.dir_out, 'results',
                                        'stats_predict.csv'))

    def optimize(self, algo):
        """
        Optimize parameters of a regression algorithm

        Args:
            * algo (str): name of the regressor to use
        """
        if algo not in TUNE_ALGO:
            logger.warning('No available optimization available for %s', algo)
            return None
        """
        # normalisation des donnees => accelere GridSearchCV
        if np.mean(self._data.X) < 0.9 or np.mean(self._data.X) > 1.1:
            self._data.scale()
        """
        print("####Optimisation de %s####\n" % algo)
        gs = GridSearchCV(self._algorithm[algo],
             param_grid=TUNE_ALGO[algo],
             n_jobs=-1, cv=self.kfold, scoring=self.__SCORING)

        gs.fit(self._data.X, self._data.Y)

        print("\n * Meilleurs parametres : " + str(gs.best_params_))
        print("\n * Meilleur estimateur: " + str(gs.best_estimator_))
        print("\n * Meilleur score : %.3f \n" % gs.best_score_)

        self._algorithm[algo + '.optim'] = gs.best_estimator_
