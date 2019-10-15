import sys, os
import numpy as np
import pandas as pd
import dask, dask.dataframe

import pytest

import JLpyUtils

def build_data_and_headers_dict():
    """
    Build a dictionary with different kinds of data to be tested on
    """
    
    #create some dummy data
    X1 = np.linspace(0,1,200)#*np.random.ranf(1000)
    X2 = X1#*np.random.ranf(1000)
    X3 = X1#*np.random.ranf(1000)

    y1 = X2 + 2*X2 + 3*X3
    y2 = X2 - 2*X2 - 3*X3
    
    df_X=pd.DataFrame(np.array([X1,X2,X3]).T,columns=['X1','X2','X3'])

    headers_dict={'continuous features': list(df_X.columns)}
    
    df_X['categorical int'] = list(np.random.randint(0,20, df_X.shape[0]))
    
    headers_dict['categorical features'] = ['categorical int']
    
    df_y = pd.DataFrame(y1, columns=['y1'])
    df_yy = pd.DataFrame(np.array([y1,y2]).T,columns=['y1','y2'])

    #build dask equivalent dataframes
    ddf_X = dask.dataframe.from_pandas(df_X, npartitions=3)
    ddf_y = dask.dataframe.from_pandas(df_y, npartitions= 3)
    ddf_yy = dask.dataframe.from_pandas(df_yy, npartitions= 3)
    
    data_dict = {'df_X':df_X,
                 'df_y':df_y,
                 'df_yy':df_yy,
                 'ddf_X':ddf_X,
                 'ddf_y':ddf_y,
                 'ddf_yy':ddf_yy}
    
    return data_dict, headers_dict

def test_regression_linear_single_output_pandas_df(tmpdir):

    data_dict, headers_dict = build_data_and_headers_dict()

    X = data_dict['df_X']
    y = data_dict['df_y']

    n_features = X.shape[1]
    n_labels = y.shape[1]

    models_dict = JLpyUtils.ML.model_selection.default_models_dict.regression(
                                                        n_features, 
                                                        n_labels,
                                                        models = ['Linear'])
    GridSearchCV = JLpyUtils.ML.model_selection.GridSearchCV(
                                     models_dict,
                                     cv=2,
                                     path_root_dir=tmpdir)
    GridSearchCV.fit(X, y, X, y)
    
def test_regression_xgboost_single_output_pandas_df(tmpdir):

    data_dict, headers_dict = build_data_and_headers_dict()

    X = data_dict['df_X']
    y = data_dict['df_y']

    n_features = X.shape[1]
    n_labels = y.shape[1]

    models_dict = JLpyUtils.ML.model_selection.default_models_dict.regression(
                                                        n_features, 
                                                        n_labels,
                                                        models = ['XGBoost'])
    GridSearchCV = JLpyUtils.ML.model_selection.GridSearchCV(
                                     models_dict,
                                     cv=2,
                                     path_root_dir=tmpdir)
    GridSearchCV.fit(X, y, X, y)
        
#     def test_linear_single_output_dask_df(self, tmpdir):
        
#         data_dict, headers_dict = build_data_and_headers_dict()

#         X = data_dict['ddf_X']
#         y = data_dict['ddf_y']

#         n_features = X.shape[1]
#         n_labels = y.shape[1]

#         models_dict = JLpyUtils.ML.model_selection.default_models_dict.regression(
#                                                             n_features, 
#                                                             n_labels,
#                                                             models = ['Linear'])
#         GridSearchCV = JLpyUtils.ML.model_selection.GridSearchCV(
#                                          models_dict,
#                                          cv=2,
#                                          path_root_dir=tmpdir)
#         GridSearchCV.fit(X, y, X, y)
        
    
    
    
# def test_multi_output_regression_models_GridSearchCV(tmpdir):
    
#     data_dict, headers_dict = build_data_and_headers_dict()
    
#     for dataframe_type in ['pandas','dask']:
            
#         if dataframe_type == 'pandas':
#             X = data_dict['df_X']
#             y = data_dict['df_yy']

#         elif dataframe_type=='dask':
#             X = data_dict['ddf_X']
#             y = data_dict['ddf_yy']

#         n_features = X.shape[1]
#         n_labels = y.shape[1]

#         models_dict = JLpyUtils.ML.model_selection.default_models_dict.regression(
#                                                                 n_features, 
#                                                                 n_labels)
#         GridSearchCV = JLpyUtils.ML.model_selection.GridSearchCV(
#                                                      models_dict,
#                                                      cv=2, 
#                                                      path_root_dir=tmpdir)
#         GridSearchCV.fit(X, y, X, y)
        
    
    