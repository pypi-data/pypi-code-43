
import pydicom as _pydicom
import sklearn.preprocessing as _sklearn_preprocessing
import warnings as _warnings

class continuous_features():
    
    def __init__(self, Scaler = _sklearn_preprocessing.MinMaxScaler()):
        
        """
        Instantiate a Scaler object to scale continuous_features specified in fit method

        Arguments:
        ---------
            Scaler: _sklearn_preprocessing....: defaults: _sklearn_preprocessing.MinMaxScaler()
                - Object specifing the scaler operation the dcm will be fit and transformed to.
        """
        
        self.Scaler = Scaler

    def fit(self, X, continuous_headers = 'auto'):
        """
        Fit the Scaler to the continous features contained in the dataframe passed
        
        Arguments:
        ----------
            X: the dataframe of interest (dask or pandas)
            continuous_headers: the header names for the continuous features of interest.
                - If 'auto', all columns will be assumed to be continuous features.
        
        Returns:
        --------
            None. The Scaler object will be ready to run the transform operation.
        """
        
        X = X.copy()
        
        if type(continuous_headers) == type(list()):
            self.continuous_headers = continuous_headers
        else:
            self.continuous_headers = list(X.columns)
            
        self.Scaler.fit(X[self.continuous_headers])
        
    def transform(self, X):
        
        
        _warnings.filterwarnings('ignore')
    
        
        type_X = str(type(X))
        if 'dask' in type_X:
            npartitions = X.npartitions
            X = X.compute()

        X[self.continuous_headers] = self.Scaler.transform(X[self.continuous_headers])
        
        if 'dask' in type_X:
            import dask, dask.dataframe
            X = dask.dataframe.from_pandas(X, npartitions=npartitions)
            
        _warnings.filterwarnings('default')

        return X

def default_Scalers_dict():
    """
    fetch dictionary containing typical scalers used for transforming continuous data
    
    Returns:
    -------
        Scalers_dict: dictionary containing typical scalers used for transforming continuous data
    """
    
    Scalers_dict = {'MinMaxScaler':_sklearn_preprocessing.MinMaxScaler(),
                    'StandardScaler':_sklearn_preprocessing.StandardScaler(),
                    'RobustScaler':_sklearn_preprocessing.RobustScaler()}
    return Scalers_dict

class Hounsfield():
    """
    computerized tomography (CT) scans values need to be in Hounsfied units (radiodensity) to be properly analyzed.
    This scaler transforms the input .dcm data into an image with HU scale.
    
    Reference:
    ----------
        https://www.kaggle.com/omission/eda-view-dicom-images-with-correct-windowing
    """
    def __init__(self):
        pass
    
    def _fetch_first_int_of_dicom_field(self, x):
        """
        get x[0] as in int if x is a 'pydicom.multival.MultiValue', otherwise get int(x)
        """
        if type(x) == _pydicom.multival.MultiValue:
            return int(x[0])
        else:
            return int(x)

    def _fetch_window(self, dcm):
        """
        fetch the window dimensions from the dcm data
        
        Arguments:
        ----------
            dcm: dcm data from .dcm file
        
        Returns:
        --------
            window_center, window_width, intercept, slope
        """
        dicom_fields = [dcm[('0028','1050')].value, #window center
                        dcm[('0028','1051')].value, #window width
                        dcm[('0028','1052')].value, #intercept
                        dcm[('0028','1053')].value] #slope
        return [self._fetch_first_int_of_dicom_field(x) for x in dicom_fields]
    
    def fit(self, dcm):
        """
        Extract the window dimensions from the dcm data and add them to the Hounsfield Scaler object
        """
        self.window_center, self.window_width, self.intercept, self.slope = self._fetch_window(dcm)
    
    def transform(self, dcm):
        """
        Transform the image data contained in the dcm file to Hounsfield Units (HUs) based on the fitted window data.
        
        Arguments:
        ----------
            dcm: data from .dcm file
        
        Returns:
        --------
            img: image data from .dcm file scaled to hounsfield units.
        """
        
        img = dcm.pixel_array
        
        img = (img*self.slope+self.intercept)
        img_min = self.window_center - self.window_width//2
        img_max = self.window_center + self.window_width//2
        img[img<img_min] = img_min
        img[img>img_max] = img_max
        
        return img
    
    def fit_transform(self, dcm):
        """
        fit and transform that passed dcm data to return the image of interest in Hounsfield Units (HUs)
        
        Arguments:
        ----------
            dcm: data from .dcm file
        
        Returns:
        --------
            img: image data from .dcm file scaled to hounsfield units.
        """
        self.fit(dcm)
        img = self.transform(dcm)
        return img
        