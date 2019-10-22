import pandas as pd
import numpy as np

# DROP, BINARIZE OR ENCODE


def cleanandencode(val, dummy=False):
    '''
    Author: Aru Raghuvanshi

    This functions takes a dataframe and drops columns from it if it has just one
    unique value (recurring values or constant).
    If a column has two values, it binarizes them
    If a column has as many unique values as the number of rows, it drops them.
    If dummy argument is True, OneHotEncodes the remaining categorical features.

    Arguments: Dataframe, dummy=False
    Returns: Dataframe
    '''

    from sklearn.preprocessing import LabelBinarizer

    lb = LabelBinarizer()
    for i in val.columns:
        count = val[i].nunique()
        if count == 1:
            val.drop(i, axis=1, inplace=True)
        elif count == 2 and val[i].dtype == 'object':
            val[i] = lb.fit_transform(val[i])
        elif count > 2 and val[i].dtype == 'object' and dummy == True:
            val = pd.get_dummies(val, columns=[i], drop_first=True)
        elif count == val.shape[0]:
            val.drop(i, axis=1, inplace=True)
        else:
            None

    return val


# ============================== IMPUTE AND ENCODE ========================== ]


def impute_encode(val, dummy=False):

    '''
    Author: Aru Raghuvanshi

    This function takes a dataframe and imputes all the
    na values with mean if numerical or mode if categorical.

    Drops all columns if nunique = number of rows in dataset.
    Drops all columns if nunique = 1
    Label Binarizes cat features if nunique = 2
    Label Encodes cat features if nunique is between 2 and 5
    One Hot Encodes cat features if nunique > 6


    Arguments: Dataframe
    Returns: Dataframe
    '''

    from sklearn.preprocessing import LabelEncoder
    from sklearn.preprocessing import LabelBinarizer
    le = LabelEncoder()
    lb = LabelBinarizer()

    for i in val.columns:
        if val[i].dtype != 'object':
            val[i] = val[i].fillna(val[i].mean())
        else:
            val[i] = val[i].fillna(val[i].mode()[0])

    for i in val.columns:
        count = val[i].nunique()
        if count == 1:
            val.drop(i, axis=1, inplace=True)
        elif count == val[i].shape[0]:
            val.drop(i, axis=1, inplace=True)
        elif count == 2 and val[i].dtype == 'object':
            val[i] = lb.fit_transform(val[i])
        elif 5 >= count > 2 and val[i].dtype == 'object':
            val[i] = le.fit_transform(val[i])
        elif count >= 6 and val[i].dtype == 'object' and dummy == True:
            val = pd.get_dummies(val, columns=[i], drop_first=True)
        else:
            None

    return val


# ==============### FEATURE SELECTOR ================================================ ]


# __1.4.3__

def featureselector(val, var, coef):

    '''
    Author: Aru Raghuvanshi

    This function takes three parameters of master dataframe,
    target variable and correlation coefficient from that dataframe.
    It returns a new dataframe with all those variables dropped
    whose correlation is lower than coefficient supplied with
    the independent or target variable 'var'. The variable 'var'
    should be converted to numerical category before supply.

    Arguments: DataFrame, variable of comparison, absolute value of coef.
    Example: df1 = featureselector(df, 'OutCome', 0.11)
    Returns: DataFrame
    '''

    corr_status = val[val.columns[0:]].corr()[var]
    to_use = corr_status.to_dict()
    to_drop = {}
    for k, v in list(to_use.items()):
        if abs(v) < float(coef):
            to_drop[k] = v
    val = val.drop(list(to_drop), axis=1)

    return val


# ============== QUALITY REPORT ================================================ ]

# __1.7.4__

