"""
Functions for performing model selection hyperparameter searchs
"""

import numpy as _np
import os as _os
import hyperopt as _hyperopt
import time as _time
import functools as _functools
import sklearn.model_selection as _sklearn_model_selection
from .. import NeuralNet as _NeuralNet
from ... import file_utils as _file_utils

import matplotlib.pyplot as _plt

class GridSearchCV():
    
    def __init__(self,
                 models_dict, 
                 cv = 4,
                 scoring= {'metric':None,'maximize':True},
                 metrics = {None:None},
                 retrain = True,
                 path_GridSearchCV_dir = 'GridSearchCV',
                 n_jobs = -1,
                 verbose = 2,
                 **kwargs):
        """
        hyperparameter GridSearchCV across different types of models

        Arguments:
        ----------
            models_dict: dictionary containing all models and their param_grid. 
                - Dictionary Format: {'model name':{'model':model object,
                                                    'param_grid': {parameter name, parameter list}]
            cv: cross-validation index.
            scoring: Default: None.
                - If scoring['metric'] = None, use default score for given sklearn model, or use 'loss' for neural network. 
                - For custom scoring functions, pass 'scoring = {'metric':function or key-word string,
                                                                'maximize':True/False}
                    - for sklearn/dask_ml GridSearchCV, a list of valid metrics can be printed via 'sklearn.metrics.SCORERS.keys()'
            metrics: dictionary with formating like {metric name (str), metric function (sklearn.metrics...)}. The metric will be evaluated after CV on the test set
            retrain: Boolean. whether or not you want to retrain the model if it is already been saved in the path_GridSearchCV_dir folder
            path_GridSearchCV_dir: root directory where the GridSearchCV outputs will be saved.
            n_jobs: int. Default: -1. number of parallel jobs to run. If -1, all available threads will be used
                - Note: parallel computing is not supported for Neural Net models
            verbose: verbosity of prints.
        """
        self.models_dict = models_dict
        self.cv = cv
        self.scoring = scoring
        self.metrics = metrics
        self.retrain = retrain
        self.path_GridSearchCV_dir = path_GridSearchCV_dir
        self.n_jobs = n_jobs
        self.verbose = verbose
        self.kwargs = kwargs
        
        self.save = _file_utils.save
        self.load = _file_utils.load

    def load_NeuralNet(self, path_model_dir, X_train, y_train, epochs):
        """
        load model_dict for Nueral Net case
        """

        #fetch best params
        best_params_ = self.load('best_params_', 'dill', path_model_dir)   
        
        #rebuild model_dict
        model_dict = _NeuralNet.DenseNet.model_dict(**best_params_)
        model_dict['best_model'] = _NeuralNet.utils.load_model(_os.path.join(path_model_dir,'best_estimator_.h5'))
        model_dict['best_params'] = best_params_ 
        model_dict['best_cv_score'] = _np.nan

        return model_dict

        
    def _single_model_GridSearchCV(self, 
                                   model_dict_, 
                                   X_train, y_train, X_test, y_test,
                                   path_model_dir):
        """
        Run Grid Search CV on a single model specified by the "key" argument
        """

        type_model = str(type(model_dict_['model']))
        type_X_train = str(type(X_train))
        if ('sklearn' in type_model or 'xgboost' in type_model) and 'dask' not in type_X_train:
            GridSearchCV = _sklearn_model_selection.GridSearchCV(model_dict_['model'],
                                                              model_dict_['param_grid'],
                                                              n_jobs= self.n_jobs,
                                                              cv = self.cv,
                                                              scoring= self.scoring['metric'],
                                                              verbose = _np.max((0,self.verbose-1))
                                                             )
            if y_train.shape[1]==1:
                y_train = _np.array(y_train).reshape(-1,)
            GridSearchCV.fit(X_train,y_train)

        elif 'dask' in type_X_train:
            from ..dask_ml_extend import model_selection as dask_ml_model_selection

            GridSearchCV = dask_ml_model_selection.GridSearchCV(model_dict_['model'],
                                                                model_dict_['param_grid'],
                                                                n_jobs= self.n_jobs,
                                                                cv = self.cv,
                                                                scoring= self.scoring['metric'],
                                                                )
            GridSearchCV.fit(X_train, y_train)

        else: #run gridsearch using neural net function
            if self.scoring['metric'] == None:
                self.scoring={'metric': 'loss', 'maximize': False}

            #check kwargs for epochs
            epochs = 100
            for item in self.kwargs.items():
                if 'epochs' in item[0]: epochs = item[1]

            GridSearchCV = _NeuralNet.search.GridSearchCV(model_dict_['model'],
                                                           model_dict_['param_grid'],
                                                           cv = self.cv,
                                                           scoring=self.scoring,
                                                           epochs =  epochs,
                                                           path_report_folder = path_model_dir,
                                                           verbose = _np.max((0,self.verbose-1))
                                                        )
            GridSearchCV.fit(X_train, y_train, X_test, y_test)

        model_dict_['best_model'] = GridSearchCV.best_estimator_
        model_dict_['best_params'] = GridSearchCV.best_params_
        model_dict_['best_cv_score'] = GridSearchCV.best_score_

        if 'sklearn' in str(type(model_dict_['model'])):
            self.save(model_dict_, 'model_dict', 'dill', path_model_dir)
        
        return model_dict_
        
       
    def fit(self,
            X_train,
            y_train, 
            X_test, 
            y_test):
        """
        Fit the X_train, y_train dataset & evaluate metrics on X_test, y_test for each of the best models found in each individual models GridSearchCV
        
        Arguments:
        ---------
            X_train, y_train, X_test, y_test: train & test datasets (pandas or dask dataframes)
        """
        
        #instantiate path_model_dirs dictionary so we can know where the models are saved
        self.path_model_dirs = {}

        for key in self.models_dict.keys():
            
            if self.verbose >=1: print('\n----',key,'----')

            #define model directory
            path_model_dir = _os.path.join(self.path_GridSearchCV_dir, key)
            self.path_model_dirs[key] = path_model_dir
            if self.verbose >=1: print('path_model_dir:',path_model_dir)
            
            model_type = type(self.models_dict[key]['model'])
            if 'sklearn' in str(model_type) or 'xgboost' in str(model_type):
                path_file = _os.path.join(path_model_dir,'model_dict.dill')
            elif 'Net' in key:
                path_file = _os.path.join(path_model_dir,'best_params_.dill')

            if self.retrain or _os.path.isfile(path_file)==False:
                self.models_dict[key] = self._single_model_GridSearchCV(self.models_dict[key], 
                                                                            X_train, y_train, 
                                                                            X_test, y_test,
                                                                            path_model_dir)

            else: #reload previously trained model
                if 'sklearn' in str(type(self.models_dict[key]['model'])):
                    self.models_dict[key] = self.load('model_dict', 'dill', path_model_dir)
                elif 'Net' in key:
                    #check kwargs for epochs
                    epochs = 100
                    for item in self.kwargs.items():
                        if 'epochs' in item[0]: epochs = item[1]
                    self.models_dict[key] = self.load_NeuralNet(path_model_dir, 
                                                                            X_train, y_train, 
                                                                            epochs)

            y_pred = self.models_dict[key]['best_model'].predict(X_test)

            if 'Net' not in key:
                self.models_dict[key]['best_pred_score'] = self.models_dict[key]['best_model'].score(X_test, y_test)
            else:
                self.models_dict[key]['best_pred_score'] = self.models_dict[key]['best_model'].evaluate(X_test, y_test, verbose =0)
            
            if self.verbose >=1:
                print('\tbest_cv_score:',self.models_dict[key]['best_cv_score'])
                print('\tbest_pred_score:',self.models_dict[key]['best_pred_score'])

            for metric_key in self.metrics.keys():
                if self.metrics[metric_key] !=None:
                    try:
                        self.models_dict[key][metric_key] = self.metrics[metric_key](y_test, y_pred)
                        print('\t',metric_key,':',self.models_dict[key][metric_key])
                    except Exception as e:
                        print('Exception occured for',metric_key,':',str(e))

            if 'sklearn' in str(type(self.models_dict[key]['model'])):
                self.save(self.models_dict[key], 'model_dict', 'dill', path_model_dir)
            elif 'Net' in key:
                model_dict_subset = self.models_dict[key].copy()
                for key in self.models_dict[key].keys():
                    if key not in ['y_test','y_pred','best_pred_score'] +list(self.metrics.keys()):
                        model_dict_subset.pop(key)
                        
                        
