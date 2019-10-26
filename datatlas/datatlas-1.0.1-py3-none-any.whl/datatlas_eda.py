
"""
Datatlas: Data Atlas
* Data profiling

Author: Mei Yong
Updated date: 2019-10-26

WIP Ideas
    * Distinct values
	* YesNo
	* Categorical
	* ID check
		- sequential score
		- Check for repeated value score - mask then group then average where zero is means more repeated values and one means less repeated values and closer to zero is more likely to be an ID
		-Check for Benford's law - basically if the values start with the same number or set of numbers
     * y/n check
        - Convert to string (keep the NaNs)
        - Check for common y/n values
	* Date check
        - Remove NaNs
        - Convert to string
        - Check regex and label
        - Count up the labels
        - If >60% date then date warning
	* Treat dates
		- split into year, month, day
		- days between current date and column date
		- convert to weekday, weekend, holidays
	* If high cardinality, check if can bucket smaller cats into other
	* Skew & should be log. must be positive. can add 1 to data to positive
	* If column should be split/pivoted
	* Only few different numbers which are actually categories
	* Treatments for time series data


"""

# Simple function for testing package installation and function calling
def say_hello(name):
	print(f"Hello {name}")
	
################################################################################



# Get DQ warnings based on relevant prior analyses
def get_dq_warnings(null_dict_p, nulls_threshold, zeroes_dict_p, zeroes_threshold, cardinality_dict, cardinality_threshold, dictinct_val_dict, dtype_regex_detail, dtype_dict, dtype_regex_final):
    '''
    Input(s):
        1) Relevant DQ dictionaries
        2) Relevant threshold values
    Output(s):
        1) A dictionary with column names as keys and values are lists of DQ warnings
    '''
    
    import pandas as pd
    
    # Flag up columns with values that may have DQ issues
    warning_null_dict = {key: 1 for key,value in null_dict_p.items() if value >= nulls_threshold }
    warning_zeroes_dict = {key: 1 for key,value in zeroes_dict_p.items() if value >= zeroes_threshold }
    warning_cardinality_dict = {key: 1 for key,value in cardinality_dict.items() if value >= cardinality_threshold }
    warning_one_distinct_dict = {key: 1 for key,value in dictinct_val_dict.items() if value == 1 }
    warning_dtype_mixed_dict = {key: 1 for key,value in dtype_regex_detail.items() if value['mixed']>0}
    
    warning_dtype_mismatch_dict = {}
    for column, auto_dtype_value, regex_dtype_value in zip(dtype_dict.keys(), dtype_dict.values(), dtype_regex_final.values()):
        if regex_dtype_value == 'numeric' and auto_dtype_value in ['object']:
            warning_dtype_mismatch_dict[column] = 1
        if regex_dtype_value == 'non-numeric' and auto_dtype_value in ['float64','int64']:
            warning_dtype_mismatch_dict[column] = 1
            
    # Put the dictionaries of DQ flags together
    warning_df = pd.DataFrame([
                                warning_null_dict
                                ,warning_zeroes_dict
                                ,warning_cardinality_dict
                                ,warning_one_distinct_dict
                                ,warning_dtype_mixed_dict
                                ,warning_dtype_mismatch_dict
                                ]
                                , index = ['Nulls','Zeroes','Cardinality','Only_1_distinct',\
                                           'Mixed_dtype','Dtype_mismatch']   
                                )
    
    # Using the df of DQ flags, put together a list of lists of DQ warnings
    final_warnings_list = []
    for column in warning_df:
        column_warnings = []
        if warning_df.loc['Nulls' , column] == 1:
            column_warnings.append('High_null_percentage')
        if warning_df.loc['Zeroes' , column] == 1:
            column_warnings.append('High_zeroes_percentage')
        if warning_df.loc['Cardinality' , column] == 1:
            column_warnings.append('High_cardinality')
        if warning_df.loc['Only_1_distinct' , column] == 1:
            column_warnings.append('Only_1_unique_value')
        if warning_df.loc['Mixed_dtype' , column] == 1:
            column_warnings.append('Mixed_dtypes')
        if warning_df.loc['Dtype_mismatch' , column] == 1:
            column_warnings.append('Auto_vs_regex_dtype_mismatch')
        final_warnings_list.append(column_warnings)
        
    final_warnings_dict = dict(zip(warning_df.columns , final_warnings_list))
    
    return final_warnings_dict
    

