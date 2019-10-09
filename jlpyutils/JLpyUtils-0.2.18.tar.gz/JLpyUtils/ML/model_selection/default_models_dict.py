"""
Fetch dictionary of default models for classification or regression tasks. The models_dict has the format of: 
    {model ID: {'model': model object,
                'param_grid': default parameter grid to run hypeparameter search on'}
     }
"""

import warnings as _warnings
import numpy as _np

def regression(n_features, 
               n_labels, 
               models = ['Linear','SVM','KNN','DecisionTree','RandomForest','xgboost','lightgbm','DenseNet'],
               ):
    """
    Fetch dictionary of standard regression models and their 'param_grid' dictionaries.
    
    Arguments: 
    ---------
        n_features, n_labels: The number of features and labels used for the model.
        models: list of models to fetch. Valid models include:
            - sklearn models: 'Linear', 'DecisionTree', 'RandomForest', 'GradBoost', 'SVM', 'KNN'
            - xgboost models: 'xgboost'
            - lighgbm models: 'lightgbm'
            - keras models: 'DenseNet'
            
    Returns:
    --------
        models_dict: dictionary of format {model ID: {'model': model object,
                                                    'param_grid': default parameter grid to run hypeparameter search on'}
                                           }
    """
    import sklearn
        
    models_dict = {}
    
    for model in models: #ensure the dictionary keys are in the order you specify in the models list
    
        if 'Linear' in model:
            import sklearn.linear_model
            models_dict['Linear'] = {'model':sklearn.linear_model.LinearRegression(),
                                     'param_grid': {'normalize': [False,True]}
                                    }
        if 'SVM' in model:
            _warnings.warn('SVMs do not scale well. The fit time complexity is more than quadratic with the number of samples which makes it hard to scale to datasets with more than a couple of 10000 samples.')
            import sklearn.svm
            if n_labels == 1:
                models_dict['SVM'] = {'model':sklearn.svm.SVR(),
                                      'param_grid': {'kernel':['rbf', 'sigmoid']} #'linear', 'poly', 
                                     }
            else:
                import sklearn.multioutput
                models_dict['SVM'] = {'model':sklearn.multioutput.MultiOutputRegressor(sklearn.svm.SVR()),
                                      'param_grid': {'estimator__kernel':['rbf', 'sigmoid']} #'linear', 'poly', 
                                     }
                

        if 'KNN' in model:
            import sklearn.neighbors
            models_dict['KNN'] = {'model': sklearn.neighbors.KNeighborsRegressor(),
                                  'param_grid': {'n_neighbors':[5, 10, 100],
                                                'weights':['uniform','distance'],
                                                'algorithm':['ball_tree','kd_tree','brute']}
                                 }

        if 'DecisionTree' in model:
            import sklearn.tree
            models_dict['DecisionTree'] = {'model':sklearn.tree.DecisionTreeRegressor(),
                                           'param_grid': {'criterion':     ['mse','friedman_mse'],#,'mae'],
                                                         'splitter':       ['best','random'],
                                                         'max_depth':      [None,5,10,100],
                                                         'max_features':   [0.25,0.5,0.75,1.0]}
                                          }
        if 'RandomForest' in model:
            import sklearn.ensemble
            models_dict['RandomForest'] = {'model': sklearn.ensemble.RandomForestRegressor(),
                                           'param_grid': {'criterion':      ['mse'],#'mae'],
                                                          'n_estimators':  [10,100],
                                                          'max_depth':      [None,5,10],
                                                          'max_features':   [0.25,0.5,0.75,1.0]}
                                          }
        if 'GradBoost' in model:
            import sklearn.ensemble
            models_dict['GradBoost'] = {'model':sklearn.ensemble.GradientBoostingRegressor(),
                                        'param_grid':{'loss':['ls', 'lad', 'huber', 'quantile'],
                                                      'criterion':["friedman_mse",'mse'], #,'mae']
                                                      'learning_rate':[0.01, 0.1, 1],
                                                      'n_estimators':[10, 100],
                                                      'subsample':[1.0,0.8,0.5],
                                                      'max_depth':[3, 10]}
                                       }

        if ('xgboost' in model or 'XGBoost' in model) and 'dask' not in model:                
            import xgboost
            from ... import ML
            
            device_counts = ML.device_counts()
            
