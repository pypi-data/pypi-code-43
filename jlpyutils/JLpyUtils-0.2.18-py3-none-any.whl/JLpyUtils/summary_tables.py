
#Fetch unique Device IDs
def Count_subgroups_in_group(df,group_label='Device_ID',sub_group_label='Composite_ID',Additional_output_labels=None):
    """
    create a summary table showing the count for subgroups within a group
    
    Arguments:
        df,
        group_label='Device_ID',
        sub_group_label='Composite_ID',
        Additional_output_labels: a list of columns that are less or equally unique as the subgroup
    Returns:
        df_group_w_subgroup_count
    Example:
        display(Count_subgroups_in_group(df,group_label='Wafer_ID_Terse',sub_group_label='Composite_ID',Additional_output_labels=['DescriptionScribe_ID']))   

    """
    import pandas as pd
    import numpy as np


    df_group = df.groupby(group_label)
    group_ID_list = []
    subgroup_count_list = []
    df_group_w_subgroup_count = pd.DataFrame()
    for group_ID, group_subset in df_group:
        if Additional_output_labels == None:
            group_subset_out = group_subset[[group_label]].drop_duplicates()
        else:
            group_subset_out = group_subset[[group_label, *Additional_output_labels]].drop_duplicates()
        df_group_w_subgroup_count = pd.concat((df_group_w_subgroup_count,group_subset_out),axis=0).reset_index(drop=True)
        
        subgroup_count_list.append(group_subset[sub_group_label].drop_duplicates().count())
        
    df_group_w_subgroup_count[sub_group_label+'_Count'] = subgroup_count_list
    
    return df_group_w_subgroup_count

def count_unique_devices(df):
    import pandas as pd
    import numpy as np


    n_unique_devices = df['Composite_ID'].drop_duplicates().count()
    print('n_unique_devices:',n_unique_devices)
    return n_unique_devices