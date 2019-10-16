def df(model, model_ID, feature_headers):
    """
    Plot the feature importance for a given model
    
    Arguments:
    ----------
        model: the model object from which the feature importance will be derived
        model_ID: the type/ID of the model
            - valid arguments: 'RandomForest', 'DecisionTree'
        feature_headers: list of feature headers for labeling
    
    Returns:
    --------
        df_feat_import: Pandas DataFrame with the feature names, importance, and standard deviation, in the case of ensemble models.
    """
    import pandas as pd
    import numpy as np

    df_feat_import= pd.DataFrame(np.array(feature_headers).reshape(-1,1), columns = ['feature'])
    df_feat_import['importance'] = model.feature_importances_.reshape(-1,1)
    
    if model_ID in ['RandomForest']: #add standard dev of feat importances
        df_feat_import['stddev'] = np.std([tree.feature_importances_ for tree in model.estimators_],axis=0)
    else:
        df_feat_import['stddev']=0
        
    df_feat_import = df_feat_import.sort_values('importance').reset_index(drop=True)
    
    return df_feat_import