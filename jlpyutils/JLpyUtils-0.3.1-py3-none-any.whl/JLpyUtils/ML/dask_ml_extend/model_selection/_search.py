"""
Functions for performing model selection hyperparameter searchs
"""

class GridSearchCV():
    
    def __init__(self,
                 estimator, 
                 param_grid,
                 scoring = None,
                 n_jobs = -1,
                 cv = 5,
                 refit = True,
                 verbose = 1):
        
        self.estimator = estimator
        self.param_grid = param_grid
        self.scoring = scoring
        self.n_jobs = n_jobs
        self.n_splits_ = cv
        self.refit = refit
        self.verbose = verbose
        
        #build param grid
        import sklearn.model_selection
        self.ParameterGrid = list(sklearn.model_selection.ParameterGrid(param_grid))
        
        #build Kfild generator
        import dask_ml.model_selection
        self.KFolder = dask_ml.model_selection.KFold(n_splits = cv)
        
        #add scorer
        if scoring == None:
            self.scorer_ = self.estimator.score
        else:
            import sklearn.metrics
            self.scorer_ = sklearn.metrics.get_scorer(scoring)
            
    def _cv(self, estimator, X, y):
        import numpy as np
        if 'dask' in str(type(estimator)):
            import dask.distributed
            client = dask.distributed.Client()

        KFolder_splits = self.KFolder.split(X,y)
        
        scores = []
        for fold in KFolder_splits:
            
            X_train = X[fold[0]]
            X_test = X[fold[1]]
            
            y_train = y[fold[0]]
            y_test = y[fold[1]]
            
            if 'dask' not in str(type(self.estimator)):
                X_train = X_train.compute()
                X_test = X_test.compute()
                y_train = y_train.compute()
                y_test = y_test.compute()

            estimator.fit(X_train, y_train)
            
            if self.scoring==None:
                score = self.scorer_(X_test, y_test)
            else:
                score = self.scorer_(estimator, X_test, y_test)
            scores.append(score)
            
            if self.verbose>=3: print('cv Progress:',round(len(scores)/self.n_splits_*100,2),'%',end='\r')
            
        score = np.mean(scores)
        
        if 'dask' in str(type(estimator)):
            client.close()
        
        return score

    
    def fit(self, X, y):
        """
        Run fit with all sets of parameters.
        
        Arguments:
        ----------
            X : array-like, shape = [n_samples, n_features]
                Training vector, where n_samples is the number of samples and
                n_features is the number of features.
            y : array-like, shape = [n_samples] or [n_samples, n_output], optional
                Target relative to X for classification or regression;
                None for unsupervised learning.
        """
        import warnings
        import dask
        import numpy as np
        
        warnings.filterwarnings('ignore')
        
        #Ensure X and y are in array form
        if 'dask.dataframe' in str(type(X)):
            X = X.to_dask_array(lengths=True)
        if 'dask.dataframe' in str(type(y)):
            y = y.to_dask_array(lengths=True)
        
        if self.verbose >=1:
            print('running', self.n_splits_, 'fold cross validation on',len(self.ParameterGrid),'candidates, totalling',self.n_splits_*len(self.ParameterGrid),'fits')
            
            if self.scoring == None:
                print('Scoring using estimator default')
            else:
                print('Scoring using',self.scoring)
            
        #run grid search
        p=0
        time_cv_list = []
        scores = []
        for params in self.ParameterGrid:
            if self.verbose >=1:
                param_sweep_print = '\tParameter sweep progress: '+\
                      str(round((p+1)/len(self.ParameterGrid)*100,3))+\
                      '(total time (mins):'+\
                      str(round(np.sum(time_cv_list),2))+' of ~'+\
                      str(round(np.median(time_cv_list)*len(self.ParameterGrid),2))+')'

            estimator = self.estimator.set_params(**params)
            score = self._cv(estimator, X, y)
            scores.append(score)
            
            p+=1
            
            if self.verbose>=1: 
                print('ParameterGrid Progress:',round(p/len(self.ParameterGrid)*100,2),'%',end='\r')
            
        #fetch best values (sklearns valid scorers are all defined such that greater is better)
        self.best_score_ = np.max(scores)
        self.best_index_ = np.argmax(scores)
        self.best_params_ = self.ParameterGrid[self.best_index_]
        self.best_estimator_ = self.estimator.set_params(**self.best_params_)
        
        if self.refit:
            if 'dask' not in str(type(self.estimator)):
                X = X.compute()
                y = y.compute()
            self.best_estimator_.fit(X, y)
            
        warnings.filterwarnings('default')
        