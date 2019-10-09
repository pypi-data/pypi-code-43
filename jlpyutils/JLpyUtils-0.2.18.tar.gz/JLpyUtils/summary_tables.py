
import pandas as _pd
import numpy as _np

#Fetch unique Device IDs
def count_subgroups_in_group(df,
                             group_label,
                             sub_group_label,
                             Additional_output_labels=None):
    """
    Create a summary table showing the count for subgroups within a group
    
    Arguments:
    ----------
        df: dataframe of interest
        group_label: column on which the data will be grouped by
        sub_group_label: column on which the nunique counts will be made for the defined group.
        Additional_output_labels: a list of columns that are less or equally unique as the subgroup
    
    Returns:
    --------
        df_group_w_subgroup_count: dataframe showing unique value counts for given subgroup in a group
    """

    df_group = df.groupby(group_label)
    group_ID_list = []
    subgroup_count_list = []
    df_group_w_subgroup_count = _pd.DataFrame()
    for group_ID, group_subset in df_group:
        if Additional_output_labels == None:
            group_subset_out = group_subset[[group_label]].drop_duplicates()
        else:
            group_subset_out = group_subset[[group_label, *Additional_output_labels]].drop_duplicates()
        df_group_w_subgroup_count = _pd.concat((df_group_w_subgroup_count,group_subset_out),axis=0).reset_index(drop=True)
        
        subgroup_count_list.append(group_subset[sub_group_label].drop_duplicates().count())
        
    df_group_w_subgroup_count[sub_group_label+'_count'] = subgroup_count_list
    
    return df_group_w_subgroup_count