import numpy as np
import pandas as pd 

def fit(df, binary_classification_target_column, columns_to_treat=[], verbose=False):


def kesh_label_encoder(df, binary_classification_target_column, columns_to_treat=[], verbose=False):
    if len(columns_to_treat)==0: # Apply for all categorical
        all_columns = list(df.columns)
        all_columns.remove(binary_classification_target_column)
        columns_to_treat = df[all_columns].select_dtypes(include=['category', object]).columns.tolist()

    for a_column_to_treat in columns_to_treat:
        if verbose:
            print(a_column_to_treat)
        ct=pd.crosstab(df[a_column_to_treat], df[binary_classification_target_column])
        cross_df=ct.div(ct.sum(1).astype(float), axis=0)
        cross_df=cross_df.sort_values(cross_df.columns[1])
        value_order = list(cross_df.index)
        cat_label = 1
        for aVal in value_order:
            if verbose:
                print('Replacing [' + aVal + '] with '+str(cat_label))
            df.loc[df[a_column_to_treat]==aVal,a_column_to_treat]=cat_label
            cat_label = cat_label+1