#             if device_counts['GPUs']>1:
#                 tree_method = 'gpu_hist'
#             else:
            tree_method = 'auto'
            
            if n_labels == 1:
                models_dict['XGBoost'] = {'model':xgboost.XGBRegressor(
                                                         n_jobs = -1,
                                                         tree_method = tree_method),
                                          'param_grid':{'max_depth': [3,10],
                                                        'learning_rate':[0.01, 0.1, 1],
                                                        'n_estimators':[10, 100, 1000],
                                                        'subsample':[1.0, 0.9,0.5],
                                                        'colsample_bytree':[1.0,0.8,0.5],
                                                        #reg_alpha
                                                        #reg_lambda
                                                       }
                                     }
            else:
                import sklearn.multioutput
                models_dict['xgboost'] = {'model':sklearn.multioutput.MultiOutputRegressor(xgboost.XGBRegressor(
                                                         n_jobs = -1,
                                                         tree_method = tree_method)),
                                      'param_grid': {'estimator__max_depth': [3,10],
                                                        'estimator__learning_rate':[0.01, 0.1, 1],
                                                        'estimator__n_estimators':[10, 100, 1000],
                                                        'estimator__subsample':[1.0, 0.9,0.5],
                                                        'estimator__colsample_bytree':[1.0,0.8,0.5],
                                                        #reg_alpha
                                                        #reg_lambda
                                                       }
                                         }
        
        if 'dask_xgboost' in model or 'dask_XGBoost' in model:                
            import dask_ml, dask_ml.xgboost
            from ... import ML
            
            device_counts = ML.device_counts()
            
            if device_counts['GPUs']>1:
                tree_method = 'gpu_hist'
            else:
                tree_method = 'auto'
                
            models_dict['xgboost'] = {'model':dask_ml.xgboost.XGBRegressor(
                                                                 n_jobs = -1,
                                                                 tree_method = tree_method),
                                      'param_grid':{'max_depth': [3,10],
                                                    'learning_rate':[0.01, 0.1, 1],
                                                    'n_estimators':[10, 100, 1000],
                                                    'subsample':[1.0,0.9,0.5],
                                                    'colsample_bytree':[1.0,0.8,0.5],
                                                    #reg_alpha
                                                    #reg_lambda
                                                   }
                                 }

        if 'DenseNet' in model:
            from .. import NeuralNet
            models_dict['DenseNet'] = NeuralNet.DenseNet.model_dict(n_features=n_features,
                                                                     n_labels = n_labels,
                                                                    final_activation = 'elu',
                                                                    loss = 'mse',
                                                                    metrics=['mse','mae'])
        if 'lightgbm' in model:
            import lightgbm as _lgb
            from ... import ML
            
            if n_labels == 1:
                models_dict['lightgbm'] = {'model':_lgb.LGBMRegressor(objective= 'regression',
                                                                       metric = 'r2' ),
                                           'param_grid':{'learning_rate':[0.001, 0.01, 0.1],
                                                        'n_estimators':[10, 100, 1000, 5000],
                                                         'num_leaves':[31,256, 512],
                                                        'subsample':[1.0,0.9,0.5],
                                                        'colsample_bytree':[1.0,0.8,0.5],
                                                       }
                                          }
                device_counts = ML.device_counts()
                #if device_counts['GPUs']>1:
                models_dict['lightgbm']['model'].__dict__['gpu_device_id'] = 0
            
            elif n_labels>1:
                import sklearn.multioutput
                models_dict['lightgbm'] = { 'model':sklearn.multioutput.MultiOutputRegressor(
                                                _lgb.LGBMRegressor(
                                                                objective= 'regression',
                                                                metric = 'r2' )),
                                           'param_grid':{
                                               'estimator__learning_rate':[0.001, 0.01, 0.1],
                                               'estimator__n_estimators':[10, 100, 1000, 5000],
                                               'estimator__num_leaves':[31,256, 512],
                                               'estimator__subsample':[1.0,0.9,0.5],
                                               'estimator__colsample_bytree':[1.0,0.8,0.5],
                                                       }
                                          }
                device_counts = ML.device_counts()
                #if device_counts['GPUs']>1:
                models_dict['lightgbm']['model'].__dict__['estimator__gpu_device_id'] = 0
                
    return models_dict                       
                    
