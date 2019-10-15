
class CorrCoeffThreshold():
    def __init__(self, 
                 AbsCorrCoeff_threshold = 0.99,
                 iterative_sample_size = None):
        """
        Method for filtering features with correlation coefficients >= the AbsCorrCoeff_threshold (absolute value of corerlation coeff. threshold) value passed, where the correlation coefficient is the pearson coerrelation coefficient
        
        Arguments:
        ----------
            AbsCorrCoeff_threshold: float. default = 0.99. valid range: 0 to 1
            iterative_sample_size: float
        """
        assert(AbsCorrCoeff_threshold>=0)
        assert(AbsCorrCoeff_threshold<=1)
        self.AbsCorrCoeff_threshold = AbsCorrCoeff_threshold
        
    def __fetch_dropped_features_slice_dict__(self,
                                              np_corr_col, 
                                              feature_idx,
                                              AbsCorrCoeff_threshold):
            """
            Arguments:
            ----------
                np_corr_col: column of correlation coefficients for the feature of feature_idx
                feature_idx: the index corresponding to the column slice of the correlation coeff. matrix
                AbsCorrCoeff_threshold: Absolute value threshold limit for the correlation coefficients to filter
            """
            
            import numpy as np
            
            dropped_features_slice_dict = {'dropped feature idx':[],
                                           'correlated feature idx':[],
                                           'corr coeff':[]}
            for i in range(np_corr_col.shape[0]):
                if i!=feature_idx:
                    if np.abs(np_corr_col[i])>= AbsCorrCoeff_threshold:
                        dropped_features_slice_dict['dropped feature idx'].append(i)
                        dropped_features_slice_dict['correlated feature idx'].append(feature_idx)
                        dropped_features_slice_dict['corr coeff'].append(np_corr_col[i])
                        
            return dropped_features_slice_dict
        
    def fit(self, 
            df, 
            CorrCoeff_features = 'auto',
            verbose = 0):
        """
        Fit the CorrelationCoeffThreshold object to the data
        
        Arguments:
        ----------
            df: the dataframe of interest
            CorrCoeff_features: list. the subset of features to analyze the correlation coeff. on. If 'auto' then all columns in the df will be used
        """
        import numpy as np
        import joblib   
        import gc
        import dask
        
        df = df.copy()
        
        type_df = type(df)

        #assigne self.CorrCoeff_features
        if CorrCoeff_features == 'auto':
            self.CorrCoeff_features = list(df.columns)
        else:
            assert(type(CorrCoeff_features)==type(list())), 'CorrCoeff_features must be "auto" or a list'
            self.CorrCoeff_features = CorrCoeff_features
        
            df = df[self.CorrCoeff_features]
            
        if type_df==dask.dataframe.core.DataFrame:
            np_corr = np.array(df.corr())
            
        else:
            np_corr = np.corrcoef(df, rowvar=False)
        
        del df
        gc.collect()
        
        executor = joblib.parallel.Parallel(n_jobs = -1, verbose=verbose, backend='multiprocessing')
        tasks = [joblib.parallel.delayed(self.__fetch_dropped_features_slice_dict__)(np_corr[:,feature_idx],
                                                                            feature_idx,
                   self.AbsCorrCoeff_threshold) for feature_idx in range(np_corr.shape[0])]
        del np_corr
        gc.collect()
        
        #execute the task
        outputs = executor(tasks)
        del tasks
        gc.collect()
        
        #assemble outputs into full dictionary
        self.dropped_features_dict = {'dropped feature':[],
                                      'correlated feature':[],
                                      'corr coeff':[]}
        self.outputs = outputs
        for dropped_feat_slice_dict in outputs:
            for i in range(len(dropped_feat_slice_dict['dropped feature idx'])):
                correlated_feat = self.CorrCoeff_features[dropped_feat_slice_dict['correlated feature idx'][i]]
                dropped_feat = self.CorrCoeff_features[dropped_feat_slice_dict['dropped feature idx'][i]]
                corr_coeff = dropped_feat_slice_dict['corr coeff'][i]
                
                if correlated_feat not in self.dropped_features_dict['correlated feature'] and correlated_feat not in self.dropped_features_dict['dropped feature']:
                    self.dropped_features_dict['dropped feature'].append(dropped_feat)
                    self.dropped_features_dict['correlated feature'].append(correlated_feat)
                    self.dropped_features_dict['corr coeff'].append(corr_coeff)
                        
    def transform(self, df):
        """
        Transform the dataframe based on the previously run fit
        
        Arguments:
        ----------
            df: dataframe which will be transformed
        """
        df = df.copy()
        for feature in self.dropped_features_dict['dropped feature']:
            if feature in df.columns:
                df = df.drop(columns=[feature])
        return df