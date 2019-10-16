from . import LabelEncode
from . import Impute
from . import Scale
from . import OneHotEncode
from ._CorrCoeff import CorrCoeffThreshold
import warnings as _warnings

import os as _os
import sys as _sys
import gc as _gc

import pandas as _pd
import numpy as _np

class feat_eng_pipe():
    
    """
    Iterate through a standard feature engineering sequence and save the resulting engineered data.
    
    Arguments:
    ---------
        path_feat_eng_root_dir: directory. Default: 'feat_eng'. the path to the directory where the feature engineering cases will be saved. It is recommended that you save outside the repo. directory where the notebook is stored, as the saved files may be > 50mb.
        verbose: int. higher values implies more print outs
        overwrite: boolean. Defeault: False. whether to overwrite a previously generated feature engineering case if it has already been saved.
    Sequence:
    ---------
        BertWord2VecPCA ->
        LabelEncode.categorical_features ->  
        Scale.continuous_features -> 
            -for Scaler_ID in Scalers_dict.keys()
        Impute.categorical_features ->
            - for Imputer_cat_ID in Imputer_categorical_dict[Imputer_cat_ID].keys():
                - for Imputer_iter_class_ID in Imputer_categorical_dict[Imputer_cat_ID].keys():
        Imputer.continuous_features ->
            - for Imputer_cont_ID in Imputer_continuous_dict.keys():
                - for Imputer_iter_reg_ID in Imputer_continuous_dict[Imputer_cont_ID].keys():
        OneHotEncode ->
        CorrCoeffThreshold ->
        Finished!
    
    """
    def __init__(self, 
                 path_feat_eng_root_dir = 'feat_eng', 
                 verbose = 1, 
                 overwrite=False):
        
        _warnings.filterwarnings('ignore')
        
        self.path_feat_eng_root_dir = path_feat_eng_root_dir
        
        #build the feat_eng directory if it doesn't exist yet
        if _os.path.isdir(self.path_feat_eng_root_dir)==False:
            _os.makedirs(self.path_feat_eng_root_dir)
            
        self.verbose = verbose
        self.overwrite = overwrite
        
        #BertWord2VecPCA:
        self.BertWord2VecPCA_args = {'n_unique_threshold': 20,
                                     'PCA_n_components':0.99,
                                     'bert_model_ID': 'bert-base-uncased'}
        
        #define default OneHot_cases
        self.OneHot_cases = [True, False]
        
        #fetch Scalers_dict
        self.Scalers_dict = Scale.default_Scalers_dict()
        
        #fetch impute iterative classifier dict
        #Imputer_iterative_classifier_dict = {None: None} #Impute.default_iterative_classifier_dict()
            
        #Imputer categorical dict of form {method: estimator}
        self.Imputer_categorical_dict = {'most_frequent':{None:None},
                                         #'iterative': Imputer_iterative_classifier_dict
                                        }
        
        #Fetch impute iterative regressors dict
        Imputer_iterative_regressors_dict = Impute.default_iterative_regressors_dict()
        
        #Imputer continous dict of form {method: estimator}
        self.Imputer_continuous_dict = {'median':{None:None},
                                        'iterative': Imputer_iterative_regressors_dict
                                        }
        
        #CorrCoeffThresholder Params
        self.AbsCorrCoeff_thresholds = [0.99] 
        
        if _os.path.dirname(_os.path.abspath(__file__)) not in _sys.path:
            _sys.path.insert(0,  _os.path.dirname(_os.path.abspath(_os.path.join(__file__,'..','..'))))
        from ... import file_utils
        
        self.save = file_utils.save
        self.load = file_utils.load
        
        _warnings.filterwarnings('default')
        
    def _feat_eng_files_saved(self,
                                 files,
                                 path_feat_eng_dir, 
                                 format_ ):
        """
        Check if feat eng files are save for the specific case directory passed. Returns False if the X
        """
        
        _gc.collect()

        file_saved_list = []
        
        #build list of files to look for
        #files = [file+'.'+format_ for file in files]

        #check if all files exist
        for file in files:
            if format_ == 'h5_csv':
                h5_csv_file_saved_list = []
                for format_ in ['csv','h5']:
                    path_save_file = _os.path.join(path_feat_eng_dir, file+'.'+format_)
                    h5_csv_file_saved_list.append(_os.path.isfile(path_save_file))
                    
                #if either h5 or csv saved, append True
                file_saved_list.append(any(h5_csv_file_saved_list)) 
                
            else: #iterate through files in the dir & assert that each file is a file if it contains the format and filname. This loop ensures that if files are saved in chunks via dask, the function will recognize the "file" as saved
                
                for dir_file in _os.listdir(path_feat_eng_dir):
                    if '.'+format_ in dir_file and file in dir_file:
                        path_save_file = _os.path.join(path_feat_eng_dir, dir_file)
                        file_saved_list.append(_os.path.isfile(path_save_file))
                
        _gc.collect()
        
        #if all files saved, return True
        if len(file_saved_list)==0:
            file_saved_list=[False]
        feat_eng_files_saved = all(file_saved_list) 
        
        return feat_eng_files_saved      
    
    def _path_feat_eng_base_dir(self, path_feat_eng_dir, 
                                         OneHot_case,
                                          Scaler_ID,
                                          Imputer_cat_ID,
                                          Imputer_iter_class_ID,
                                          Imputer_cont_ID,
                                          Imputer_iter_reg_ID,
                                           AbsCorrCoeff_threshold):

        path_feat_eng_base_dir = _os.path.join(path_feat_eng_dir,
                                  'Scaler_ID['+Scaler_ID+']',
                                  'Imputer_categorical_ID['+Imputer_cat_ID+']',
                                  'Imputer_iterator_classifier_ID['+str(Imputer_iter_class_ID)+']',
                                  'Imputer_continuous_ID['+Imputer_cont_ID+']',
                                  'Imputer_iterator_regressor_ID['+str(Imputer_iter_reg_ID)+']',
                                  'OneHot_case['+str(OneHot_case)+']',
                                  'CorrCoeffThreshold['+str(AbsCorrCoeff_threshold)+']')
        return path_feat_eng_base_dir
    
    def _assert_n_samples_is_unchaged(self, X):
        
        if 'dask' in str(type(X)):
            n_samples_after_process = X.iloc[:,0].shape[0]
        else:
            n_samples_after_process = X.shape[0]

        assert(self.n_samples==n_samples_after_process), 'expected '+str(self.n_samples)+', but received '+str(n_samples_after_process)
        

 
    ######### Fit Transforme Operations ############
    
    def _fit_transform_BertWord2VecPCAer(self,
                                         X, 
                                         path_feat_eng_dir,
                                         format_):
        """
        Fit and Transform using BertWord2VecPCA function
        """
        from ..NeuralNet.Bert import Word2VecPCA as _BertWord2VecPCA

        method_ID = 'BertWord2VecPCA'
        if self.verbose>=1: print(method_ID)
            
        _gc.collect()

        files=['X']
        path_feat_eng_dir = _os.path.join(path_feat_eng_dir, method_ID)
        
        if _os.path.isdir(path_feat_eng_dir) == False:
            _os.makedirs(path_feat_eng_dir)
        
        if self._feat_eng_files_saved(files, path_feat_eng_dir, format_)==False or self.overwrite==True or self.overwrite==method_ID:
            
            self.BertWord2VecPCAer = _BertWord2VecPCA(**self.BertWord2VecPCA_args)
            
            X = self.BertWord2VecPCAer.fit_transform(X)
            self._assert_n_samples_is_unchaged(X)
            
            #update headers dict
            self.headers_dict['categorical features'] = [feat for feat in self.headers_dict['categorical features'] if feat not in self.BertWord2VecPCAer.vectorized_columns]
            self.headers_dict['continuous features'] = [feat for feat in X.columns if feat not in self.headers_dict['categorical features']]
            
            #save
            self.save(X, 'X', format_, path_feat_eng_dir)
            self.save(self.BertWord2VecPCAer, 'BertWord2VecPCAer', 'dill', path_feat_eng_dir)
            self.save(self.headers_dict, 'headers_dict', 'dill', path_feat_eng_dir)
            
        else: 
            del X
            _gc.collect()
                
            X = self.load('X', format_, path_feat_eng_dir)
            self._assert_n_samples_is_unchaged(X)
            
        _gc.collect()
        
        return X, path_feat_eng_dir
        
    
    def _fit_transform_LabelEncode(self,
                                    X, 
                                    path_feat_eng_dir,
                                    format_):
        method_ID = 'LabelEncode'
        if self.verbose>=1: print('\t'+method_ID)
            
        _gc.collect()

        #label encode X
        files=['X']
        path_feat_eng_dir = _os.path.join(path_feat_eng_dir, method_ID)
        
        if _os.path.isdir(path_feat_eng_dir) == False:
            _os.makedirs(path_feat_eng_dir)
        
        if self._feat_eng_files_saved(files, path_feat_eng_dir, format_)==False or self.overwrite==True or self.overwrite==method_ID:
            self.LabelEncoder = LabelEncode.categorical_features()
            self.LabelEncoder.fit(X, categorical_headers=self.headers_dict['categorical features'])

            X = self.LabelEncoder.transform(X)
            self._assert_n_samples_is_unchaged(X)
            
            #save
            self.save(X, 'X', format_, path_feat_eng_dir)
            self.save(self.LabelEncoder, 'LabelEncoder', 'dill', path_feat_eng_dir)
            self.save(self.headers_dict, 'headers_dict', 'dill', path_feat_eng_dir)

        else: 
            del X
            _gc.collect()
                
            X = self.load('X', format_, path_feat_eng_dir)
            self.LabelEncoder = self.load('LabelEncoder', 'dill', path_feat_eng_dir)
            self._assert_n_samples_is_unchaged(X)
            
        _gc.collect()
        return X, path_feat_eng_dir
    
    
    def _fit_transform_Scale(self,
                            X, 
                            path_feat_eng_dir,
                            format_,
                            Scaler_ID,
                            Imputer_cat_ID,
                            Imputer_iter_class_ID):
        """
        Scale, transform, and save the continuous data
        """
        method_ID = 'Scale'
        if self.verbose>=1: print('\t'+method_ID+':',Scaler_ID)
        
        _gc.collect()

        path_feat_eng_dir = _os.path.join(path_feat_eng_dir,'Scaler_ID['+Scaler_ID+']')
        
        files=['X']
        if self._feat_eng_files_saved(files, path_feat_eng_dir, format_)==False or self.overwrite==True:

            self.Scaler = Scale.continuous_features(Scaler = self.Scalers_dict[Scaler_ID])
            self.Scaler.fit(X, self.headers_dict['continuous features'])
            
            X = self.Scaler.transform(X)
            self._assert_n_samples_is_unchaged(X)
            
            #save
            self.save(X, 'X', format_, path_feat_eng_dir)
            self.save(self.Scaler, 'Scaler', 'dill', path_feat_eng_dir)
            self.save(self.headers_dict, 'headers_dict', 'json', path_feat_eng_dir)

        else:
            #check if the step after this has been completed, if not load the data here
            path_next_step = _os.path.join(path_feat_eng_dir, 
                                          'Imputer_categorical_ID['+Imputer_cat_ID+']',
                                          'Imputer_iterator_classifier_ID['+str(Imputer_iter_class_ID)+']')
            if self._feat_eng_files_saved(files, path_next_step, format_)==False:
                del X
                _gc.collect()
                X = self.load('X', format_, path_feat_eng_dir)
                self._assert_n_samples_is_unchaged(X)
                
                self.headers_dict = self.load('headers_dict', 'json', path_feat_eng_dir)
                
        _gc.collect()

        return X, path_feat_eng_dir
   
    def _fit_transform_Impute_categorical(self,
                                           X, 
                                          path_feat_eng_dir,
                                          format_,
                                          Imputer_cat_ID,
                                          Imputer_iter_class_ID,
                                          Imputer_cont_ID,
                                          Imputer_iter_reg_ID):
        """
        Impute, transform, and save the categorical data
        """
        
        _gc.collect()
        
        if self.verbose>=1: print('\t\tImpute Categorical Features:',
                                              Imputer_cat_ID,'[',Imputer_iter_class_ID,']')

        
        path_feat_eng_dir = _os.path.join(path_feat_eng_dir, 
                                   'Imputer_categorical_ID['+Imputer_cat_ID+']',
                                   'Imputer_iterator_classifier_ID['+str(Imputer_iter_class_ID)+']')
        
        files=['X']
        if self._feat_eng_files_saved(files, path_feat_eng_dir, format_)==False or self.overwrite==True:

            X, Imputer = Impute.categorical_features(X, 
                                                    self.headers_dict['categorical features'], 
                                                    strategy = Imputer_cat_ID, 
                                                    estimator = self.Imputer_categorical_dict[Imputer_cat_ID][Imputer_iter_class_ID],
                                                    verbose= 0)
            self._assert_n_samples_is_unchaged(X)

            #save
            self.save(X, 'X', format_, path_feat_eng_dir)
            self.save(Imputer, 'Imputer', 'dill', path_feat_eng_dir)
            self.save(self.headers_dict, 'headers_dict', 'json', path_feat_eng_dir)

        else:
            #check if the step after this has been completed, if not load the data here
            path_next_step = _os.path.join(path_feat_eng_dir, 
                                          'Imputer_continuous_ID['+Imputer_cont_ID+']',
                                          'Imputer_iterator_regressor_ID['+str(Imputer_iter_reg_ID)+']')
            if self._feat_eng_files_saved(files, path_next_step, format_)==False:
                del X
                _gc.collect()
                
                X = self.load('X', format_, path_feat_eng_dir)
                self._assert_n_samples_is_unchaged(X)
                self.headers_dict = self.load('headers_dict', 'json', path_feat_eng_dir)
                
        _gc.collect()

        return X, path_feat_eng_dir
        
        
    def _fit_transform_Impute_continuous(self,
                                  X, 
                                  path_feat_eng_dir,
                                  format_,
                                  Imputer_cont_ID,
                                  Imputer_iter_reg_ID,
                                  OneHot_case):
        """
        Impute, transform, and save the continuous data
        """
        
        if self.verbose>=1: print('\t\t\tImpute Continuous Features:',
                                                      Imputer_cont_ID,'[',Imputer_iter_reg_ID,']')

        
        _gc.collect()

        path_feat_eng_dir = _os.path.join(path_feat_eng_dir, 
                               'Imputer_continuous_ID['+Imputer_cont_ID+']',
                               'Imputer_iterator_regressor_ID['+str(Imputer_iter_reg_ID)+']')
        files=['X']
        if self._feat_eng_files_saved(files, path_feat_eng_dir, format_)==False or self.overwrite==True:

            X, Imputer = Impute.continuous_features(X, 
                    self.headers_dict['continuous features'], 
                    strategy = Imputer_cont_ID, 
                    estimator = self.Imputer_continuous_dict[Imputer_cont_ID][Imputer_iter_reg_ID],
                    verbose= 0)
            self._assert_n_samples_is_unchaged(X)

            #save
            self.save(X, 'X', format_, path_feat_eng_dir)
            self.save(Imputer, 'Imputer', 'dill', path_feat_eng_dir)
            self.save(self.headers_dict, 'headers_dict', 'json', path_feat_eng_dir)

        else:
            #check if the step after this has been completed, if not load the data here
            path_next_step = _os.path.join(path_feat_eng_dir,'OneHot_case['+str(OneHot_case)+']')
            
            if self._feat_eng_files_saved(files, path_next_step, format_)==False or self.overwrite=='OneHot':
                del X
                _gc.collect()
                
                X = self.load('X', format_, path_feat_eng_dir)
                self._assert_n_samples_is_unchaged(X)
                 
                if format_ != 'csv' and format_!='hdf':
                    
                    X = _pd.DataFrame(X, columns = self.headers_dict['features'])
                    self.headers_dict = self.load('headers_dict', 'json', self.path_feat_eng_root_dir)
                    
        _gc.collect()
        
        return X, path_feat_eng_dir

    def _fit_transform_OneHot_Encode(self,
                              X, 
                              path_feat_eng_dir,
                              format_,
                              OneHot_case,
                              AbsCorrCoeff_threshold):
        """
        OneHotEncode, transform, and save the categorical data
        """
        
        if self.verbose>=1: print('\t\t\t\tOne Hot Encode:','[',OneHot_case,']')
                                
        _gc.collect()

        path_feat_eng_dir = _os.path.join(path_feat_eng_dir, 'OneHot_case['+str(OneHot_case)+']')
        
        files=['X']
        if self._feat_eng_files_saved(files, path_feat_eng_dir, format_)==False or self.overwrite==True or self.overwrite=='OneHot' or self.overwrite == 'OneHotEncode' or self.overwrite == 'OneHot_Encode':

            if OneHot_case:
                
                #return_format='npArray'
                return_format='DataFrame'
                
                OneHotEncoder = OneHotEncode.categorical_features(return_format = return_format,
                                                                  LabelEncoder = self.LabelEncoder)
                OneHotEncoder.fit(X, categorical_headers=self.headers_dict['categorical features'])

                X = OneHotEncoder.transform(X)
                self._assert_n_samples_is_unchaged(X)
                
                #save the self.headers_dict after one hot
                self.headers_dict['headers after OneHot'] = OneHotEncoder.headers_after_OneHot

                #save the encoder
                self.save(OneHotEncoder, 'OneHotEncoder', 'dill', path_feat_eng_dir)

            else: #if OneHot is False, just skip transform to numpy array
                self.headers_dict['headers after OneHot'] = list(X.columns)
                #X = _np.array(X)
                   
            #save 
            self.save(X, 'X', format_, path_feat_eng_dir)
            self.save(self.headers_dict, 'headers_dict', 'json', path_feat_eng_dir)
            
            #transform back to pandas df
            #X = _pd.DataFrame(X, columns = self.headers_dict['headers after OneHot'])
            
        else:
            #check if the step after this has been completed, if not load the data here
            path_next_step = _os.path.join(path_feat_eng_dir,'CorrCoeffThreshold['+str(AbsCorrCoeff_threshold)+']')
            
            if self._feat_eng_files_saved(files, path_next_step, format_)==False or self.overwrite=='CorrCoeffThreshold' or self.overwrite=='CorrCoeff' or self.overwrite=='CorrCoeffThresholder' :
                del X
                _gc.collect()
            
                X = self.load('X', format_, path_feat_eng_dir)
                self._assert_n_samples_is_unchaged(X)
                self.headers_dict = self.load('headers_dict', 'json', path_feat_eng_dir)
                 
                #transform back to pandas df
                #X = _pd.DataFrame(X, columns = self.headers_dict['headers after OneHot'])

        _gc.collect()

        return X, path_feat_eng_dir, self.headers_dict
    
    def _fit_transform_CorrCoeffThreshold(self,
                                          X, 
                                          path_feat_eng_dir,
                                          format_,
                                          AbsCorrCoeff_threshold):
        """
        fit a Correlation Coefficient Threshold object, transform, and save
        """

        if self.verbose>=1: print('\t\t\t\t\tCorrCoeffThreshold:','[',AbsCorrCoeff_threshold,']')
        
        _gc.collect()

        path_feat_eng_dir = _os.path.join(path_feat_eng_dir,'CorrCoeffThreshold['+str(AbsCorrCoeff_threshold)+']')
        
        files=['X']
        if self._feat_eng_files_saved(files, path_feat_eng_dir, format_)==False or self.overwrite==True  or self.overwrite=='CorrCoeffThreshold' or self.overwrite=='CorrCoeff' or self.overwrite=='CorrCoeffThresholder' :

            if AbsCorrCoeff_threshold!=1:
                
                CorrCoeffThresholder = CorrCoeffThreshold(AbsCorrCoeff_threshold)
                CorrCoeffThresholder.fit(X)

                X = CorrCoeffThresholder.transform(X)
                self._assert_n_samples_is_unchaged(X)
                
                #save the encoder
                self.save(CorrCoeffThresholder, 'CorrCoeffThresholder', 'dill', path_feat_eng_dir)
   
            self.headers_dict['headers after CorrCoeffThreshold'] = list(X.columns)

            #save
            self.save(X, 'X', format_, path_feat_eng_dir)
            self.save(self.headers_dict, 'headers_dict', 'json', path_feat_eng_dir)
            
        else:
            del X
            _gc.collect()
            
            #load
            X = self.load('X', format_, path_feat_eng_dir)
            self._assert_n_samples_is_unchaged(X)
            self.headers_dict = self.load('headers_dict', 'json', path_feat_eng_dir)
        
            if format_ != 'csv':
                
                X = _pd.DataFrame(X, columns = self.headers_dict['headers after CorrCoeffThreshold'])

        _gc.collect()

        return X, path_feat_eng_dir, self.headers_dict

    
    def _fit_transform_feat_eng_case(self,
                                      X,
                                      path_feat_eng_dir,
                                      format_,
                                      Scaler_ID,
                                      Imputer_cat_ID,
                                      Imputer_iter_class_ID,
                                      Imputer_cont_ID,
                                      Imputer_iter_reg_ID,
                                      OneHot_case,
                                      AbsCorrCoeff_threshold):
        """
        run through a single feature engineering case instance (after Label Encoding)
        Arguments:
        ----------
            X, X_field: the datasets to run feature engineering on
            ...
        """
        import os, sys
        import gc
        
        _gc.collect()
        
        #build feat_eng_case_base_dir
        path_feat_eng_base_dir = self._path_feat_eng_base_dir(path_feat_eng_dir, 
                                                              OneHot_case,
                                                              Scaler_ID,
                                                              Imputer_cat_ID,
                                                              Imputer_iter_class_ID,
                                                              Imputer_cont_ID,
                                                              Imputer_iter_reg_ID,
                                                              AbsCorrCoeff_threshold)
        if _os.path.isdir(path_feat_eng_base_dir)==False:
            _os.makedirs(path_feat_eng_base_dir)

        #check if all the required files are saved in the base directory
        all_data_previously_saved = True
        for filename in ['X', 'headers_dict.json']:

            if 'headers_dict' not in filename:
                filename = filename+'.'+format_

            path_save_file = _os.path.join(path_feat_eng_base_dir, filename)
            if _os.path.isfile(path_save_file)==False:
                all_data_previously_saved = False

        if all_data_previously_saved==False or self.overwrite == True: 

            X = X.copy()
            self.headers_dict = self.headers_dict.copy()

            ####### Scale #########
            X, path_feat_eng_dir = self._fit_transform_Scale(X, 
                                                            path_feat_eng_dir,
                                                            format_,
                                                            Scaler_ID,
                                                            Imputer_cat_ID,
                                                            Imputer_iter_class_ID)
            ####### Impute Categorical Features #########
            X, path_feat_eng_dir = self._fit_transform_Impute_categorical(X, 
                                                              path_feat_eng_dir,
                                                              format_,
                                                              Imputer_cat_ID,
                                                              Imputer_iter_class_ID,
                                                              Imputer_cont_ID,
                                                              Imputer_iter_reg_ID)

            ###### Impute Continuous Features ########
            X, path_feat_eng_dir = self._fit_transform_Impute_continuous(X, 
                                                                      path_feat_eng_dir,
                                                                      format_,
                                                                      Imputer_cont_ID,
                                                                      Imputer_iter_reg_ID,
                                                                      OneHot_case)

            ##### One Hot Encode #####
            X, path_feat_eng_dir, self.headers_dict = self._fit_transform_OneHot_Encode(X, 
                                                                      path_feat_eng_dir,
                                                                      format_,
                                                                      OneHot_case,
                                                                      AbsCorrCoeff_threshold)
            
            ##### CorreCoeffThreshold #####
            X, path_feat_eng_dir, self.headers_dict = self._fit_transform_CorrCoeffThreshold(X, 
                                                                          path_feat_eng_dir,
                                                                          format_,
                                                                          AbsCorrCoeff_threshold)
            
            assert(path_feat_eng_base_dir == path_feat_eng_dir)

            del X
            _gc.collect()
            
        else:
            print('pre-existing saved data found at path_feat_eng_dir:', path_feat_eng_base_dir)
        
    ############# Transform Operations #########################

    def _transform_BertWord2VecPCAer(self, X_field, path_feat_eng_dir):
        """
        Transform and save X_field using LabelEncoder
        """
        
        method_ID = 'BertWord2VecPCA'
        if self.verbose>=1: print(method_ID)
        
        _gc.collect()

        path_feat_eng_dir = _os.path.join(path_feat_eng_dir, method_ID)
        
        files=['X_field']
        if self._feat_eng_files_saved(files, path_feat_eng_dir, self.format_)==False or self.overwrite==True or self.overwrite==method_ID:
            
            self.BertWord2VecPCAer = self.load('BertWord2VecPCAer', 'dill', path_feat_eng_dir)
            
            X_field = self.BertWord2VecPCAer.transform(X_field)
            self._assert_n_samples_is_unchaged(X_field)

            #save
            self.save(X_field, 'X_field', self.format_, path_feat_eng_dir)
            
        else: 
            del X_field
            _gc.collect()
            
            X_field = self.load('X_field', self.format_, path_feat_eng_dir)
            self._assert_n_samples_is_unchaged(X_field)
        
        _gc.collect()
        return X_field, path_feat_eng_dir
    
    def _transform_LabelEncode(self, X_field, path_feat_eng_dir):
        """
        Transform and save X_field using LabelEncoder
        """
        
        if self.verbose>=1: print('LabelEncode')
        
        _gc.collect()

        #label encode X
        path_feat_eng_dir = _os.path.join(path_feat_eng_dir, 'LabelEncode')
        
        files=['X_field']
        if self._feat_eng_files_saved(files, path_feat_eng_dir, self.format_)==False or self.overwrite==True or self.overwrite=='LabelEncode':
            
            LabelEncoder = self.load('LabelEncoder', 'dill', path_feat_eng_dir)
            
            X_field = LabelEncoder.transform(X_field)
            self._assert_n_samples_is_unchaged(X_field)

            #save
            self.save(X_field, 'X_field', self.format_, path_feat_eng_dir)
            
        else: 
            del X_field
            _gc.collect()
            
            X_field = self.load('X_field', self.format_, path_feat_eng_dir)
            self._assert_n_samples_is_unchaged(X_field)
        
        _gc.collect()
        return X_field, path_feat_eng_dir
                
      
    def _transform_Scale(self,
                        X_field, 
                        path_feat_eng_dir,
                        Scaler_ID,
                        Imputer_cat_ID,
                        Imputer_iter_class_ID):
        """
        transform, and save the continuous data
        """
        
        if self.verbose>=1: print('\tScale:',Scaler_ID)
        
        _gc.collect()

        path_feat_eng_dir = _os.path.join(path_feat_eng_dir, 'Scaler_ID['+Scaler_ID+']')
        
        files=['X_field']
        if self._feat_eng_files_saved(files, path_feat_eng_dir, self.format_)==False or self.overwrite==True:

            Scaler = self.load('Scaler', 'dill', path_feat_eng_dir)
            
            X_field = Scaler.transform(X_field)
            self._assert_n_samples_is_unchaged(X_field)

            #save
            self.save(X_field, 'X_field', self.format_, path_feat_eng_dir)
            
        else:
            #check if the step after this has been completed, if not load the data here
            path_next_step = _os.path.join(path_feat_eng_dir, 
                                  'Imputer_categorical_ID['+Imputer_cat_ID+']',
                                  'Imputer_iterator_classifier_ID['+str(Imputer_iter_class_ID)+']')
            if self._feat_eng_files_saved(files, path_next_step, self.format_)==False:
                X_field = self.load('X_field', self.format_, path_feat_eng_dir)
                self._assert_n_samples_is_unchaged(X_field)
        
        _gc.collect()

        return X_field, path_feat_eng_dir   
    
    def _transform_Impute_categorical(self,
                                   X_field, 
                                   path_feat_eng_dir,
                                   Imputer_cat_ID,
                                   Imputer_iter_class_ID,
                                   Imputer_cont_ID,
                                   Imputer_iter_reg_ID):
        """
        Transform and save the categorical data using the fitted Imputer
        """
        import os, sys
        import gc
        
        if self.verbose>=1: print('\t\tImpute Categorical Features:',
                                              Imputer_cat_ID,'[',Imputer_iter_class_ID,']')

        _gc.collect()

        path_feat_eng_dir = _os.path.join(path_feat_eng_dir, 
                                  'Imputer_categorical_ID['+Imputer_cat_ID+']',
                                  'Imputer_iterator_classifier_ID['+str(Imputer_iter_class_ID)+']')
        files=['X_field']
        if self._feat_eng_files_saved(files, path_feat_eng_dir, self.format_)==False or self.overwrite==True:

            Imputer = self.load('Imputer', 'dill', path_feat_eng_dir)
            
            type_X_field = type(X_field)
            import dask
            if type_X_field==dask.dataframe.core.DataFrame:
                npartitions = X_field.npartitions
                X_field = X_field.compute()
            
            X_field[self.headers_dict['categorical features']] = Imputer.transform(X_field[self.headers_dict['categorical features']])
            self._assert_n_samples_is_unchaged(X_field)
            
            if type_X_field==dask.dataframe.core.DataFrame:
                X_field = dask.dataframe.from_pandas(X_field, npartitions=npartitions)
         

            #save
            self.save(X_field, 'X_field', self.format_, path_feat_eng_dir)

        else:
            #check if the step after this has been completed, if not load the data here
            path_next_step = _os.path.join(path_feat_eng_dir, 
                                          'Imputer_continuous_ID['+Imputer_cont_ID+']',
                                          'Imputer_iterator_regressor_ID['+str(Imputer_iter_reg_ID)+']')
            if self._feat_eng_files_saved(files, path_next_step, self.format_)==False:
                X_field = self.load('X_field', self.format_, path_feat_eng_dir)
                self._assert_n_samples_is_unchaged(X_field)
        
        _gc.collect()

        return X_field, path_feat_eng_dir
        
        
    def _transform_Impute_continuous(self,
                                  X_field, 
                                  path_feat_eng_dir,
                                  Imputer_cont_ID,
                                  Imputer_iter_reg_ID,
                                  OneHot_case):
        """
        Impute, transform, and save the continuous data
        """
        import os, sys
        import gc
        
        if self.verbose>=1: print('\t\t\tImpute Continuous Features:',
                                  Imputer_cont_ID,'[',Imputer_iter_reg_ID,']')

        
        _gc.collect()

        path_feat_eng_dir = _os.path.join(path_feat_eng_dir, 
                                      'Imputer_continuous_ID['+Imputer_cont_ID+']',
                                      'Imputer_iterator_regressor_ID['+str(Imputer_iter_reg_ID)+']')
        files=['X_field']
        if self._feat_eng_files_saved(files, path_feat_eng_dir, self.format_)==False or self.overwrite==True:

            Imputer = self.load('Imputer', 'dill', path_feat_eng_dir)
            
            type_X_field = type(X_field)
            import dask
            if type_X_field==dask.dataframe.core.DataFrame:
                npartitions = X_field.npartitions
                X_field = X_field.compute()
            
            X_field[self.headers_dict['continuous features']] = Imputer.transform(X_field[self.headers_dict['continuous features']])
            self._assert_n_samples_is_unchaged(X_field)
            
            if type_X_field==dask.dataframe.core.DataFrame:
                X_field = dask.dataframe.from_pandas(X_field, npartitions=npartitions)
         
            #save
            self.save(X_field, 'X_field', self.format_, path_feat_eng_dir)

        else:
            #check if the step after this has been completed, if not load the data here
            path_next_step = _os.path.join(path_feat_eng_dir,'OneHot_case['+str(OneHot_case)+']')
            if self._feat_eng_files_saved(files, path_next_step, self.format_)==False or self.overwrite=='OneHot':
                X_field = self.load('X_field', self.format_, path_feat_eng_dir)
                self._assert_n_samples_is_unchaged(X)
                    
                if self.format_ != 'csv':
                    import pandas as pd
                    X_field = _pd.DataFrame(X_field, columns = self.headers_dict['features'])
        
        _gc.collect()
        
        return X_field, path_feat_eng_dir

    def _transform_OneHot_Encode(self,
                              X_field, 
                              path_feat_eng_dir,
                              OneHot_case,
                              AbsCorrCoeff_threshold):
        """
        OneHotEncode, transform, and save the categorical data
        """
        
        import os, sys
        import numpy as np
        import gc
        
        if self.verbose>=1: print('\t\t\t\tOne Hot Encode:','[',OneHot_case,']')
        
        _gc.collect()

        path_feat_eng_dir = _os.path.join(path_feat_eng_dir, 'OneHot_case['+str(OneHot_case)+']')
        
        files=['X_field']
        if self._feat_eng_files_saved(files, path_feat_eng_dir, self.format_)==False or self.overwrite==True or self.overwrite=='OneHot' or self.overwrite == 'OneHotEncode' or self.overwrite == 'OneHot_Encode':

            if OneHot_case:
                #fetch the label encoder
                self.LabelEncoder = self.load('LabelEncoder', 'dill',
                                      _os.path.join(self.path_feat_eng_root_dir, 'BertWord2VecPCA','LabelEncode') )
                
                
                OneHotEncoder = self.load('OneHotEncoder', 'dill', path_feat_eng_dir)
                
                X_field = OneHotEncoder.transform(X_field)
                self._assert_n_samples_is_unchaged(X_field)
                
            else: #if OneHot is False, just skip transform to numpy array
                #X_field = _np.array(X_field) 
                None
                    
            #save
            self.save(X_field, 'X_field', self.format_, path_feat_eng_dir)
            
        else:
             #check if the step after this has been completed, if not load the data here
            path_next_step = _os.path.join(path_feat_eng_dir,'CorrCoeffThreshold['+str(AbsCorrCoeff_threshold)+']')
            
            if self._feat_eng_files_saved(files, path_next_step, self.format_)==False or self.overwrite=='CorrCoeffThreshold' or self.overwrite=='CorrCoeff' or self.overwrite=='CorrCoeffThresholder' :
                del X_field
                _gc.collect()
                
                X_field = self.load('X_field', self.format_, path_feat_eng_dir)
                
                self.headers_dict = self.load('headers_dict', 'json', path_feat_eng_dir)
                 
                #transform back to pandas df
                import pandas as pd
                X_field  = _pd.DataFrame(X_field, columns = self.headers_dict['headers after OneHot'])
                self._assert_n_samples_is_unchaged(X_field)
            
        _gc.collect()

        return X_field, path_feat_eng_dir
    
    def _transform_CorrCoeffThreshold(self,
                                          X_field, 
                                          path_feat_eng_dir,
                                          AbsCorrCoeff_threshold):
        """
        OneHotEncode, transform, and save the categorical data
        """

        if self.verbose>=1: print('\t\t\t\t\tCorrCoeffThreshold:','[',AbsCorrCoeff_threshold,']')
        
        _gc.collect()

        path_feat_eng_dir = _os.path.join(path_feat_eng_dir,'CorrCoeffThreshold['+str(AbsCorrCoeff_threshold)+']')
        
        files=['X_field']
        if self._feat_eng_files_saved(files, path_feat_eng_dir, self.format_)==False or self.overwrite==True  or self.overwrite=='CorrCoeffThreshold' or self.overwrite=='CorrCoeff' or self.overwrite=='CorrCoeffThresholder' :

            if AbsCorrCoeff_threshold!=1:
                
                CorrCoeffThresholder = self.load('CorrCoeffThresholder', 'dill', path_feat_eng_dir)
                
                X_field = CorrCoeffThresholder.transform(X_field)
                self._assert_n_samples_is_unchaged(X_field)
                
            #save
            self.save(X_field, 'X_field', self.format_, path_feat_eng_dir)
            
        else:
            del X_field
            _gc.collect()
            
            #load
            X_field = self.load('X_field', self.format_, path_feat_eng_dir)
            self._assert_n_samples_is_unchaged(X_field)
            
            self.headers_dict = self.load('headers_dict', 'json', path_feat_eng_dir)
        
            if self.format_ != 'csv':
                import pandas as pd
                X_field = _pd.DataFrame(X_field, columns = self.headers_dict['headers after CorrCoeffThreshold'])
                

        _gc.collect()

        return X_field, path_feat_eng_dir
      
    def _transform_feat_eng_case(self,
                                  X_field,
                                  path_feat_eng_dir,
                                  Scaler_ID,
                                  Imputer_cat_ID,
                                  Imputer_iter_class_ID,
                                  Imputer_cont_ID,
                                  Imputer_iter_reg_ID,
                                  OneHot_case,
                                  AbsCorrCoeff_threshold):
        """
        Run through a single feature engineering case instance (after Label Encoding)
        
        Arguments:
        ----------
            X_field: the datasets to run feature engineering on
            ...
        """

        _gc.collect()
        
        #define feat_eng_case_base_dir
        path_feat_eng_base_dir = self._path_feat_eng_base_dir(path_feat_eng_dir, 
                                                              OneHot_case,
                                                              Scaler_ID,
                                                              Imputer_cat_ID,
                                                              Imputer_iter_class_ID,
                                                              Imputer_cont_ID,
                                                              Imputer_iter_reg_ID,
                                                              AbsCorrCoeff_threshold)

        #check if all the required files are saved in the base directory
        all_data_previously_saved = True
        for filename in ['X_field', 'headers_dict.json']:

            if 'headers_dict' not in filename:
                filename = filename+'.'+self.format_

            path_save_file = _os.path.join(path_feat_eng_base_dir, filename)
            if _os.path.isfile(path_save_file)==False:
                all_data_previously_saved = False
                
        if all_data_previously_saved==False or self.overwrite == True: 

            X_field = X_field.copy()
            
            ####### Scale #########
            X_field, path_feat_eng_dir = self._transform_Scale(X_field, 
                                                                    path_feat_eng_dir,
                                                                    Scaler_ID,
                                                                    Imputer_cat_ID,
                                                                    Imputer_iter_class_ID)
            ####### Impute Categorical Features #########
            X_field, path_feat_eng_dir = self._transform_Impute_categorical(X_field, 
                                                                              path_feat_eng_dir,
                                                                              Imputer_cat_ID,
                                                                              Imputer_iter_class_ID,
                                                                              Imputer_cont_ID,
                                                                              Imputer_iter_reg_ID)

            ###### Impute Continuous Features ########
            X_field, path_feat_eng_dir = self._transform_Impute_continuous(X_field, 
                                                                              path_feat_eng_dir,
                                                                              Imputer_cont_ID,
                                                                              Imputer_iter_reg_ID,
                                                                              OneHot_case)

            ##### One Hot Encode #####
            X_field, path_feat_eng_dir = self._transform_OneHot_Encode(X_field, 
                                                                          path_feat_eng_dir,
                                                                          OneHot_case,
                                                                          AbsCorrCoeff_threshold)
            
            #### CorrCoeffThreshold #####
            X_field, path_feat_eng_dir = self._transform_CorrCoeffThreshold(X_field, 
                                                                                  path_feat_eng_dir,
                                                                                  AbsCorrCoeff_threshold)
           
            del X_field
            _gc.collect()
            
        else:
            print('pre-existing saved data found at path_feat_eng_dir:', path_feat_eng_base_dir)
        
        
    def fit(self,
            X, 
            headers_dict,
            format_ = 'csv'):
        """
        Run standard feature engineering processes on data.
        Arguments:
            X: pandas dataframe. The train and test set features which will be engineered
            self.headers_dict: dictionary containing a list of headers. The required keys are
                - categorical features
                - continuous features
            format_: string. Default: 'csv'.
                - 'csv': saves the engineered data as a csv using pandas or numpy
                - 'h5': saves the engineered data as h5 dataset
        """

        _gc.collect()
        
        self.headers_dict = headers_dict.copy()
        
        for key_header in ['categorical features', 'continuous features']:
            assert(key_header in self.headers_dict.keys()), 'headers_dict is missing the "'+key_header+'" key'
            
        X = X.copy()     
        
        self.format_ = format_ 
        
        #ensure only the features identified in the headers dict are passed
        n_features = X[self.headers_dict['categorical features']+self.headers_dict['continuous features']].shape[1]
        assert(n_features == X.shape[1]), 'headers_dict specifies '+str(n_features)+' features, but X contains'+str(X.shape[1])+' features. Update the X dataframe or headers_dict["categorical features"]+headers_dict["continuous features"]'
        
        if 'dask' in str(type(X)):
            self.n_samples = X.iloc[:,0].compute().shape[0]
        else:
            self.n_samples = X.shape[0]
        
        if self.verbose>=2: 
            print('X.info():')
            X.info()
            
        #Save X
        path_feat_eng_dir = self.path_feat_eng_root_dir 
        
        files=['X']
        if self._feat_eng_files_saved(files, path_feat_eng_dir, format_) == False or self.overwrite==True:
            self.save(X, 'X', format_, path_feat_eng_dir)
                
            #save the original headers dict
            self.headers_dict['features'] = list(X.columns)
            self.save(self.headers_dict,  'headers_dict', 'json', path_feat_eng_dir)

        #Run the pipe
        print('-------------------------------- feat_eng_pipe fit --------------------------------')
        
        #BertWord2VecPCA
        X, path_feat_eng_dir = self._fit_transform_BertWord2VecPCAer(X, 
                                                                     path_feat_eng_dir,
                                                                     format_)
        
        #LabelEncode
        X, path_feat_eng_dir = self._fit_transform_LabelEncode(X, 
                                                               path_feat_eng_dir,
                                                               format_)
        
        self.path_feat_eng_dirs = []
        
        for Scaler_ID in self.Scalers_dict.keys():

            for Imputer_cat_ID in self.Imputer_categorical_dict.keys():
                
                for Imputer_iter_class_ID in self.Imputer_categorical_dict[Imputer_cat_ID].keys():
                    
                    for Imputer_cont_ID in self.Imputer_continuous_dict.keys():

                        for Imputer_iter_reg_ID in self.Imputer_continuous_dict[Imputer_cont_ID].keys():
                            
                            for OneHot_case in self.OneHot_cases:
                                    
                                for AbsCorrCoeff_threshold in self.AbsCorrCoeff_thresholds:
                                    
                                    self._fit_transform_feat_eng_case(X,
                                                              path_feat_eng_dir,
                                                              format_,
                                                              Scaler_ID,
                                                              Imputer_cat_ID,
                                                              Imputer_iter_class_ID,
                                                              Imputer_cont_ID,
                                                              Imputer_iter_reg_ID,
                                                              OneHot_case,
                                                              AbsCorrCoeff_threshold)

                                    self.path_feat_eng_dirs.append(self._path_feat_eng_base_dir(path_feat_eng_dir, 
                                                                                              OneHot_case,
                                                                                              Scaler_ID,
                                                                                              Imputer_cat_ID,
                                                                                              Imputer_iter_class_ID,
                                                                                              Imputer_cont_ID,
                                                                                              Imputer_iter_reg_ID,
                                                                                              AbsCorrCoeff_threshold))

                                    _gc.collect()


        print('------------------------------------ !Finished! ------------------------------------')

    def transform(self, X_field):
        """
        Transform an arbitrary dataset of the same format as the X dataset passed in the fit method
        
        Arguments:
        ----------
            X_field: the dataset you wish to transform
        """

        _gc.collect()
        
        for key_header in ['categorical features', 'continuous features']:
            assert(key_header in self.headers_dict.keys()), 'headers_dict is missing the "'+key_header+'" key'
            
        X_field = X_field.copy()
        
        if self.verbose>=2: 
            print('\nX_field.info():')
            X_field.info()
            
        if 'dask' in str(type(X_field)):
            self.n_samples = X_field.iloc[:,0].compute().shape[0]
        else:
            self.n_samples = X_field.shape[0]

        #Save the X and X_field data
        path_feat_eng_dir = self.path_feat_eng_root_dir 
        
        files=['X_field']
        if self._feat_eng_files_saved(files, path_feat_eng_dir, self.format_) == False or self.overwrite==True:
            self.save(X_field, 'X_field', self.format_, path_feat_eng_dir)
                
        #Run the Pipe
        print('---------------------------- feat_eng_pipe transform ---------------------------')
        
        #BertWord2VecPCAer
        X_field, path_feat_eng_dir = self._transform_BertWord2VecPCAer(X_field, 
                                                                        path_feat_eng_dir)
        #Label Encode
        X_field, path_feat_eng_dir = self._transform_LabelEncode(X_field,
                                                                    path_feat_eng_dir)
      
        
        for Scaler_ID in self.Scalers_dict.keys():
            
            for Imputer_cat_ID in self.Imputer_categorical_dict.keys():
                
                for Imputer_iter_class_ID in self.Imputer_categorical_dict[Imputer_cat_ID].keys():
                   
                    for Imputer_cont_ID in self.Imputer_continuous_dict.keys():

                        for Imputer_iter_reg_ID in self.Imputer_continuous_dict[Imputer_cont_ID].keys():
                            
                            for OneHot_case in self.OneHot_cases:
                                
                                for AbsCorrCoeff_threshold in self.AbsCorrCoeff_thresholds:

                                    self._transform_feat_eng_case(X_field,
                                                                      path_feat_eng_dir,
                                                                      Scaler_ID,
                                                                      Imputer_cat_ID,
                                                                      Imputer_iter_class_ID,
                                                                      Imputer_cont_ID,
                                                                      Imputer_iter_reg_ID,
                                                                      OneHot_case,
                                                                      AbsCorrCoeff_threshold)

                                    _gc.collect()


        print('------------------------------------ !Finished! ------------------------------------')


        
        


