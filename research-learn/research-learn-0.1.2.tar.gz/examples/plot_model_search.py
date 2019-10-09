"""
=============================
Model search cross-validation
=============================

This example illustrates the usage of model
search cross-validation class.

"""

# Author: Georgios Douzas <gdouzas@icloud.com>
# Licence: MIT

import matplotlib.pyplot as plt

import pandas as pd
from sklearn.base import clone
from sklearn.datasets import make_classification
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline

from rlearn.model_selection import ModelSearchCV

print(__doc__)

RND_SEED = 0


###############################################################################
# Generate classification data
###############################################################################

###############################################################################
# We are generating a binary class data set, using
# ``make_classification`` from scikit-learn.

X, y = X, y = make_classification(n_classes=2, random_state=RND_SEED)

###############################################################################
# Using model search
###############################################################################

###############################################################################
# Model search cross-validation class allows to search the model and
# hyper-parameters in a unified way.

classifiers = [
    ('knn', make_pipeline(MinMaxScaler(), KNeighborsClassifier())),
    ('gbc', GradientBoostingClassifier(random_state=RND_SEED)),
]
param_grids = [
    {
        'knn__minmaxscaler__feature_range': [(0, 1), (0, 0.5)],
        'knn__kneighborsclassifier__k_neighbors': [2, 4, 5],
    },
    {'gbc__gradientboostingclassifier__max_depth': [3, 4, 5]},
]

model_search_cv = ModelSearchCV(classifiers, param_grids, cv=5, scoring='accuracy')