class BayesianSearchCV():
    
    def __init__(self,
                 models_dict, 
                 cv = 4,
                 scoring= {'metric':None,'maximize':True},
                 metrics = {None:None},
                 retrain = True,
                 path_BayesianSearchCV_dir = 'BayesianSearchCV',
                 n_jobs = -1,
                 verbose = 2,
                 **kwargs):
        """
        Hyperparameter BayesianSearchCV across different types of models. This class leverages the hyperopt API. 
        
        Arguments:
        ----------
            models_dict: dictionary containing all models and their param_grid. 
                - Dictionary Format: {'model name':{'model':model object,
                                                    'param_grid': {parameter name, parameter list}]
            cv: cross-validation index.
            scoring: Default: None.
                - If scoring['metric'] = None, use default score for given sklearn model, or use 'loss' for neural network. 
                - For custom scoring functions, pass 'scoring = {'metric':function or key-word string,
                                                                'maximize':True/False}
                    - for sklearn/xgboost/dask_ml GridSearchCV, a list of valid metrics can be printed via 'sklearn.metrics.SCORERS.keys()'
            metrics: dictionary of the form {metric name (str): metric function (sklearn.metrics...)}. The metric will be evaluated after CV on the test set
            retrain: Boolean. whether or not you want to retrain the model if it is already been saved in the path_GridSearchCV_dir folder
            path_BayesianSearchCV_dir: root directory where the BayesianSearchCV outputs will be saved.
            n_jobs: int. Defualt: -1. number of parallel jobs to run. If -1, all available threads will be used
                - Note: parallel computing is not supported for Neural Net models
            verbose: print-out verbosity
            
        Notes:
        ------
            Technically, the optimization is performed using the tree-structured parzeen estimator approach, not a pure bayesian estimator. This approach is more efficient handling hyperparameter optimization tasks with high dimensions and small fitness evaluation budgets. See more details in the paper linked below
            
            https://papers.nips.cc/paper/4443-algorithms-for-hyper-parameter-optimization.pdf
        """
        
        self.models_dict = models_dict
        self.cv = cv
        self.scoring = scoring
        self.metrics = metrics
        self.retrain = retrain
        self.path_BayesianSearchCV_dir = path_BayesianSearchCV_dir
        self.n_jobs = n_jobs
        self.verbose = verbose
        self.kwargs = kwargs
        
        self.save = _file_utils.save
        self.load = _file_utils.load
        
        #define model directory
        self.path_model_dirs = {}
        for key in self.models_dict.keys():
            self.path_model_dirs[key] = _os.path.join(self.path_BayesianSearchCV_dir, key)
        
    def _build_space(self, param_grid):
        """
        Build the hyperparameter space for input into hyperopt.fmin() function.
        
        Arguments:
        ----------
            param_grid: hyperparameter dictionary with key-list pairs.
        
        Returns:
        --------
            space: dictionary with key-hyperopt.hp... pairs
            
        Notes:
        ------
            For each hyperparameter of interest, the max and min in the list of possible values in the param_grid[key] element is evaluated. If the difference between the number of decades between the min and max value is greater than 1, a uniform probability distribution will be sampled between log10(min) and log10(max). This will result in the prefixe 'log10.' being pre-pended to the key in the 'space' dict for the given hyperparameter under consideration. 
            
            For the case of non-numeric hyperparameters, the space[key] value will be assigned using the hyperopt.hp.choice() function, with the choices being in integer form (index), rather than their raw string value.
            
            To convert the hyperparameters from hyperopts 'space' back to the parameters required by the model under evaluation, we run the function '_update_model_params()' in each instance of the 'objective' function evaluation.
        """
        param_grid = param_grid.copy()
        space = {}
        for key in param_grid.keys():
            params = param_grid[key]
            type_str = str(type(params[0]))

            if 'float' in type_str or 'int' in type_str:
                
                min_ = min(params)
                max_ = max(params)
                log10_min_ = _np.log10(min_)
                log10_max_ = _np.log10(max_)

                if round(log10_max_)-round(log10_min_)>1: # use uniform distribution on log spacing 

                    space['log10.'+key] = _hyperopt.hp.uniform(key, log10_min_, log10_max_)
                        
                else:
                    if 'int' in type_str:
                        space[key] = _hyperopt.hp.quniform(key, min_, max_, 1)
                        
                    elif 'float' in type_str:
                        space[key] = _hyperopt.hp.uniform(key, min_, max_)
                        
            elif 'str' in type_str:
                space[key] = _hyperopt.hp.choice(key, [i for i in range(len(params))])

            else:
                raise Exception('type(params[0]) is '+type_str+'. This type of hyperparameter is not yet supported.')

        assert(len(space.keys())==len(param_grid.keys())), 'len(space.keys())='+str(len(space.keys()))+', which is not equal to len(param_grid.keys())='+str(len(param_grid.keys()))

        return space
    
    def _plot_space(self, space):
        '''
        Generate plots to visualize the probability distribution for the parameter space being evaluated.
        
        Arguments:
        ----------
            space: dictionary of form {<parameter ID>: hyperopt.hp... object} generated from the '_build_space()' function
            
        Returns:
        -------
            None. displays histograms showing the probability space
        '''
        n_samples = 5000
        for title, space_slice in space.items():
            
            evaluated = [_hyperopt.pyll.stochastic.sample(space_slice) for _ in range(n_samples)]
            
            _plt.title(title)
            _plt.hist(evaluated)
            _plt.grid(which='both',visible=False)
            _plt.show()
    
    def _update_model_params(self, params, model, param_grid):
        """
        Iterate through the params and update the models arguments/params, ensuring the type of each parameter does not change after updating and transforming log10 distributions back to their base value
        
        Arguments:
        ----------
            params: hyperparameter dictionary being evaluated by hyperopt
            model: model being evaluated
            param_grid: original parameter grid under evaluation
            
        Returns
        -------
            params_transform: dictionary similar to params, but transformed to match the inputs required by the model
            model: Updated model object with the params under evaluation applied to the models arguments by updating the model.__dict__ values.
        """
        
        params = params.copy()
        param_grid = param_grid.copy()
        
        params_transform = {}
        
        for key in params.keys():
            
            if 'log10.' in key:
                log10_transform = True
            else:
                log10_transform = False
            
            key = key.replace('log10.','')
            
            type_str = str(type(param_grid[key][0]))
            
            if 'int' in type_str: 
                if log10_transform:
                    model.__dict__[key]=int(10**params['log10.'+key])
                else:
                    model.__dict__[key]=int(params[key])
            
            elif 'float' in type_str:
                if log10_transform:
                    model.__dict__[key]=float(10**params['log10.'+key])
                else:
                    model.__dict__[key]=float(params[key])
            
            elif 'str' in type_str: #index the param grid for hyperparams using 'choice'
                model.__dict__[key]=param_grid[key][params[key]]
                
            params_transform[key] = model.__dict__[key]    
            
            assert(type_str == str(type(model.__dict__[key]))), 'type(param_grid[key][0]) changed from '+type_str+' to '+str(type(param_grid[key][0]))+' after updating params for key:'+str(key)
            
            if 'str' in type_str:
                assert(params_transform[key] in param_grid[key]), 'params_transform['+key+']='+str(params_transform[key])+' is not in the list of valid parameter choices:'+str(param_grid[key])
                
            else:
                assert(params_transform[key]<=max(param_grid[key]) and params_transform[key]>=min(param_grid[key])), 'params_transform['+key+']='+str(params_transform[key])+' does not lie in the range of valid values:'+str([min(param_grid[key]),max(param_grid[key])] )

        return params_transform, model 
        
    def _objective(self, params, model_dict, X, y):
        """
        Objective function for hyperopt fmin. Note hyperopt assumes the only argument required is the params argument, thus before passing this objective as an argument into the hyperopt.fmin() function, we specify the other arguments using the functools.partial() function (see the _single_model_BayesianSearchCV() function code for more details)
        
        Arguments:
        ----------
            params: hyperparameter dictionary for an individual evaluation
            model_dict: dictionary of form {'model': estimator/model object,
                                           'param_grid':dictionary defining the hyperparameter bounds}
            X: dataframe of features on which the cv_score will be evaluated
            y: dataframe of labels on which the cv_score will be evaluated
        
        Returns:
        -------
            objective: dictionary of form {'loss': cv_score,
                                           'params': hyperparameters using the the evaluation,
                                           'status': hyperopt.STATUS_OK,
                                           'eval_time': evaluation time}
        
        Notes:
        ------
            sklearn-style models try to maximize their score by default, while hyperopt assumes we are trying to minimize our loss, thus if a scoring metric is not defined, or if a metric is specified with a maximize boolean==True, the cv_score will be transformed by cv_score=1/cv_score before being output to the hyperopt fmin optimizer. 
            
            In contrast, in Neural Net models, the default scorer is the loss function, thus if the cv_score will only be transformed to 1/cv_score if scoring['maximize']=True and scoring['metric']!=None
        """
        model = model_dict['model']
        param_grid = model_dict['param_grid'].copy()
        params = params.copy()
        
        obj_verbose = max(0,self.verbose-2)
        
        type_model = str(type(model))
        type_X = str(type(X))
        
        if 'dask' in type_X:
            X = X.compute()
            y = y.compute()
        
        if obj_verbose>=2:
            print('params',params)
        
        params_transform, model = self._update_model_params(params, model, param_grid)
        
        if obj_verbose>=2:
            print('params_transform',params_transform)
        if 'sklearn' in type_model or 'xgboost' in type_model:
            
            cv_scores = _sklearn_model_selection.cross_val_score(model, X, y,
                                                              scoring= self.scoring['metric'],
                                                              cv = self.cv,
                                                              n_jobs= self.n_jobs,
                                                              verbose = obj_verbose
                                                             )

        else: #run gridsearch using neural net function
            
            #check kwargs for epochs
            epochs = 100
            for item in self.kwargs.items():
                if 'epochs' in item[0]: epochs = item[1]

            cv_scores = _NeuralNet.cross_val_score(model, X, y,
                                                   scoring=self.scoring,
                                                   cv = self.cv,
                                                   epochs =  epochs,
                                                   verbose = obj_verbose
                                                   )
            
        cv_score = _np.mean(cv_scores)
        
        if 'sklearn' in type_model or 'xgboost' in type_model:
            if self.scoring['maximize']==True or self.scoring['metric']==None:
                cv_score = 1/cv_score 
        else:
            if self.scoring['maximize']==True and self.scoring['metric']!=None :
                cv_score = 1/cv_score 
             
        objective = {'loss': cv_score,
                     'params': params,
                     'status': _hyperopt.STATUS_OK,
                     'eval_time': _time.time()}
        return objective
    
    def _single_model_BayesianSearchCV(self, 
                                       model_dict, 
                                       X_train, y_train, 
                                       X_test, y_test,
                                       path_model_dir,
                                       refit=True):
        """
        Run BayesianSearchCV on a single model of interest, save the results, and return the updated model_dict
        
        Arguments:
        ----------
            model_dict: dictionary of form {'model': estimator/model object,
                                           'param_grid':dictionary defining the hyperparameter bounds}
            X_train, y_train, X_test, y_test: training and test sets under evaluation
            path_model_dir: path to directory where the model results will be saved. For none-NeuralNet models, the model_dict will be saved as model_dict.dill. For NeuralNets, the model and othere relevant parameters will be saved using keras-based saving methods.
            refit: boolean. whether or not to refit the model on the full training set using the best_params
            
        Returns:
        --------
            model_dict: the passed model_dict, but with key-value pairs for: 'best_params', 'best_model', 'best_cv_score'
        """
        if self.verbose>=1:
            print('Fitting',self.cv,'folds for each of',self.max_evals,'candidates, totalling',self.cv*self.max_evals,'fits')
        
        model_dict = model_dict.copy()
        model = model_dict['model']
        model_type = str(type(model_dict['model']))
        param_grid = model_dict['param_grid'].copy()
        objective = _functools.partial(self._objective, 
                                       model_dict = model_dict, 
                                       X = X_train, y=y_train)
        space = self._build_space(param_grid)
        
        if self.verbose>=4:
            self._plot_space(space)
            
        best_params_bad_keys = _hyperopt.fmin(fn = objective, 
                             space = space, 
                             algo = _hyperopt.tpe.suggest, 
                             max_evals = self.max_evals, 
                             trials = _hyperopt.Trials(),
                             verbose = self.verbose)
        # hyperopt doesn't return the best params dict with keys matching the 'space' keys.
        # This breaks handling of 'log10.' transformed parameters. Fix is implemented below
        best_params_ = {}
        for key in space.keys():
            best_params_[key] = best_params_bad_keys[key.replace('log10.','')]
        if self.verbose>=3:
            print('hyperopt_input_best_params_:',best_params_)
            
        best_score_ = self._objective(best_params_, 
                                       model_dict = model_dict, 
                                       X = X_train, y=y_train)['loss']
        
        #transform params back to original model values
        best_params_, best_model_ = self._update_model_params(best_params_, model, param_grid)
        
        if self.verbose>=3:
            print('model_input_best_params_:',best_params_)
        
        if refit:
            if y_train.shape[1]==1:
                y_train = _np.array(y_train).reshape(-1,)
            best_model_.fit(X_train, y_train)
        
        model_dict['best_params'] = best_params_
        model_dict['best_model'] = best_model_
        model_dict['best_cv_score'] = best_score_ 
        
        if 'sklearn' in model_type or 'xgboost' in model_type:
            self.save(model_dict, 'model_dict', 'dill', path_model_dir)
        
        return model_dict
        
    def fit(self,
            X_train,
            y_train, 
            X_test, 
            y_test,
            max_evals,
            ):
        """
        Fit the X_train, y_train dataset & evaluate metrics on X_test, y_test for each of the best models found in each individual models GridSearchCV
        
        Arguments:
        ---------
            X_train, y_train, X_test, y_test: train & test datasets (pandas or dask dataframes)
            max_evals: Max number of evaluations to perform during the BayesianSearchCV procedure for each model.
            
        Returns:
        -------
            None. The models_dict dictionary will be updated for each model to include key-value pairs for: 'best_params', 'best_model', 'best_cv_score', 'best_pred_score', and a key-value pair for each of the metrics in the metrics dictionary, where the 'best_pred_score' and the metrics are evaluated on the test set passed
        """
        
        self.max_evals = max_evals
        
        for key in self.models_dict.keys():
            
            path_model_dir = self.path_model_dirs[key]
            
            if self.verbose >=1: 
                print('\n----',key,'----')
                print('path_model_dir:',path_model_dir)
            
            model_dict = self.models_dict[key]
            model_type = str(type(model_dict['model']))
            
            if 'sklearn' in model_type or 'xgboost' in model_type:
                path_file = _os.path.join(path_model_dir,'model_dict.dill')
            elif 'Net' in key:
                path_file = _os.path.join(path_model_dir,'best_params_.dill')

            if self.retrain or _os.path.isfile(path_file)==False:
                model_dict = self._single_model_BayesianSearchCV(model_dict, 
                                                                X_train, y_train, 
                                                                X_test, y_test,
                                                                path_model_dir)
                self.models_dict[key] = model_dict
                

            else: #reload previously trained model
                if 'sklearn' in str(type(self.models_dict[key]['model'])):
                    self.models_dict[key] = self.load('model_dict', 'dill', path_model_dir)
                elif 'Net' in key:
                    #check kwargs for epochs
                    epochs = 100
                    for item in self.kwargs.items():
                        if 'epochs' in item[0]: epochs = item[1]
                    self.models_dict[key] = self.load_NeuralNet(path_model_dir, 
                                                                X_train, y_train, 
                                                                epochs)

            y_pred = self.models_dict[key]['best_model'].predict(X_test)

            if 'Net' not in key:
                self.models_dict[key]['best_pred_score'] = self.models_dict[key]['best_model'].score(X_test, y_test)
            else:
                self.models_dict[key]['best_pred_score'] = self.models_dict[key]['best_model'].evaluate(X_test, y_test, verbose =0)
            
            if self.verbose >=1:
                print('\tbest_cv_score:',self.models_dict[key]['best_cv_score'])
                print('\tbest_pred_score:',self.models_dict[key]['best_pred_score'])

            for metric_key in self.metrics.keys():
                if self.metrics[metric_key] !=None:
                    try:
                        self.models_dict[key][metric_key] = self.metrics[metric_key](y_test, y_pred)
                        print('\t',metric_key,':',self.models_dict[key][metric_key])
                    except Exception as e:
                        print('Exception occured for',metric_key,':',str(e))

            if 'sklearn' in str(type(self.models_dict[key]['model'])):
                self.save(self.models_dict[key], 'model_dict', 'dill', path_model_dir)
            elif 'Net' in key:
                model_dict_subset = self.models_dict[key].copy()
                for key in self.models_dict[key].keys():
                    if key not in ['y_test','y_pred','best_pred_score'] +list(self.metrics.keys()):
                        model_dict_subset.pop(key)
                        
            