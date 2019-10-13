from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn import metrics
import numpy as np
from scipy import sparse
import logging

def cvmRun(dict_conf, M, colnames, rownames):
    
    '''
    Run a k-fold random forest. 
    :param dict_conf: Dictionary containing setting parameters. 
    :param M: Matrix containing features. 
    :param colnames: Array of columns names. 
    :param rownames: Array of rows names. 
    :return: Predictions
    '''

    np.random.seed(1102)

    M = sparse.csc_matrix(M)

    y = np.array(M[:, colnames.index[colnames == dict_conf["target"]]].todense()).flatten()
    if dict_conf["target_type"] == "classification":
        y = np.array((y > dict_conf["threshold"]) + 0)
    if sum(y == 0) == len(y):
            logging.warning("Target " + dict_conf["target"] + " | Target always zero!")
            y[0] = 1
    
    X = M[:, colnames.index[colnames.isin(dict_conf["features"])]]
    
    random_folds = np.random.choice(range(dict_conf["nfolds"]), size=len(y)) + 1
    while len(np.unique(random_folds)) != dict_conf["nfolds"]:
        random_folds = np.random.choice(range(dict_conf["nfolds"]), size=len(y)) + 1
    
    predictions = np.zeros(len(y))

    if dict_conf["target_type"] == "classification":
        model = RandomForestClassifier(
            n_estimators=dict_conf["n_estimators"], 
            max_depth=dict_conf["max_depth"], 
            random_state=1102
        )
    else:
        model = RandomForestRegressor(
            n_estimators=dict_conf["n_estimators"], 
            max_depth=dict_conf["max_depth"], 
            random_state=1102
        ) 

    for k in range(dict_conf["nfolds"]):
        k = k + 1
        logging.debug("Target " + dict_conf["target"] + " | Fold " + str(k) + ".")
        bln_tmp = (random_folds != k)
        X_tmp = X[rownames.index[bln_tmp], ]
        y_tmp = y[bln_tmp]
        if sum(y_tmp == 0) == len(y_tmp):
            logging.warning("Target " + dict_conf["target"] + " | Fold " + str(k) + " | Target always zero!.")
            y_tmp[0] = 1
        model.fit(X_tmp, y_tmp)
        if dict_conf["target_type"] == "classification":
            predictions_tmp = model.predict_proba(X[rownames.index[~bln_tmp], :])
            predictions[~bln_tmp] = predictions_tmp[:, model.classes_ == 1].flatten()
        else:
            predictions_tmp = model.predict(X[rownames.index[~bln_tmp], :])
            predictions[~bln_tmp] = predictions_tmp

    if dict_conf["target_type"] == "classification":
        fpr, tpr, _ = metrics.roc_curve(y_true=y+1, y_score=predictions, pos_label=2)
        logging.debug("Target " + dict_conf["target"] + " | AUC on training set: " + str(metrics.auc(fpr, tpr)) + ".")
    else: 
        logging.debug("Target " + dict_conf["target"] + " | RMSE on training set: " + str( np.mean( (predictions-y)**2 )**(0.5) ) + ".")

    return predictions



import multiprocessing
import functools

def cvmMultiRun(array_dict_conf, M, colnames, rownames, npool=6):
    '''
    Run cvmRun in multiprocessing. 
    :param array_dict_conf: List of dictionaries containing setting parameters. 
    :param M: Matrix containing features. 
    :param colnames: Array of columns names. 
    :param rownames: Array of rows names.
    :param npool: Number of workers.  
    :return: Predictions
    '''
    pool = multiprocessing.Pool(npool)
    output = pool.map(functools.partial(cvmRun, M=M, colnames=colnames, rownames=rownames), array_dict_conf)
    return output

