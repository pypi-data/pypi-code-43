from sklearn.svm import SVR, SVC
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

default_clf_params = {
    SVC: [
        {
            'key': 'kernel',
            'items': ['linear', 'rbf'],
            'type': 'categorical'
        },
        {
            'key': 'C',
            'items': [1e0, 1e3],
            'type': 'loguniform'
        }
    ],
    RandomForestClassifier: [
        {
            'key': 'n_estimators',
            'items': [3, 50],
            'type': 'int'
        },
        # {
        #     'key': 'criterion',
        #     'items':  ['gini', 'entropy'],
        #     'type': 'categorical'
        # }
    ],
    DecisionTreeClassifier: [
        {
            'key': 'splitter',
            'items': ['best', 'random'],
            'type': 'categorical'
        },
    ]
}

default_reg_search_models = [SVR, RandomForestRegressor, DecisionTreeRegressor]
default_clf_search_models = [SVC, RandomForestClassifier, DecisionTreeClassifier]

default_reg_params = {
    SVR: [
        {
            'key': 'kernel',
            'items': ['linear', 'rbf'],
            'type': 'categorical'
        },
        {
            'key': 'C',
            'items': [1e0, 1e4],
            'type': 'loguniform'
        }
    ],
    RandomForestRegressor: [
        {
            'key': 'n_estimators',
            'items': [3, 100],
            'type': 'int'
        },
        {
            'key': 'criterion',
            'items': ['gini', 'entropy'],
            'type': 'categorical'
        }
    ],
    DecisionTreeRegressor: [
        {
            'key': 'criterion',
            'items': ['mse', 'friedman_mse', 'mae'],
            'type': 'categorical'
        },
        {
            'key': 'splitter',
            'items': ['best', 'random'],
            'type': 'categorical'
        },
    ]
}
