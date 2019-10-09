
    
class categorical_features():
    
    def __init__(self, return_format = 'DataFrame', LabelEncoder = None):
            
        """
        OneHot encode each categorical feature. This function assumes an impute transformation (fill na) has been performed prior to encoding such that the encoder does not need to be able to transform datasets containng NaN values

        Arugments:
        ----------
           return_format: string, default = 'DataFrame'
                - if 'DataFrame': the transformed data will be returned as a pandas or dask dataframe. 
                - if 'npArray': the transformed data will be returned as a numpy array.
           LabelEncoder: The LabelEncoder object used previously in the feature engineering operations. If this is passed, the headers for the encoded dataframe will be updated using the LabelEncoder.LabelEncoder_dict.keys() value.
        """
        
        import numpy as np
        import pandas as pd
        import sklearn, sklearn.preprocessing
        import warnings

        self.return_format = return_format
        self.LabelEncoder = LabelEncoder
        
    def fit(self, X, categorical_headers):
        """
        Fit the encoder to the categorical_headers in X dataframe passed. 
        Arugments:
        ----------
            X: dask or pandas dataframe of interest
            categorical_headers: list of categorical feature columns/headers in the X dataframe
        
        """
        import numpy as np
        import pandas as pd
        import warnings
        import dask
        
        warnings.filterwarnings('ignore')
    
        X = X.copy()
        
        type_X = type(X)
        
        self.categorical_headers = categorical_headers

          
        if type_X==dask.dataframe.core.DataFrame:
            X_cat = X[categorical_headers].compute()
        else:
            X_cat = X[categorical_headers]

        # fetch categories
        categories = []
        for header in categorical_headers:
            X_cat[header] = X_cat[header].astype(int)
            categories.append([idx for idx in range(X_cat[header].unique().min(), X_cat[header].unique().max()+1)])

        import sklearn, sklearn.preprocessing
        self.Encoder = sklearn.preprocessing.OneHotEncoder(categories = categories)

        #run fit
        self.Encoder.fit(X_cat)

        #add fit value counts to use if transforming unseen dataset with values not found in original data
        self.fit_value_counts = []
        for header in categorical_headers:
            counts = X_cat[header].value_counts().reset_index()
            counts.columns = ['value', 'count']
            self.fit_value_counts.append(counts)

         
        #compile OneHot_headers
        self.OneHot_headers = []
        for i in range(len(self.categorical_headers)):
            header = self.categorical_headers[i]
            for val in self.Encoder.categories_[i]:

                #if a LabelEncoder is passed, inverse transform the encoded value for labeling the header
                if self.LabelEncoder!= None:
                    if header in self.LabelEncoder.LabelEncoder_dict.keys():
                        try:
                            val = self.LabelEncoder.LabelEncoder_dict[header].inverse_transform([val])[0]
                        except:
                            pass
                
                #compile one heade encoded headers, ensuring illegal characters do not appear in the header.
                self.OneHot_headers.append(header+'('+str(val)+')'.replace('<','less'))
                
        warnings.filterwarnings('default')
        
        
    def transform(self, X):
        """
        transform the X dataframe passed
        """
        import numpy as np
        import pandas as pd
        import sklearn, sklearn.preprocessing
        import warnings
        import dask
        
        warnings.filterwarnings('ignore')

        X = X.copy()
        
        type_X = type(X)
        if type_X==dask.dataframe.core.DataFrame:
            npartitions = X.npartitions
            X = X.compute()
            
        c =0
        for header in self.categorical_headers:
            #ensure integer data type
            X[header] = X[header].astype(int)

            #if a value in the X does not exist in the encoder, update it with most frequent value from the fit_value_counts
            for unique in X[header].unique():
                if unique not in self.Encoder.categories_[c]:
                    value = int(self.fit_value_counts[c]['value'][self.fit_value_counts[c]['count'] == np.max(self.fit_value_counts[c]['count'])])
                    X[header][X[header]==unique] = value
            c+=1

        OneHotEncodings = self.Encoder.transform(X[self.categorical_headers])

        X = X.drop(columns = self.categorical_headers).reset_index(drop=True)
        
        if self.return_format == 'DataFrame':
            OneHotEncodings = pd.DataFrame(OneHotEncodings.toarray(),
                                columns = self.OneHot_headers )
            X = pd.concat((X, OneHotEncodings),axis=1)
            
            self.headers_after_OneHot = list(X.columns)
            
            if type_X==dask.dataframe.core.DataFrame:
                X = dask.dataframe.from_pandas(X, npartitions=npartitions)
            
        if self.return_format == 'npArray':
            
            self.headers_after_OneHot = list(X.columns) + self.OneHot_headers
            
            X = np.concatenate((np.array(X), OneHotEncodings.toarray()), axis = 1)

        warnings.filterwarnings('default')

        return X
