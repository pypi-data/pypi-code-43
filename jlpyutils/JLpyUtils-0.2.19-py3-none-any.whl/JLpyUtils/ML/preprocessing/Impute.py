def categorical_features(X, 
                        categorical_headers, 
                        strategy = 'most_frequent', 
                        estimator = None,
                        verbose= 0):
        """
        Impute (fill nan) values for categorical features

        Arguments:
        ----------
            X: pandas dataframe. If strategy = 'iterative', then all categorical features must be label encoded in a previous step, with nan values remaining after encoding.
            categorical_headers: list of categorical feature headers.
            strategy : The imputation strategy.
                - If If “constant”, then replace missing values with fill_value. Can be used with strings or numeric data. fill_value will be 0 when imputing numerical data and “missing_value” for strings or object data types.
                - If "most_frequent", then replace missing using the most frequent value along each column. Can be used with strings or numeric data.
                - If 'iterative', then use sklearn.imputer.IterativeImputer with the specified estimator
            estimator: sklearn estimator object
                The estimator to be used if 'iterative' strategy chosen
        Note: sklearn.impute.IterativeImputer has a number of other options which could be varied/tuned, but for simplicity we just use the defaults
        """
        import sklearn.preprocessing, sklearn.impute
        from sklearn.experimental import enable_iterative_imputer
        import warnings
        import pandas as pd
        import dask
        import numpy as np
        import dask
        
        warnings.filterwarnings('ignore')

        X = X.copy()
        
        if strategy != 'iterative':
            Imputer = sklearn.impute.SimpleImputer(strategy=strategy,
                                                   verbose = verbose)

        else:
            n_nearest_features = np.min([10, len(categorical_headers)]) #use less than or equal to 10 features
            Imputer = sklearn.impute.IterativeImputer(estimator= estimator, 
                                                      initial_strategy = 'most_frequent',
                                                      verbose = verbose,
                                                      n_nearest_features = n_nearest_features)
            
        #create a dummy nan row to ensure any dataset containing nan for any of the features can be transformed
        
        type_X = type(X)
        if type_X==dask.dataframe.core.DataFrame:
            npartitions = X.npartitions
            X = X.compute()
            
        X_nans = pd.DataFrame(np.array([[np.nan for header in categorical_headers]]), columns =  categorical_headers)
        X_fit = pd.concat((X[categorical_headers],X_nans))
        
        Imputer.fit(X_fit)

        X[categorical_headers] = Imputer.transform(X[categorical_headers])

        if type_X==dask.dataframe.core.DataFrame:
            X = dask.dataframe.from_pandas(X, npartitions=npartitions)
          
        warnings.filterwarnings('default')
        return X, Imputer

def continuous_features(X, 
                        continuous_headers, 
                        strategy = 'median', 
                        estimator = None,
                        verbose= 0):
    """
    Impute (fill nan) values for continuous features

    Arguments:
    ----------
        X: pandas dataframe. If strategy = 'iterative', then all categorical features must be label encoded in a previous step, with nan values remaining after encoding.
        continuous_headers: list of continuous feature headers.
        strategy : The imputation strategy.
            - If If “constant”, then replace missing values with fill_value. fill_value will be 0 when imputing numerical data.
            - If "most_frequent", then replace missing using the most frequent value along each column.
            - If 'iterative', then use sklearn.imputer.IterativeImputer with the specified estimator
        estimator: sklearn estimator object
            The estimator to be used if 'iterative' strategy chosen
        Note: sklearn.impute.IterativeImputer has a number of other options which could be varied/tuned, but for simplicity we just use the defaults
    """
    import sklearn.preprocessing, sklearn.impute
    from sklearn.experimental import enable_iterative_imputer
    import warnings
    import pandas as pd
    import numpy as np
    import dask

    warnings.filterwarnings('ignore')
    X = X.copy()

    if strategy in ['most_frequent', 'constant', 'mean', 'median']:
        Imputer = sklearn.impute.SimpleImputer(strategy=strategy,
                                               verbose = verbose)
    if strategy == 'iterative':
        n_nearest_features = np.min([10, len(continuous_headers)]) 
        Imputer = sklearn.impute.IterativeImputer(estimator= estimator, 
                                                  initial_strategy = 'most_frequent',
                                                  verbose = verbose,
                                                  n_nearest_features = n_nearest_features)
    type_X = type(X)
    if type_X==dask.dataframe.core.DataFrame:
        npartitions = X.npartitions
        X = X.compute()
        
    #create a dummy nan row to ensure any dataset containing nan for any of the features can be transformed
    X_nans = pd.DataFrame(np.array([[np.nan for header in continuous_headers]]), columns =  continuous_headers)
    X_fit = pd.concat((X[continuous_headers],X_nans))

    Imputer.fit(X_fit)

    X[continuous_headers] = Imputer.transform(X[continuous_headers])

    if type_X==dask.dataframe.core.DataFrame:
        X = dask.dataframe.from_pandas(X, npartitions=npartitions)
            
    warnings.filterwarnings('default')
    return X, Imputer

def default_iterative_regressors_dict():
    """
    dictionary of typical iterative estimators
    """
    import sklearn, sklearn.linear_model, sklearn.ensemble
    
    #focus on BayesianRidge (sklearn default) and RandomForest, since they generally perform better than simple linear or DecisionTree and scale better than KNN
    
    iterative_regressors_dict = {'BayesianRidge':sklearn.linear_model.BayesianRidge(),
                                 'RandomForestRegressor': sklearn.ensemble.RandomForestRegressor(n_jobs=-1)
                                }

    #sklearn.linear_model.LinearRegression(n_jobs=-1), 
    #sklearn.neighbors.KNeighborsRegressor(n_jobs=-1)
    #sklearn.tree.DecisionTreeRegressor(),

    return iterative_regressors_dict

def __unit_test__(X, headers_dict, verbose =1 ):
    """
    Iterate over impute_categorical_feature and impute_continuous_features options & ensure everything works for this particular dataset
    """

    print('------running impute.continuous_features validation-------')
    for strategy in ['mean','median','iterative']:
        print('strategy:',strategy,)

        if strategy in ['most_frequent','mean','median']:
            X_imputed, headers_dict, Imputer = Impute.continuous_features(X, 
                                                                        headers_dict, 
                                                                        strategy = strategy, 
                                                                        estimator = None,
                                                                        verbose = verbose)
        else:
            iterative_estimators_dict = Impute.fetch_iterative_estimators_dict()
            for estimatorID in iterative_estimators_dict.keys():
                print('estimator:',estimatorID)

                X_imputed, headers_dict, Imputer = Impute.continuous_features(X, 
                                                                        headers_dict, 
                                                                        strategy = strategy, 
                                                                        estimator = iterative_estimators_dict[estimatorID],
                                                                        verbose = verbose)

    print('------running impute.categorical_features validation-------')
    for strategy in ['most_frequent', 'iterative']:
        print('strategy:',strategy,)

        if strategy == 'most_frequent':
            X_imputed, headers_dict, Imputer = Impute.categorical_features(X, 
                                                                headers_dict, 
                                                                strategy = strategy, 
                                                                estimator = None,
                                                                verbose = verbose)
        else:
            for estimator in impute.fetch_typical_iterative_estimators():
                print('estimator:',estimator)

                X_imputed, headers_dict, Imputer = Impute.categorical_features(X, 
                                                                    headers_dict, 
                                                                    strategy = strategy, 
                                                                    estimator = estimator,
                                                                    verbose = verbose)




    print('\nall imputation options validated!')