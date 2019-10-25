"""
from KUtils.eda import data_preparation as dp
"""

import numpy as np
import pandas as pd

import re

from KUtils.eda import chartil

def plotUnique(df, optional_settings={}):
    unique_dict = {x: len(df[x].unique()) for x in df.columns}
    optional_settings.update({'x_label':'Features'}) 
    optional_settings.update({'y_label':'Unique values'})
    optional_settings.update({'chart_title':'Unique values in each Feature/Column'})

    if optional_settings.get('sort_by_value')==None:
        optional_settings.update({'sort_by_value':False})
        
    chartil.core_barchart_from_series(pd.Series(unique_dict), optional_settings) 
    
def plotNullInColumns(df, optional_settings={}):
    aSeries = df.isnull().sum() 
    if sum(aSeries)>0:
        optional_settings.update({'exclude_zero_column':True})
        optional_settings.update({'x_label':'Features'}) 
        optional_settings.update({'y_label':'Missing Count'})
        optional_settings.update({'chart_title':'Count of missing values in each Feature/Column'})
        chartil.core_barchart_from_series(aSeries, optional_settings)
    else:
        print('Nothing to plot. All series value are 0')

def plotNullInRows(df, optional_settings={}):
    no_of_columns = df.shape[1]
    colNulls = df.isnull().sum(axis=1)
    if sum(colNulls)>0:
        colNulls = colNulls*100/no_of_columns
        df['nan_percentage']=colNulls
        
        # Todo: Try Range instead of hrdcoded value (Take care when Percentage is 0)
        df['nan_percentage_bin'] = pd.cut(df['nan_percentage'], 
                  [-1, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100], 
                  labels=['<0', '<=5%', '<=10%', '<=15', '<=20', '<=25', '<=30',
                          '<=35','<=40','<=45', '<=50', '<=55', '<=60', '<=65', '<=70', '<=75', '<=80','<=85', '<=90', '<=95', '<=100'])
        
        data_for_chart = df['nan_percentage_bin'].value_counts(dropna=False)  
        data_for_chart = data_for_chart.loc[data_for_chart.index!='<0'] # Remove zero percentage
        
        df.drop(['nan_percentage', 'nan_percentage_bin'], axis=1, inplace=True) # No more required
        
        if len(data_for_chart)==0:
            print('No nulls found')
        else:
            optional_settings.update({'x_label':'Percenatge Bin'}) 
            optional_settings.update({'y_label':'Number of records'})
            optional_settings.update({'chart_title':'Percenatge of missing values in each Row'})
            optional_settings.update({'sort_by_value':False})
            chartil.core_barchart_from_series(data_for_chart, optional_settings)
    else :
        print('Nothing to plot. All series value are 0')
       
def cap_outliers_using_iqr(df, column_to_treat, lower_quantile=0.25, upper_quantile=0.75, iqr_range=1.5):
    q1 = df[column_to_treat].quantile(lower_quantile)
    q3 = df[column_to_treat].quantile(upper_quantile)
    iqr = q3 - q1
    lower_value = q1 - iqr_range*iqr
    upper_value = q3 + iqr_range*iqr
    df.loc[df[column_to_treat]<lower_value, column_to_treat] = lower_value
    df.loc[df[column_to_treat]>upper_value, column_to_treat] = upper_value
    print('Done')
    
def drop_outliers_using_iqr(df, column_to_treat, lower_quantile=0.25, upper_quantile=0.75, iqr_range=1.5):
    q1 = df[column_to_treat].quantile(lower_quantile)
    q3 = df[column_to_treat].quantile(upper_quantile)
    iqr = q3 - q1
    lower_value = q1 - iqr_range*iqr
    upper_value = q3 + iqr_range*iqr
    
    df.drop(df.index[df[column_to_treat]<lower_value], inplace = True)
    df.drop(df.index[df[column_to_treat]>upper_value], inplace = True)
    
    print('Done')

def cap_outliers_using_zscore(df, column_to_treat, z_score_cap=3): # z_score_cap=Z-score is the number of standard deviations from the mean a data point is 
	 
    data_mean = np.mean(df[column_to_treat])
    data_stddev = np.std(df[column_to_treat])
    
    lower_value = data_mean - z_score_cap*data_stddev
    upper_value = data_mean + z_score_cap*data_stddev
    
    df.loc[df[column_to_treat]<lower_value, column_to_treat] = lower_value
    df.loc[df[column_to_treat]>upper_value, column_to_treat] = upper_value
    print('Done')

def drop_outliers_using_zscore(df, column_to_treat, z_score_cap=3): # z_score_cap=Z-score is the number of standard deviations from the mean a data point is 
	
    data_mean = np.mean(df[column_to_treat])
    data_stddev = np.std(df[column_to_treat])
    
    lower_value = data_mean - z_score_cap*data_stddev
    upper_value = data_mean + z_score_cap*data_stddev
    
    df.drop(df.index[df[column_to_treat]<lower_value], inplace = True)
    df.drop(df.index[df[column_to_treat]>upper_value], inplace = True)
    
    print('Done')
    
def cap_outliers_using_percentile(df, column_to_treat, lower_percent=2, upper_percent=98):
    upper_limit = np.percentile(df[column_to_treat], upper_percent) 
    lower_limit = np.percentile(df[column_to_treat], lower_percent) # Filter the outliers from the dataframe    
    df.loc[df[column_to_treat]<lower_limit, column_to_treat] = lower_limit
    df.loc[df[column_to_treat]>upper_limit, column_to_treat] = upper_limit
    print('Done')
    
