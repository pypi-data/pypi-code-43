import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

# __1.6__


def testplot(yt, pred):
    '''
    Author: Aru Raghuvanshi

    This function plots Predictions against Truth Values
    of the Algorithm. Best used for Regression Models.

    Arguments: truth, pred
    Returns: Plot

    '''
    import matplotlib.pyplot as plt
    plt.style.use('seaborn')

    xaxis = range(1, yt.shape[0] + 1)
    plt.figure(figsize=(15, 6))
    plt.scatter(xaxis, yt, color='green', label='Truth Data', marker='o')
    plt.plot(xaxis, pred, color='limegreen', label='Prediction')
    plt.xlabel('Test Observations', fontsize=14)
    plt.ylabel('Predictions', fontsize=14)
    plt.title('Truth Vs Predicted', fontsize=16)
    plt.legend(fontsize=15, loc=4)
    plt.show()

# ======================== FITTING PLOT =========================== ]


# __1.4.3__


def fittingplot(clf, a, b):

    '''
    Author: Aru Raghuvanshi

    This functions takes a single feature and target variable, and plots
    the regression line on that  data to see the fit of the model. The shapes
    of input data should X.shape=(abc,1) and y.shape=(abc, ).

    Argument: estimator, X, y
    Returns: Plot
    '''
    import numpy as np
    import matplotlib.pyplot as plt
    plt.style.use('seaborn')

    a = np.asarray(a).reshape(-1, 1)

    X_grid = np.arange(min(a), max(a), 0.01)
    X_grid = X_grid.reshape((len(X_grid), 1))

    plt.figure(figsize=(14, 6))
    plt.scatter(a, b, color=np.random.rand(3,))   # color=np.random.rand(3,) - to test for 1.4.2
    clf.fit(a, b)
    plt.plot(X_grid, clf.predict(X_grid), color='black')

    plt.title('Fitting Plot', fontsize=16)
    plt.xlabel('Predictor Feature', fontsize=14)
    plt.ylabel('Target Feature', fontsize=14)

    plt.show()





# ======================== FORECAST PLOT =========================== ]

# __1.6.2__


def plot_forecast(true, pred):

    '''
    Author: Aru Raghuvanshi

    This function plots the graph of the Truth values
    and Predicted values of a predictive model and
    visualizes in the same frame. The truth values
    and pred value sizes should be same and both
    should be sharing the same x-axis.


    Arguments: truth value, predicted value
    Returns: Plot

    '''

    import matplotlib.pyplot as plt
    plt.style.use('seaborn')

    plt.figure(figsize=(15, 6))
    plt.plot(true, color='b', label='Test')
    plt.plot(pred, color=np.random.rand(3, ), label='Predicted')
    plt.xlabel('Variable', fontsize=16)
    plt.ylabel('Target', fontsize=16)
    plt.title('Truth v/s Prediction Chart', fontsize=16)
    plt.legend()
    plt.show()