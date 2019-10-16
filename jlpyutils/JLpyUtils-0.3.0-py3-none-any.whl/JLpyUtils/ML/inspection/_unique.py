
def uniques(df):
    """
    Inspect number of unique values and the unique values themselves for the passed dataframe
    """
    
    dtypes = df.dtypes.reset_index()
    dtypes.columns = ['column','dtype']
    dtypes = dtypes.sort_values(['dtype','column'])
    
    for col in dtypes['column']:
        
        if 'dask' in str(type(df)):
            uniques = df[col].compute().sort_values().unique()
        else:
            uniques = df[col].sort_values().unique()
        
        n_uniques = len(uniques)
        
        print('\n----',col,'----', 
              '\nn_uniques:',n_uniques,
              '\ndtype:',uniques.dtype)
        
        if n_uniques<=20:
            print('\nuniques[:]:')
            display(list(uniques))
        else:
            print('\nuniques[:20]:')
            display(list(uniques[:20])+['...'])