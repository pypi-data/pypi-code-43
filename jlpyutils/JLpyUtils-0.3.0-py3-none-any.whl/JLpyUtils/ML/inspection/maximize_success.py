"""
This sub-module contains functions to evaluate how a model could maximize success for a given problem
"""

def dropping_label_categories(model, X, y, drop_label_categories, show_plot = True):
    """
    maximize success for a given problem by dropping the rows/samples containing the labels in the drop_label_categories list. This type of maximization is appropriate for problems such as credit default, where one wishes to simply ignore customers who will default.

    Arguments:
    ----------
        model: the model object of interest from which predictions will be made on the X dataset passed
        X, y: The features and labels the evaluation will be performed on
        drop_label_categories: list. The names of the label categories you wish to exclude for optimal results.

    Returns:
    -------
        df_lift: The lift score for each of the categories in the drop_label_categories list.
            - The lift is calculated as the original % of occurances / the % of occurances after dropping samples based on the predicted values
        y_drop: The true values corresponding to the samples selected after dropping the label categories from the y_pred 
        y_pred_drop: The remaining predicted values after dropping the samples with values matching those in the drop_label_categories list
        y_drop_value_counts: Pandas df containg the value counts for the label categories before dropping based on the predicted values
        y_drop_value_counts: Pandas df containg the value counts for the label categories after dropping based on the predicted values
    """
    import pandas as pd

    y_pred = model.predict(X)
    y_pred = pd.DataFrame(y_pred, columns = list(y.columns))

    y_pred.index = y.index

    y_pred_drop = y_pred[~(y_pred.iloc[:,0].isin(drop_label_categories))]
    drop_idx_list = list(y_pred[(y_pred.iloc[:,0].isin(drop_label_categories))].index.values)

    y_drop = y.drop(drop_idx_list)
    assert(y_drop.shape==y_pred_drop.shape)

    y_value_counts = y.iloc[:,0].value_counts().reset_index()
    y_value_counts.columns = [y.columns[0], 'counts']
    y_value_counts['% of Total'] = y_value_counts['counts']/y_value_counts['counts'].sum()*100

    y_drop_value_counts = y_drop.iloc[:,0].value_counts().reset_index()
    y_drop_value_counts.columns = [y_drop.columns[0], 'counts']
    y_drop_value_counts['% of Total'] = y_drop_value_counts['counts']/y_drop_value_counts['counts'].sum()*100

    df_lift = (y_value_counts['% of Total'][y_value_counts.iloc[:,0].isin(drop_label_categories)] / y_drop_value_counts['% of Total'][y_drop_value_counts.iloc[:,0].isin(drop_label_categories)]).reset_index()
    df_lift.columns = [y.columns[0],'lift']
    
    if show_plot:
        import matplotlib.pyplot as plt
        
        fig, ax_list = plt.subplots(1,2)
        p=0
        for ylabel in ['counts', '% of Total']:
            for df_counts, label in [[y_value_counts, 'before drop'],
                                     [y_drop_value_counts, 'after drop']]:
                ax_list[p].bar(df_counts[y.columns[0]].astype(str), 
                       df_counts[ylabel], label = label,alpha=0.5)

            ax_list[p].set_xticklabels(df_counts[y.columns[0]].astype(str), rotation=90)
            ax_list[p].legend()

            header = y.columns[0]
            if len(header)>20:
                xlabel = '\n'.join(header.split(' '))
            else:
                xlabel = header

            ax_list[p].ticklabel_format(axis='y', style='sci', scilimits=(-3,3))
            ax_list[p].set_xlabel(xlabel)
            ax_list[p].set_ylabel(ylabel)
            ax_list[p].grid(which='both',visible=False)
            p+=1
            
        fig.tight_layout(rect=(0,0,1.5,1))
        plt.show()

    return df_lift, y_drop, y_pred_drop, y_value_counts, y_drop_value_counts

