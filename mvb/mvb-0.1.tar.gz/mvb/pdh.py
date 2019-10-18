
"""
pdh
pandas helper functions
@author: Michael Van Beek
"""

import pandas as pd
import numpy as np
import subprocess

def set_pandas_options(show_all_rows=True,
                       show_all_cols=True,
                       show_full_col=True):
    if show_all_rows:
        # do not truncate table rows
        pd.set_option("display.max_rows", None)

    if show_all_cols:
        # do not truncate columns
        pd.set_option('display.max_columns', None)  

    if show_full_col:
        # do not truncate cell contents
        pd.set_option('display.max_colwidth', -1)

def percentile(n):
    """
    @input n: 0-100 number representing percentile
    
    @returns: function which takes a list of values and returns percentile of those values
    """
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = f"percentile_{n}"
    return percentile_

def ps_df():
    """
    calls ps and returns results as a pandas dataframe

    @returns: pandas.DataFrame containing row per result from ps
    """
    f='pid:8,rss:8,user:32,cmd:256'
    F=f.upper()
    o=subprocess.check_output(['ps','-Ao',f'{f}'])
    d = list(map(lambda s: [int(s[0:8]),int(s[9:18]),s[18:48].strip(),s[49:].strip()],o.decode('utf8').split('\n')[1:-1]))
    df = pd.DataFrame(d,columns=['pid','memory','user','cmd']).set_index('pid')
    return df

def explode_dict_col(df,dict_col):
    """
    Takes a pandas dataframe and column name containing dictionaries.
    Explodes the dictionaries such that each key in the dict becomes a value in the resulting dataframe.
    
    @input df: pandas dataframe to act on
    @input dict_col: string name of column containing a dict to explode    
    
    @returns: new pandas dataframe where dict_col`
    """
    return pd.concat([df.drop([dict_col], axis=1), df[dict_col].apply(pd.Series)], axis=1, sort=False)

def explode_kv_str_col(df,kv_str_col,kv_delim='=',item_delim='&'):
    """
    Takes a dataframe and explodes kv_str_col into key value pairs, which it returns as new columns
    
    @input kv_str_col: string name of the column containing kev value string
    @input kv_delim: delimiter between keys and values, default '=' 
    @input item_delim: delimiter between items (key value pairs), default '&'
        
    @returns: new panadas dataframe with values transformed
    """
    df[kv_str_col] = df[kv_str_col].apply(lambda s: str_to_dict(s,kv_delim,item_delim))
    return explode_dict_col(df,kv_str_col)

def add_section_header(df,section_header):
    """
    Transforms a pandas dataframe with single level column index to a multi index
    with a section header over all columns.
    
    @input df: pandas dataframe to transfrom
    @input section_header: string to use as section header
    """
    df.columns = pd.MultiIndex.from_product([[section_header],df.columns], names=['section', 'metric'])
    
def color_by_section(section_color_map):
    def color_section(series):
        section = series.name[0]
        if section in section_color_map:
            color = section_color_map[section]
            return [f"background-color: {color}" for c in series]
        else:
            return ["" for c in series]
    return color_section
