# Load required libraries
import numpy as np
import pandas as pd

from KUtils.eda import data_preparation as dp

from sklearn.preprocessing import MinMaxScaler

def run_for_eternity(df, target_column_name, verbose=False):
    
    # Target column should be mapped to 0 and 1 (I cannot decide if it is str. So below code will raise error)
    df[target_column_name] = df[target_column_name].astype('int')
    df[target_column_name] = df[target_column_name].astype('category')
    
    # Step 1. Fix column names (df.query not comfortable with special chars)
    print('  Fixing column names bcoz df.query not comfortable with special chars in feature names')
    dp.fix_invalid_column_names(df)
    
    # Step 2: Convert all continuous variables to cut categorical bins after scaling
    print('  Converting all continuous variables to cut categorical bins after MinMaxScaling') 
    no_of_bins=10
    categorical_column_names = list(df.select_dtypes(include=['object', 'category']).columns)
    numerical_column_names =  [i for i in df.columns if not i in categorical_column_names]
    categorical_column_names.remove(target_column_name)
    
    scaler = MinMaxScaler()
    df[numerical_column_names] = scaler.fit_transform(df[numerical_column_names])
    
    for a_column in numerical_column_names:         
        df[a_column+'_tmp_bin'] = pd.cut(df[a_column], no_of_bins, labels=False)
        del df[a_column] # drop original column
        df[a_column+'_tmp_bin']=df[a_column+'_tmp_bin'].astype('str')
       
    # Step 3. Separate the +ve and -ve target dataset
    rule_columns = list(df.columns)
    rule_columns.remove(target_column_name)
    
    negative_target_df = df.loc[df[target_column_name]==0]
    positive_target_df = df.loc[df[target_column_name]==1]
    
    iter = 0
    query_iter_df = pd.DataFrame( columns = ['query_id', 'query', 'positive_record_Count', 'negative_record_Count','total_records', 'tp','tn','fp','fn'])
    print(' Has to go thru rows '+str(len(positive_target_df)))
    print(' Now wait...')
    while(len(positive_target_df)>0):
        selected_row = positive_target_df.iloc[0,:]
        filter_condition = ''
        for a_rule_column_name in rule_columns:
            if len(filter_condition)!=0:
                filter_condition =  filter_condition + ' and '
            filter_condition =  filter_condition + a_rule_column_name+'==\'' + selected_row[a_rule_column_name] + '\''

        filtered_positive_df = positive_target_df.query(filter_condition)
        filtered_negative_df = negative_target_df.query(filter_condition)
        positive_target_df = positive_target_df.drop(filtered_positive_df.index)
        negative_target_df = negative_target_df.drop(filtered_negative_df.index)
        
        tp=tn=fp=fn=0
        if (len(filtered_positive_df)==1 and len(filtered_negative_df)==0): # Can't decide easily give 50% to both class
            tp = 0.5
            fn = 0.5
        elif (len(filtered_positive_df)==0 and len(filtered_negative_df)==1): # Can't decide easily give 50% to both class
            tn = 0.5
            fp = 0.5
        elif (len(filtered_positive_df)>len(filtered_negative_df)): # Majority belongs to positive class
            tp = len(filtered_positive_df)
            fp = len(filtered_negative_df)
        elif (len(filtered_positive_df)<len(filtered_negative_df)): # Majority belongs to negative class
            tn = len(filtered_negative_df)
            fn = len(filtered_positive_df)
        else: # Rare case of Equal sample size - Distinute equally to all group
            tn = len(filtered_negative_df)/2
            tp = len(filtered_negative_df)/2
            fp = len(filtered_negative_df)/2
            fn = len(filtered_negative_df)/2
            
        total_records = len(filtered_positive_df) + len(filtered_negative_df)
        query_iter_df.loc[iter] =[iter, filter_condition, len(filtered_positive_df), len(filtered_negative_df),total_records, tp,tn,fp,fn ]
        iter=iter+1
        if verbose:
            if iter%500==0:
                print(' Remaining rows to process '+str(len(positive_target_df)))
        
        
    if len(negative_target_df)>0: # Leftover
        query_iter_df.loc[iter] =[iter, 'Leftover', 0, len(negative_target_df),len(negative_target_df), 0,len(negative_target_df),0,0 ]
    
        
    sum(query_iter_df['total_records'])
    
    total_tp=sum(query_iter_df['tp'])
    total_tn=sum(query_iter_df['tn'])
    total_fp=sum(query_iter_df['fp'])
    total_fn=sum(query_iter_df['fn'])
    
    accuracy = (total_tp+total_tn)/(total_tn+total_tp+total_fn+total_fp)
    sensitivity = total_tp/(total_tp+total_fn) 
    specificity = total_tn/(total_tn+total_fp)
    precision = total_tp/(total_tp+total_fp)
    
    print('Done.')
    
    error_range=0.01
    print('For this dataset max performance you can achieve is ')
    print('  Accuracy around {0:.3f}'.format(accuracy-error_range))
    print('  Sensitivity around {0:.3f}'.format(sensitivity-error_range))
    print('  Specificity around {0:.3f}'.format(specificity-error_range))
    print('  Precision around {0:.3f}'.format(precision-error_range))
    print('  Recall around {0:.3f}'.format(sensitivity-error_range))
    print('  --Try applying tranformations like PCA, tSNE or UMAP to improve the result--')
    
    return query_iter_df