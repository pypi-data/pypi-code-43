import pandas as pd
import numpy as np


# ======================= CUSTOM REGRESSORS ===================== ]


# __1.5__

def run_regressor(model, xtr, xt, ytr, yt, k=3):

    '''
    Author: Aru Raghuvanshi

    This Functions Fits a Regression model with the Train Datasets and
    predicts on a Test Dataset and evaluates its various metrics.
    Predictions are available in the global variable 'pred'.

    Default KFold cross validation is 3.

    Arguments: estimator, X_train, X_test, y_train, y_test
    Returns: Metrics, Plot

    '''

    import warnings
    from warnings import filterwarnings
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    from sklearn.model_selection import cross_val_score, KFold
    import matplotlib.pyplot as plt
    plt.style.use('seaborn')
    warnings.filterwarnings('ignore')

    model.fit(xtr, ytr)

    kf = KFold(n_splits=k, random_state=22)
    trsc = cross_val_score(model, xtr, ytr, cv=kf)
    tesc = cross_val_score(model, xt, yt, cv=kf)
    tr = np.mean(trsc)
    te = np.mean(tesc)
    global pred
    pred = model.predict(xt)

    rmse = np.sqrt(mean_squared_error(yt, pred))
    mae = mean_absolute_error(yt, pred)
    try:
        mape = (np.mean(np.abs((yt - pred) / yt)) * 100)
    except:
        mape = 'NA'

    tr = tr * 100
    te = te * 100

    if 1.1 > tr / te > 1.07:
        fit = 'Slight Over-Fit'
    elif 0.89 < tr / te < 0.93:
        fit = 'Slight Under-Fit'
    elif tr / te > 1.1:
        fit = 'Over-Fitted'
    elif tr / te < 0.89:
        fit = 'Under-Fitted'
    else:
        fit = 'Good Fit'

    table = pd.DataFrame({'CV Training Score': [tr],
                          'CV Test Score': [te],
                          'RMSE': [rmse],
                          'MAE': [mae],
                          'MAPE %': [mape],
                          'Fit': [fit]
                          }).T

    fig = plt.figure(figsize=(14, 5))
    plt.ylim(0, 1)
    plt.plot(range(1, k + 1), trsc, label='Cross Validated Training Scores', color='navy',
             marker='o', mfc='black', ls='dashed')
    plt.plot(range(1, k + 1), tesc, label='Cross Validated Test Scores', color='salmon',
             marker='o', mfc='red')
    plt.xlabel('Cross Validation Iterations', fontsize=14)
    plt.ylabel('Model Scores', fontsize=14)
    plt.title('Train vs Test Scores', fontsize=16)
    plt.legend(fontsize=14)

    table.rename(columns={0: 'Score'}, inplace=True)

    print('\nPredictions stored in global variable "pred".')
    return table


# ============================= FIT CLASSIFY ============================ ]


# __1.5__

