class categorical_features():
    
    """
    LabelEncode non-numeric categorical features. Unlike in sklearns default encoder, this class ensures missing values can be handled when transforming an arbitrary dataset.
    """
    def __init__(self, verbose = 0):
        """
        Arguments:
        ---------
            verbose: int. Default: 0. higher implies more prints
        """

        self.verbose = verbose
        
    def _LabelEncode_uniques_list(self,
                               uniques_list):
            import pandas as pd
            import sklearn.preprocessing
            
            # ensure 'missing_value' is encoded so that the LabelEncoders can encode test sets
            uniques = uniques_list+['missing_value']
            uniques.sort()
            
            #fit the encoder
            LabelEncoder = sklearn.preprocessing.LabelEncoder()
            LabelEncoder.fit(uniques)
            
            return LabelEncoder
        
    def fit(self,
            X, categorical_headers ):
        """
        Fit the LabelEncoder to the categorical_features
        
        Arguments:
        ----------
            X: pandas X with the features of interest
            categorical_headers: list of headers within the dataframe which are categorical
                - Only non-numeric categorical columns will be encoded, even if the categorical headers contains some numeric columns.
        """
        import pandas as pd
        import numpy as np
        import joblib

        X = X.copy()
        
        #fetch the non-numeric categorical headers which will be encoded
        LabelEncode_headers = [header for header in categorical_headers if pd.api.types.is_numeric_dtype(X[header])==False and header in categorical_headers]
        if self.verbose>=1: 
            print("LabelEncode_headers:\n", LabelEncode_headers)

        #build label encoder
        self.LabelEncoder_dict = {}
        
        #build uniques dictionary (This loop is necessary of compatability with dask, where X[header].unique() cannot be pickled)
        uniques_dict = {}
        for header in LabelEncode_headers:
            uniques_dict[header] = list(X[header].fillna('missing_value').unique())
        
         # run parallel computing job for label encoding 
        executor = joblib.parallel.Parallel(n_jobs = -1, verbose=self.verbose, backend='multiprocessing')
        tasks = [joblib.parallel.delayed(self._LabelEncode_uniques_list)(uniques_dict[header]) for header in LabelEncode_headers]

        #execute the task
        outputs = executor(tasks)
        
        for i in range(len(LabelEncode_headers)):
            self.LabelEncoder_dict[LabelEncode_headers[i]] = outputs[i]
            
    
    def transform(self, X):
        """
        Transform the X dataset passed. If the dataset contains a value which the encoder has not previously seen, it will assume that value is a NaN/missing_value.
        """
        import numpy as np
        import warnings
        import dask
        
        X = X.copy()
        
        type_X = type(X)
        if type_X==dask.dataframe.core.DataFrame:
            npartitions = X.npartitions
            X = X.compute()
        
        for header in self.LabelEncoder_dict.keys():
            warnings.filterwarnings('ignore')
            
            #fill na as "missing_value"
            X[header] = X[header].fillna('missing_value')
            
            #check if all unique values are contained in the encodings
            #if not assume they are 'missing_value'
            for unique in X[header].unique():
                if unique not in list(self.LabelEncoder_dict[header].classes_):
                    X[header][X[header]==unique] = 'missing_value'

            X[header] =list(self.LabelEncoder_dict[header].transform(X[header]))
            
            #fill back in nan values
            nan_encoding = self.LabelEncoder_dict[header].transform(['missing_value'])[0]
            X[header][X[header]==nan_encoding] = np.nan
            
        if type_X==dask.dataframe.core.DataFrame:
            X = dask.dataframe.from_pandas(X, npartitions=npartitions)
            
        warnings.filterwarnings('default')

        return X