def classification(n_features, n_labels, 
               models = ['Logistic', 'SVM', 'KNN', 
                         'DecisionTree', 'RandomForest', 
                         'xgboost', 'DenseNet'],
               ):
    
    """
    Fetch dictionary of standard classification models and their 'param_grid' dictionaries.     
    
    Arguments: 
    ---------
        n_features, n_labels: The number of features and labels used for the model. These parameters are only required if 'DenseNet' is selected
        models: list of models to fetch. Valid models include:
            - sklearn models: 'Linear', 'DecisionTree', 'RandomForest', 'GradBoost', 'SVM', 'KNN'
            - xgboost models: 'Xoost'
            - lighgbm models: 'lightgbm'
            - keras modesl: 'DenseNet'
        Note: if running binary classfication, your labels should be 0 and 1. If running multiclass classifciation, your labels should be one-hot encoded
        
    """
    import sklearn
        
    models_dict = {}
    
    for model in models: #ensure the dictionary keys are in the order you specify in the models list

        if 'Logistic' in model:
            import sklearn.linear_model
            models_dict['Logistic'] = {'model':sklearn.linear_model.LogisticRegression(),
                                         'param_grid': {'penalty': ['l1', 'l2']}
                                        }
        if 'SVM' in model:
            import sklearn.svm
            models_dict['SVM'] = {'model':sklearn.svm.SVC(probability=True),
                                  'param_grid': {'kernel':['rbf', 'sigmoid'], #'linear', 'poly'
                                             }
                                 }
        if 'KNN' in model:
            import sklearn.neighbors
            models_dict['KNN'] = {'model': sklearn.neighbors.KNeighborsClassifier(),
                                  'param_grid': {'n_neighbors':[5, 10, 100],
                                                'weights':['uniform','distance'],
                                                'algorithm':['ball_tree','kd_tree','brute']}
                                 }

        if 'DecisionTree' in model:
            import sklearn.tree
            models_dict['DecisionTree'] = {'model':sklearn.tree.DecisionTreeRegressor(),
                                           'param_grid': {'criterion':     ['mse','friedman_mse'],#,'mae'],
                                                          'splitter':       ['best','random'],
                                                         'max_depth':      [None,5,10,100],
                                                         'max_features':   [0.25,0.5,0.75,1.0]}
                                          }
        if 'RandomForest' in model:
            import sklearn.ensemble
            models_dict['RandomForest'] = {'model': sklearn.ensemble.RandomForestClassifier(),
                                       'param_grid':{'criterion':['gini','entropy'],
                                                     'n_estimators':  [10,100],
                                                     'max_depth':      [None,5,10],
                                                     'max_features':   [0.25,0.5,0.75,1.0]}
                                       }
        if 'GradBoost' in model:
            import sklearn.ensemble
            models_dict['GradBoost'] = {'model': sklearn.ensemble.GradientBoostingClassifier(),
                                    'param_grid': {'loss':['deviance','exponential'],
                                                  'criterion':["friedman_mse",'mse'],#'mae' BAD. WON"T FINISH
                                                   'learning_rate':[0.001, 0.01, 0.1],
                                                   'n_estimators':[10, 100, 1000],
                                                   'subsample':[1.0,0.8,0.5],
                                                   'max_depth':[3, 10]}
                                   }

        if ('xgboost' in model or 'XGBoost' in model) and 'dask' not in model:                
            import xgboost
            from ... import ML
            
            device_counts = ML.device_counts()
            
            if device_counts['GPUs']>1:
                tree_method = 'gpu_hist'
            else:
                tree_method = 'auto'
                
            models_dict['xgboost'] = {'model':xgboost.XGBClassifier(
                                                     n_jobs = -1,
                                                     tree_method = tree_method),
                                      'param_grid':{'max_depth': [3,10],
                                                    'learning_rate':[0.01, 0.1, 1],
                                                    'n_estimators':[10, 100, 1000, 5000],
                                                    'subsample':[1.0, 0.9,0.5],
                                                    'colsample_bytree':[1.0,0.8,0.5],
                                                    #reg_alpha
                                                    #reg_lambda
                                                   }
                                 }
        
        if 'dask_XGBoost' in model or 'dask_xgboost' in model:                
            import dask_ml, dask_ml.xgboost
            from ... import ML
            
            device_counts = ML.device_counts()
            
            if device_counts['GPUs']>1:
                tree_method = 'gpu_hist'
            else:
                tree_method = 'auto'
            
            models_dict['xgboost'] = {'model': dask_ml.xgboost.XGBClassifier(
                                                                 n_jobs = -1,
                                                                 tree_method = tree_method),
                                      'param_grid':{'max_depth': [3,10],
                                                    'learning_rate':[0.001, 0.01, 0.1],
                                                    'n_estimators':[10, 100, 1000, 5000],
                                                    'subsample':[1.0,0.9,0.5],
                                                    'colsample_bytree':[1.0,0.8,0.5],
                                                    #reg_alpha
                                                    #reg_lambda
                                                   }
                                 }

        if 'DenseNet' in model:
            from .. import NeuralNet
            if n_labels > 1:
                loss = 'categorical_crossentropy'
            else:
                loss = 'binary_crossentropy'

            models_dict['DenseNet'] = NeuralNet.DenseNet.model_dict(n_features=n_features,
                                                                     n_labels = n_labels,
                                                                    final_activation = 'softmax',
                                                                    loss = loss,
                                                                    metrics=['accuracy'])
            
        if 'lightgbm' in model:
            import lightgbm as _lgb
            models_dict['lightgbm'] = {'model':_lgb.LGBMClassifier(metric= 'auc'),
                                       'param_grid':{'learning_rate':[0.001, 0.01, 0.1],
                                                    'n_estimators':[10, 100, 1000, 5000],
                                                     'num_leaves':[31,256, 512],
                                                    'subsample':[1.0,0.9,0.5],
                                                    'colsample_bytree':[1.0,0.8,0.5],
                                                   }
                                      }
            from ... import ML
            device_counts = ML.device_counts()
            if device_counts['GPUs']>1:
                models_dict['lightgbm']['model'].__dict__['gpu_device_id'] = 0
            
    return models_dict


