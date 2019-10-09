import os as __os__
try:
    import tensorflow as __tf__
    __callbacks__ = [__tf__.keras.callbacks.EarlyStopping(monitor='val_loss', patience =10)]
except:
    __callbacks__ = [None]

class GridSearchCV:
    """
    GridSearchCV on keras-based neural nets
    
    Arguments:
    ---------
        
    
    """
    
    def __init__(self, 
                 model, 
                 param_grid, 
                 callbacks = __callbacks__,
                 scoring = {'metric': 'loss', 'maximize':False},
                 batch_size = 32,
                 epochs = 100,
                 cv='warn', 
                 path_report_folder = __os__.path.abspath('.'),
                 verbose=1):
        
        import sys, os
        from . import utils
        from ... import file_utils
        
        self.param_grid = param_grid
        self.model = model
        self.cv = cv
        self.verbose = verbose
        self.param_grid = param_grid
        self.callbacks = callbacks
        self.batch_size = batch_size
        self.epochs = epochs
        self.scoring = scoring
        
        #import load and saving functions from JL_file_utils
        
        self.load = file_utils.load
        self.save = file_utils.save
        self.load_model = utils.load_model
        self.save_model = utils.save_model
        
        #check assertions
        assert(type(self.scoring)==dict), 'scoring must be a dictionary with a "metric" and "maximize" key'
        
        #append to cv_Scores list
        if self.scoring['metric'] == None: #use validation loss as the score if history 
            self.scoring['metric'] = 'loss'
            
        if self.scoring['metric'] != 'loss':   
            #update param_grid if scoring metrics not already in param grid
            if scoring['metric'] not in self.param_grid['metrics'][0]:
                self.param_grid['metrics'][0].append(scoring['metric'])
        
        #ensure the report folder has consistant nomenclature at its root
        root_name = 'GridSearchCV'
        if root_name not in path_report_folder:
            path_report_folder = os.path.join(path_report_folder,root_name)
        self.path_report_folder = path_report_folder
        
        #build report folder
        if os.path.isdir(self.path_report_folder)==False:
            os.makedirs(self.path_report_folder)
        
        #save the settings to the report folder
        self.save(self.model, 'model', 'dill', self.path_report_folder)
        
        batch_size_epochs_cv_params = {'batch_size':self.batch_size,
                                      'epochs':self.epochs,
                                      'cv':self.cv}
        
        self.save(batch_size_epochs_cv_params, 'batch_size_epochs_cv_params', 'dill', self.path_report_folder)
        
    
    def __run_single_cv_fit__(self,
                              X_train, y_train,
                               X_test, y_test,
                               train_idx, val_idx,
                               model,
                               batch_size, 
                               epochs,
                               callbacks,
                               scoring,
                               verbose=0):

        X_train_val, X_val = X_train[train_idx], X_train[val_idx]
        y_train_val, y_val = y_train[train_idx], y_train[val_idx]

        #fit the model
        history = model.fit(x=X_train_val, 
                            y=y_train_val, 
                            validation_data=(X_val, y_val),
                            batch_size=batch_size, 
                            epochs = epochs, 
                            verbose= verbose, 
                            callbacks = callbacks)
        metrics_dict = {}
        for key in history.history.keys():
            if key!='lr':
                metrics_dict[key] = history.history[key][-1]

        Score = metrics_dict['val_'+scoring['metric']]

        return Score
    
    def Kfold(self, X, y, n_splits = 5, stratified = False ):
        """
        Build train - validation index generator for K fold splits
        """
        import sklearn.model_selection
        import numpy as np
        
        if len(y.shape)>1:
            if y.shape[1]>1: #if y is one hot encoded
                y_flat = np.zeros((y.shape[0],1))

                encoding_idx = 0
                for c in range(y.shape[1]):
                    y_flat[y[:,c]==1] = encoding_idx
                    encoding_idx+=1
        else: y_flat = y
        
        if stratified:
            kf = sklearn.model_selection.StratifiedKFold(n_splits = n_splits, shuffle=True)
        else:
            kf = sklearn.model_selection.KFold(n_splits=n_splits, shuffle=True)
        
        kf_Xy_split_idx_gen = kf.split(X)
        
        return kf_Xy_split_idx_gen 
    
    def ParameterGrid(self, param_grid):
        import sklearn.model_selection
        return list(sklearn.model_selection.ParameterGrid(param_grid))
    
    def fit(self, X_train, y_train, X_test, y_test):
        
        import numpy as np
        import warnings
        import time
        import sys, os
        
        warnings.filterwarnings('ignore')
        
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        X_test = np.array(X_test)
        y_test = np.array(y_test)
        
        #build parameter grid list
        self.ParameterGrid_dict = {}
        self.ParameterGrid_dict['params'] = self.ParameterGrid(self.param_grid)
        
        if self.verbose >=1:
            print('running', self.cv, 'fold cross validation on',len(self.ParameterGrid_dict['params']),'candidates, totalling',self.cv*len(self.ParameterGrid_dict['params']),'fits')
            print('Scoring using',self.scoring)
        
        cv_verbosity = self.verbose
        if cv_verbosity==1: cv_verbosity = 0
            
        self.ParameterGrid_dict[self.scoring['metric']] = np.zeros((len(self.ParameterGrid_dict['params'])))
        
        #save to report folder
        self.save(self.ParameterGrid_dict, 'ParameterGrid_dict', 'dill', self.path_report_folder)
        
        #run grid search
        p=0
        time_cv_list = []
        for params in self.ParameterGrid_dict['params']:
            if self.verbose >=1:
                param_sweep_print = '\tParameter sweep progress: '+\
                      str(round((p+1)/len(self.ParameterGrid_dict['params'])*100,3))+\
                      '(total time (mins):'+\
                      str(round(np.sum(time_cv_list),2))+' of ~'+\
                      str(round(np.median(time_cv_list)*len(self.ParameterGrid_dict['params']),2))+')'
            
            #build the model
            model_ = self.model(**params)
            if self.verbose >=4:
                model_.summary()
            
            if self.verbose>=3:
                print('\tn_params:',model_.count_params())
                
            #get cv split generator
            kf_Xy_split_idx_gen  = self.Kfold(X_train, y_train, self.cv)

            cv_Scores = []
            time_cv = time.time() #total cv training time
            c=0
            for train_idx, val_idx in kf_Xy_split_idx_gen:
                
                time_train = time.time()
                Score = self.__run_single_cv_fit__(X_train, y_train,
                                                  X_test, y_test,
                                                  train_idx, val_idx,
                                                  model_,
                                                  self.batch_size, 
                                                  self.epochs,
                                                  self.callbacks,
                                                  self.scoring,
                                                  verbose=cv_verbosity)
                if self.verbose>=3:
                    print('\t\tScore:',Score) 
                cv_Scores.append(Score)
                time_train = (time.time() - time_train)/60
                
                if self.verbose>=1:
                    print(param_sweep_print,'[cv Progress:',round((c+1)/self.cv*100,3),
                          '(train time (mins):',round(time_train,2),')]',end='\r')
                c+=1
                
            
            time_cv = (time.time() - time_cv)/60
            time_cv_list.append(time_cv)
            
            #eval avg. score for all cvs
            Score = np.mean(cv_Scores)
            if self.verbose>=2:
                print('\tcv Score:',Score,' (cv time (mins):',round(time_cv,2),')\t\t\t')
            self.ParameterGrid_dict[self.scoring['metric']][p] = Score
            
            #save to report folder
            self.save(self.ParameterGrid_dict, 'ParameterGrid_dict', 'dill', self.path_report_folder)
                                               
            p+=1
        
        #determine best score
        if self.scoring['maximize']:
            self.best_score_ = np.max(self.ParameterGrid_dict[self.scoring['metric']])
        else:
            self.best_score_ = np.min(self.ParameterGrid_dict[self.scoring['metric']])
            
        #find idx of best score
        best_idx = np.where(np.array(self.ParameterGrid_dict[self.scoring['metric']]) == self.best_score_)[0][0]
        
        #fetch best parameters
        self.best_params_ = self.ParameterGrid_dict['params'][best_idx]
        self.save(self.best_params_, 'best_params_', 'dill', self.path_report_folder)
        
        if self.verbose >=1:
            print('best_score_:',self.best_score_,'         ')
            print('best_params_:')
            display(self.best_params_)
        
        #fetch best model
        if self.verbose >=1:
            print('re-fitting best estimator...')
        self.best_estimator_ = self.model(**self.best_params_)
        self.best_estimator_.fit(x=X_train, y=y_train,
                                   validation_data=(X_test, y_test),
                                   batch_size=self.batch_size, 
                                   epochs = self.epochs, 
                                   verbose= cv_verbosity, 
                                   callbacks = self.callbacks)
        
        try:
            self.best_estimator_.save(os.path.join(self.path_report_folder, 'best_estimator_.h5')) 
        except Exception as e:
            print('Exception at save:',e)
        
        if self.verbose >=1:
            print('...Finished')
            
        warnings.filterwarnings('default')
        
        
            