def varying_features_for_max_prob(model, X, y, 
                                    free_categorical_features= None, 
                                    free_continuous_features = None, 
                                    success_label = 1,
                                  verbose = 1):
    """
    Vary features in X to maximize the probability of success.
    
    Arguments:
    ----------
        model: the model object of interest from which predictions will be made on the X dataset passed
        X, y: The features and labels the evaluation will be performed on. We assume the categorical features in the X data should be One-Hot encoded, such that their values are only either 0 or 1.
        LabelEncoder: The LabelEncoder object that defines the possible categorical features which 
        free_categorical_features: the categorical features in X which can be freely varied for success
        free_continuous_features: the continuous features in X which can be freely varied for success
        success_label: the label category in y which you want to be maxime success/probability for.
        verbose: print-out verbosity
        
    Returns:
    --------
        X_opt: Pandas DataFrame with the optimal parameters inserted for each case in X
        y_opt_probas: the probabilities for each optimal condition
        lift_dict: dictionary containing various lift metrics ('mean(opt/orig proba)', 'median(opt/orig proba)', 'stddev(opt/orig probe)':np.std(y_opt_probas/y_proba))
    """
    import itertools
    import joblib
    import scipy, scipy.optimize
    import sklearn, sklearn.metrics
    import numpy as np
    import warnings
    
    def cont_feat_optimizer(X_slice,
                       free_cat_feature_headers,
                       free_cont_feature_headers, 
                       model,
                       success_label,
                       cat_feat_combo
                      ):
        """
        Optimizer to find the best free continuous feature values for a given example (slice) of features and labels
        """
        import scipy, scipy.optimize
        
        #update X_slice free categorical features with categorical feature combo case
        X_slice[free_cat_feature_headers] = cat_feat_combo
        
        def loss(free_cont_feat_vals,
                 free_cont_feature_headers, 
                 X_slice, model):
            X_slice[free_cont_feature_headers] = free_cont_feat_vals
            y_pred_proba = model.predict_proba(X_slice)
            loss_ = 1-y_pred_proba[0][success_label]
            return loss_
        
        #define initial guess for optimial free continuous feature values
        free_cont_feat_vals = np.array(X_slice[free_cont_feature_headers]).reshape(-1,1)
        
        #run optimizer for free continuous features
        results = scipy.optimize.minimize(loss, free_cont_feat_vals, 
                                          args = (free_cont_feature_headers, 
                                                  X_slice, model)
                                         )
        
        #fetch optimal results and updated X_slice
        optimal_cont_feat_vals = results['x']
        X_slice[free_cont_feature_headers] = optimal_cont_feat_vals
        
        y_pred_proba = model.predict_proba(X_slice)
        y_pred_proba = y_pred_proba[0][success_label]
        
        return optimal_cont_feat_vals, y_pred_proba
    
    def cat_cont_feat_optimizer(X_slice,
                               free_categorical_features,
                               free_continuous_features, 
                               model,
                               success_label,
                               cat_feat_combos):
        
        results_dict={'cat features':[],
                      'optimal_cont_feat_vals':[],
                      'y_pred_proba':[]}
        for cat_feat_combo in cat_feat_combos:
            optimal_cont_feat_vals, y_pred_proba = cont_feat_optimizer(X_slice,
                                                           free_categorical_features,
                                                           free_continuous_features, 
                                                           model,
                                                           success_label,
                                                           cat_feat_combo
                                                          )
            results_dict['cat features'].append(cat_feat_combo)
            results_dict['optimal_cont_feat_vals'].append(optimal_cont_feat_vals)
            results_dict['y_pred_proba'].append(y_pred_proba)
        idx_max_proba = np.argmax(results_dict['y_pred_proba'])
        
        opt_cat_feat_vals = results_dict['cat features'][idx_max_proba]
        opt_cont_feat_vals = results_dict['optimal_cont_feat_vals'][idx_max_proba]
        opt_proba = results_dict['y_pred_proba'][idx_max_proba]
        
        return opt_cat_feat_vals, opt_cont_feat_vals, opt_proba
    
    warnings.filterwarnings('ignore')
    
    #fetch baseline probs
    y_proba = model.predict_proba(X)[:,success_label]
    
    #fetch locked features list
    locked_features = [feature for feature in X.columns if feature not in free_categorical_features and feature not in free_continuous_features]
    
    #build all possible combinations of categorical features
    cat_feat_combos = list(itertools.product([0, 1], repeat=len(free_categorical_features)))
    
    X_opt = X
    y_opt_probas = []
    for i in range(X.shape[0]):
        if verbose>=1:
            print('Progress:',round(i/X.shape[0]*100,2),'%',end='\r')
        
        X_slice = X.iloc[i,:].to_frame().T
        
        opt_cat_feat_vals, opt_cont_feat_vals, opt_proba = cat_cont_feat_optimizer(
                                                                X_slice,
                                                                free_categorical_features,
                                                                free_continuous_features, 
                                                                model,
                                                                success_label,
                                                                cat_feat_combos)
        y_opt_probas.append(opt_proba)
        X_opt[free_categorical_features] = list(opt_cat_feat_vals)
        X_opt[free_continuous_features] = list(opt_cont_feat_vals)
    
    lift_dict = {'mean(opt/orig proba)':np.mean(y_opt_probas/y_proba),
                 'median(opt/orig proba)':np.median(y_opt_probas/y_proba),
                 'stddev(opt/orig probe)':np.std(y_opt_probas/y_proba)
                 }
    
    warnings.filterwarnings('default')
    
    return X_opt, y_opt_probas, lift_dict