# Get data type profiles using regex
def get_dtype_profile(df):
    '''
    Input(s):
        1) df to profile
    Output(s):
        1) Dictionary where key is the column name & value is a nested dictionary with percentages of numeric, non-numeric, or mixed characters
        2) Dictionary where key is the column name & value is the most likely data type it should be
    '''
    
    import re
    
    dtype_regex_detail = {}
    
    for column in df:
        
        col = df[column]
        
        # Data prep for regex
        col.dropna(inplace=True) # Drop nulls
        col = col.astype(str).str.lower() # Lowercase
        col = col.str.replace(' ','') # Remove whitespace
        col = col.apply(lambda x: re.sub(r'[^\w\s]', '', x)) # Remove punctuation
        
        numeric_count, string_count, mixed_count = 0, 0, 0
        
        for item in col:
            
            item_len = len(item)
            
            # Find the number of alphabets in the string
            alphabet_find = re.findall(r"[a-zA-Z]+", item)
            try:
                alphabet_len = len(alphabet_find[0])
            except:
                alphabet_len = 0
            
            # Find the number of numbers in the string
            number_find = re.findall(r"[0-9]+", item)
            try:
                number_len = len(number_find[0])
            except:
                number_len = 0
            
            # Note the number of strings that are fully alphabets, fully numbers, or mixed
            if item_len == number_len:
                numeric_count += 1
            elif item_len == alphabet_len:
                string_count += 1
            else:
                mixed_count += 1
        
        # Put the results together into a summary dictionary
        dtype_regex_result = {'numeric': round(numeric_count/len(col) *100, 2)
                            ,'non-numeric': round(string_count/len(col) *100, 2)
                            ,'mixed': round(mixed_count/len(col) *100, 2)   
                            }
            
        dtype_regex_detail[column] = dtype_regex_result
    
    # Using the summary dictionary, find the most common detected dtype
    dtype_regex_final = {}
    for column in dtype_regex_detail:
        d = dtype_regex_detail[column]
        dtype_regex_final[column] = max(d, key=d.get)
        # https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
    
    return dtype_regex_detail, dtype_regex_final




# Main function that profiles a df
def df_profiling(df, nulls_threshold=50.0, zeroes_threshold=50.0, cardinality_threshold=50.0):
    '''
    Input(s):
        1) df - dataframe to analyse
        2) nulls_threshold - int - default 50. Adds warning if >50% nulls
        3) zeroes_threshold - int - default 50. Adds warning if >50% zeroes for numerical dtype columns
        4) cardinality_threshold - int - default 50. Adds warning if >50% nulls for categorical dtype columns
    Output(s):
        1) Dataframe with statistics and data quality warnings about the input df
    '''

    import pandas as pd
    import numpy as np
    
    rowcount = df.shape[0]
    
    # Data type that is auto-detected
    dtype_dict = {column : df[column].dtype.name for column in df}
    
    # Data type using regex
    dtype_regex_detail, dtype_regex_final = get_dtype_profile(df)
    
    # Number of not-nulls
    count_dict = {column : df[column].count() for column in df}
    
    # Number of nulls
    null_dict_n = {column : df[column].isnull().sum() for column in df}
    
    # Percentage of nulls
    null_dict_p = {column : round(df[column].isnull().sum() / rowcount * 100, 2) for column in df}
    
    # Number of distinct categorical values
    dictinct_val_dict = {column: df[column].nunique() \
                         for column in df if df[column].dtype in ['object'] }
    
    # Percentage of distinct categorical values
    cardinality_dict = {column: round(df[column].value_counts().count() / rowcount * 100 , 2) \
                         for column in df if df[column].dtype in ['object'] }
    
    # Number of zeroes
    zeroes_dict_n = {column : (df[column]==0).sum() \
                         for column in df if df[column].dtype in ['int64','float64'] }
    # Percentage of zeroes
    zeroes_dict_p = {column : round((df[column]==0).sum() / rowcount * 100, 2) \
                         for column in df if df[column].dtype in ['int64','float64'] }
    
    # Mean numerical value
    mean_dict = {column : df[column].mean() \
                         for column in df if df[column].dtype in ['int64','float64'] }
    
    # Min numerical value
    min_dict = {column : df[column].min() \
                         for column in df if df[column].dtype in ['int64','float64'] }
    
    # Quartile 1 - 25%
    q1_dict = {column : np.percentile(df[column], 25) \
                         for column in df if df[column].dtype in ['int64','float64'] }
    # Quartile 2 - 50%
    q2_dict = {column : np.percentile(df[column], 50) \
                         for column in df if df[column].dtype in ['int64','float64'] }
    # Quartile 3 - 75%
    q3_dict = {column : np.percentile(df[column], 75) \
                         for column in df if df[column].dtype in ['int64','float64'] }
    
    # Max numerical value
    max_dict = {column : df[column].max() \
                         for column in df if df[column].dtype in ['int64','float64'] }
    
    # Outliers
    
    
    
    # DQ Warnings
    final_warnings_dict = get_dq_warnings(null_dict_p
                                          , nulls_threshold
                                          , zeroes_dict_p
                                          , zeroes_threshold
                                          , cardinality_dict
                                          , cardinality_threshold
                                          , dictinct_val_dict
                                          , dtype_regex_detail
                                          , dtype_dict
                                          , dtype_regex_final
                                          )
            
    
    # Put together the final summary profile
    df_profile = pd.DataFrame([
                        dtype_dict
                        ,dtype_regex_final
                        ,dtype_regex_detail
                        ,count_dict
                        ,null_dict_n
                        ,null_dict_p
                        ,dictinct_val_dict
                        ,cardinality_dict
                        ,zeroes_dict_n
                        ,zeroes_dict_p
                        ,mean_dict
                        ,min_dict
                        ,q1_dict
                        ,q2_dict
                        ,q3_dict
                        ,max_dict
                        #outliers
                        ,final_warnings_dict
                        ]
                        , index = ['Dtype_Auto','Dtype_Regex','Dtype_Detail',\
                                   'Count','Null(n)','Null(p)','Distinct_Values','Cardinality',
                                   'Zeroes(n)','Zeroes(p)','Mean','Min','Q1','Q2','Q3','Max','DQ_Warnings']       
                        )
    
    return df_profile



# test = df_profiling(df)

###################################################################################################

### To enable this module to be called from another Python file
    
if __name__ == '__main__':
    say_hello()
    df_profiling()