def run_classifier(model, xtr, xt, ytr, yt, k=3):

    '''
    Author: Aru Raghuvanshi

    This Functions Fits a classification model with the Train Datasets and
    predicts on a Test Dataset and evaluates its various metrics.
    Predictions are available in the global variable 'pred'.

    Default KFold cross validation is 3.

    Arguments: estimator, X_train, X_test, y_train, y_test
    Returns: Metrics, Plot

    '''

    import warnings
    from warnings import filterwarnings
    from sklearn.model_selection import KFold, cross_val_score
    from sklearn.metrics import classification_report
    import matplotlib.pyplot as plt

    warnings.filterwarnings('ignore')

    model.fit(xtr, ytr)
    #     tr = model.score(xtr, ytr)
    #     te = model.score(xt, yt)
    global pred
    pred = model.predict(xt)

    kf = KFold(n_splits=k, random_state=22)

    graphtr = cross_val_score(model, xtr, ytr, cv=kf, scoring='accuracy')
    graphte = cross_val_score(model, xt, yt, cv=kf, scoring='accuracy')

    tr = np.mean(cross_val_score(model, xtr, ytr, cv=kf, scoring='accuracy'))
    te = np.mean(cross_val_score(model, xt, yt, cv=kf, scoring='accuracy'))

    tepr = np.mean(cross_val_score(model, xt, yt, cv=kf, scoring='precision_weighted'))
    tere = np.mean(cross_val_score(model, xt, yt, cv=kf, scoring='recall_weighted'))
    tef1 = np.mean(cross_val_score(model, xt, yt, cv=kf, scoring='f1'))
    tr = tr * 100
    te = te * 100

    if 1.1 > tr / te > 1.07:
        fit = 'Slight Over-Fit'
    elif 0.89 < tr / te < 0.93:
        fit = 'Slight Under-Fit'
    elif tr / te > 1.1:
        fit = 'Over-Fitted'
    elif tr / te < 0.89:
        fit = 'Under-Fitted'
    else:
        fit = 'Good Fit'

    table = pd.DataFrame({
        'CV Training Score': [tr],
        'CV Test Score': [te],
        'Precision': [tepr],
        'Recall': [tere],
        'F1-Score': [tef1],
        'Fit': [fit]
    }).T

    table.rename(columns={0: 'Score'}, inplace=True)

    fig = plt.figure(figsize=(14, 5))
    plt.ylim(0, 1)
    plt.plot(range(1, k + 1), graphtr, label='Cross Validated Training Scores', color='navy',
             marker='o', mfc='black', ls='dashed')
    plt.plot(range(1, k + 1), graphte, label='Cross Validated Test Scores', color='salmon',
             marker='o', mfc='red')
    plt.xlabel('Cross Validation Iterations', fontsize=14)
    plt.ylabel('Model Scores', fontsize=14)
    plt.title('Train vs Test Scores', fontsize=16)
    plt.legend(fontsize=14)

    print('\nPredictions stored in global variable "pred".')
    return table






# ---------------------------------KMEANS K FINDER ------------------------------]


def kmeans_kfinder(dtf, lower=1, upper=9):

    '''
    Author: Aru Raghuvanshi

    Standardize (StandardScaler) data before feeding to function.
    This functions plots the Elbow Curve for KMeans Clustering
    to find the elbow value of K.

    Arguments: (dataframe, lower=1, upper=9)
    Returns: Plot

    Defaults of lower=0, upper=7
    Example: e = elbowplot(df, 0, 5)
    '''

    from sklearn.cluster import KMeans
    import matplotlib.pyplot as plt
    plt.style.use('seaborn')

    #     from scipy.spatial.distance import cdist
    k_range = range(lower, upper)
    sse = []
    for i in k_range:
        km = KMeans(n_clusters=i)
        km.fit(dtf)
        sse.append(km.inertia_)
    #       sse.append(sum(np.min(cdist(dtf, km.cluster_centers_, 'euclidean'), axis=1)) / dtf.shape[0]))

    plt.figure(figsize=(14, 6))
    plt.plot(k_range, sse, label='K vs SSE', color='g', lw=3, marker='o', mec='black')
    plt.xlabel('K', fontsize=18)
    plt.title('KMEANS ELBOW PLOT - K vs Sum of Square Error', fontsize=16)
    plt.legend()
    plt.show()



# ----------------------------- KNN K FINDER --------------------------------]


def knn_kfinder(xtr, xt, ytr, yt, lower=1, upper=30):

    '''
    Author: Aru Raghuvanshi

    This function plots the KNN elbow plot to figure out
    the best value for K in the KNN Classifier.

    Arguments: (xtr, xt, ytr, yt, lower=1, upper=30)
    Returns: Plot

    Example: p = knn_plot(X_train, X_test, y_train, y_test, 1, 30)

    '''
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import accuracy_score
    import matplotlib.pyplot as plt
    plt.style.use('seaborn')

    krange = range(lower, upper)
    acc_score = []
    # Might take some time
    for i in krange:
        knn = KNeighborsClassifier(n_neighbors=i)
        knn.fit(xtr, ytr)
        pred_i = knn.predict(xt)
        acc_score.append(accuracy_score(yt, pred_i))

    plt.figure(figsize=(14, 6))
    plt.plot(krange, acc_score, color='salmon', linestyle='solid',
             marker='o', mfc='purple', label='K vs Testing Accuracy', lw=2)
    plt.title('KNN K-GRAPH')
    plt.xlabel('K', fontsize=18)
    plt.ylabel('Test Accuracy', fontsize=16)
    plt.legend()
    plt.show()