def drop_outliers_using_percentile(df, column_to_treat, lower_percent=2, upper_percent=98):
    upper_limit = np.percentile(df[column_to_treat], upper_percent) 
    lower_limit = np.percentile(df[column_to_treat], lower_percent) # Filter the outliers from the dataframe    
    
    df.drop(df.index[df[column_to_treat]<lower_limit], inplace = True)
    df.drop(df.index[df[column_to_treat]>upper_limit], inplace = True)
    print('Done')
	
def fill_category_column_na_with_new(df, column_name, na_column_name='Unknown'): 
    df[column_name].fillna(na_column_name, inplace=True)
    print('Done')
    
def fill_column_na_with_mode(df, column_name): # Can be applied to both categorical and numerical features
    df[column_name].fillna(df[column_name].mode()[0], inplace=True)
    print('Done')
    
def fill_column_na_with_mean(df, column_name): 
    df[column_name].fillna(df[column_name].mean(), inplace=True)
    print('Done')
    
def drop_rows_with_na_in_column(df, column_name):
    df.dropna(subset=[column_name], how='all', inplace = True)
    print('Done')
    
def drop_rows_with_na_percentage_in_row(df, percent_value):
    colNulls = (df.isnull().sum(axis=1))*100/(df.shape[1])
    df['nan_percentage']=colNulls    
    df.drop(df.index[df['nan_percentage'] >= percent_value], inplace = True)    
    df.drop(['nan_percentage'], axis=1, inplace=True) # nan_percentage No more required
    print('Done')

# Log-transformation of the continuous variable which is right skewed
def transform_continuous_by_log1p(df, column_to_treat):
    df[column_to_treat] = np.log1p(df[column_to_treat])
    
# Refer http://onlinestatbook.com/2/transformations/box-cox.html
# https://docs.scipy.org/doc/scipy-0.19.0/reference/generated/scipy.special.boxcox1p.html
def transform_continuous_by_boxcox(df, columns_to_treat=[], lambda_value=0.15, skewness_threshold=0.75): # For highly skewed features
    from scipy.special import boxcox1p
    from KUtils.stat import statil
    if len(columns_to_treat)==0: # Find columns yourself
        skewed_feet_df = statil.analyse_skew(df)
        skewed_feet_df = skewed_feet_df.loc[abs(skewed_feet_df['Skew']) > 0.75]
        skewness_to_treat = list(skewed_feet_df.index)
        for a_col in skewness_to_treat:
            print('Transforming {0} using boxcox1p'.format(a_col))
            df[a_col] = boxcox1p(df[a_col], lambda_value)
    else:
        for a_col in columns_to_treat:
            df[a_col] = boxcox1p(df[a_col], lambda_value)
    # No need to return the data. Inplace transformation done.
    
def fix_invalid_column_names(df): # For Kalgo columns with -.$ wil throw exception, so replace all such chars in column nmae with underscore
    invalid_column_names = [x for x in list(df.columns.values) if not x.isidentifier() ]                              
    for a_colname in invalid_column_names:
        new_colname = re.sub("[-@$.:;*~ +=# ]", "_", a_colname)
        df.rename(columns={a_colname:new_colname},inplace=True)
        print('  ' + a_colname+' Replaced with ' + new_colname)

# This will create a new column boolean type _hasdata and replace original column nan with lowest-1(continuous) or with _unknown(categorical)
def mass_na_fill_with_substitute_column(df, columns_to_treat=[]):    
    if len(columns_to_treat)==0: # Apply to all columns which has 1+ missing values
        aSeries = df.isnull().sum() 
        aSeries = aSeries[aSeries!=0]
        columns_to_treat = list(aSeries.index)

    for a_column_to_treat in columns_to_treat:
        if df[a_column_to_treat].isnull().sum()>0:
            print('Treating ' + a_column_to_treat)
            #new_substitute_column=a_column_to_treat+'_has_data'
            #df[new_substitute_column] = ~pd.isnull(df[a_column_to_treat])
            if df[a_column_to_treat].dtype.kind=='O': # Categorical
                df[a_column_to_treat].fillna('_Unknown', inplace=True)
            else: # numerical
                #print(min(df[a_column_to_treat]))
                col_mean = np.mean(df[a_column_to_treat])
                col_sd = np.std(df[a_column_to_treat])
                print('Replace with (mean-3stddev)' + str(col_mean-3*col_sd))
                df[a_column_to_treat].fillna((col_mean-3*col_sd), inplace=True)
            
            #df[new_substitute_column] = df[new_substitute_column].map({True:1, False:0})
            
    return df

def drop_features_by_ks_2samp(train_df, test_df, p_cutoff=0.05):
    from KUtils.stat import statil
    
    columns_to_drop, ks_dict = statil.ks_2samp(train_df, test_df, p_cutoff)
    
    train_df = train_df.drop(columns_to_drop, axis=1)
    test_df = test_df.drop(columns_to_drop, axis=1)
    return train_df, test_df

def reduce_memory_usage(df):
    """ Go through all the columns of the dataframe and modify the data type to use less memory. 
        (Specifically numeric data type)
    """
    start_mem = df.memory_usage().sum() / 1024**2
    print('Memory usage of dataframe is {:.2f} MB'.format(start_mem))
    
    for col in df.columns:
        col_type = df[col].dtype
        
        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)  
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
        else:
            df[col] = df[col].astype('category')

    end_mem = df.memory_usage().sum() / 1024**2
    print('Memory usage after optimization is: {:.2f} MB'.format(end_mem))
    print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))
    
    return df