def qualityreport(val):
    '''

    Author: Aru Raghuvanshi

    This function displays various attributes of a dataframe
    imported from an external file like csv, excel etc. and
    doesn't return a dataframe but only displays.

    Arguments: Dataframe
    Returns: Dataframe

    '''
    dtypes = val.dtypes
    rows = val.T.apply(lambda x: x.count(), axis=1)
    nuniq = val.T.apply(lambda x: x.nunique(), axis=1)
    uniq = val.T.apply(lambda x: x.unique() if x.dtype == 'object' else None, axis=1)
    total = val.T.apply(lambda x: x.isna().sum(), axis=1)
    count = val.shape[0]
    pc = np.round(total / count * 100, 2)

    mini = val.min()
    maxi = val.max()

    mean = val.mean()

    qualitydf = pd.concat([dtypes, rows, total, pc, mean, mini, maxi, nuniq, uniq],
                          keys=['Dtype', 'Available Rows', 'Missing Values', 'Percent Missing', 'Mean',
                                'Min', 'Max', 'No. Of Uniques', 'Unique Values'], sort=True, axis=1)

    a = b = c = d = e = f = 0

    a = len(qualitydf[qualitydf.Dtype == 'object'])
    b = len(qualitydf[qualitydf.Dtype == 'int64'])
    c = len(qualitydf[qualitydf.Dtype == 'float64'])
    d = len(qualitydf[qualitydf.Dtype == 'uint8'])
    e = len(qualitydf[qualitydf.Dtype == 'int32'])
    f = len(qualitydf[qualitydf.Dtype == 'float32'])

    catfeat = a
    numfeat = b + c + d + e + f
    integrity = 100 - (sum(pc) / val.shape[1])

    print(f'Categorical Features: {catfeat} | Numerical Features: {numfeat}\
 | Dataset Shape: {val.shape} | DataSet Integrity: {np.round(integrity, 1)} %')

    return qualitydf


# ======================== INTEGRITY REPORT ========================== ]

# __1.7.4.1__


def integrity_report(val):
    '''

    Author: Aru Raghuvanshi

    This function displays various attributes of a dataset
    imported from an external file like csv, excel etc.

    Arguments: Dataframe
    Returns: Dataframe, plots

    '''

    import numpy as np
    import matplotlib.pyplot as plt
    import warnings
    from warnings import filterwarnings
    warnings.filterwarnings('ignore')

    dtypes = val.dtypes
    rows = val.T.apply(lambda x: x.count(), axis=1)
    nuniq = val.T.apply(lambda x: x.nunique(), axis=1)

    total = val.T.apply(lambda x: x.isna().sum(), axis=1)
    count = val.shape[0]
    pc = np.round(total / count * 100, 2)

    qualitydf = pd.concat([dtypes, rows, total, pc, nuniq],
                          keys=['Dtype', 'Available Rows', 'Missing Values', 'Percent Missing',
                                'No. Of Uniques'], axis=1)

    a = b = c = d = e = f = 0

    a = len(qualitydf[qualitydf.Dtype == 'object'])
    b = len(qualitydf[qualitydf.Dtype == 'int64'])
    c = len(qualitydf[qualitydf.Dtype == 'float64'])
    d = len(qualitydf[qualitydf.Dtype == 'uint8'])
    e = len(qualitydf[qualitydf.Dtype == 'int32'])
    f = len(qualitydf[qualitydf.Dtype == 'float32'])
    g = len(qualitydf[qualitydf.Dtype == 'datetime64[ns]'])
    catfeat = a
    numfeat = b + c + d + e + f
    datefeat = g
    integrity = 100 - (sum(pc)/val.shape[1])

    print(f'Categorical Features: {catfeat} | Numerical Features: {numfeat} | DateTime Features: {datefeat}\
            \nDataset Shape: {val.shape} | DataSet Integrity: {np.round(integrity, 1)} %')

    availablerows = val.shape[0] * len(val.columns)
    missing = (val.shape[0] * len(val.columns)) - sum(rows)

    types = pd.DataFrame(
        {'INTEGER': [b+e+d], 'FLOAT': [c], 'OBJECT': [a], 'DATETIME': [g]})
    catnum = pd.DataFrame({'CATEGORICAL': [catfeat], 'NUMERICAL': [
                          numfeat], 'DATETIME': [datefeat]})
    missdata = pd.DataFrame({'USEABLE': [availablerows], 'MISSING': [missing]})

    labels1 = types.columns
    labels2 = missdata.columns
    labels3 = catnum.columns

    fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(16, 4))

    ax1.pie(types, labels=labels1, explode=None, radius=1.0, autopct='%1.1f%%',
            colors=['lime', 'mediumseagreen', 'mediumspringgreen', 'seagreen'],
            startangle=310)
    ax2.pie(missdata, labels=labels2, explode=None, radius=1.0, autopct='%1.1f%%', colors=['pink', 'lightcoral'],
            startangle=310)

    ax3.pie(catnum, labels=labels3, explode=None, radius=1.0, autopct='%1.1f%%',
            startangle=310, colors=['lightskyblue', 'steelblue', 'deepskyblue'])

    plt.subplots_adjust(wspace=0)
    plt.show()

    return qualitydf