import matplotlib.pyplot as __plt__

def true_vs_pred(y_true, y_pred, train_test_ID, 
                 scale = 'linear', color = 'dodgerblue',
                 rect = (0, 0, 1,1)
                ):
    """
    plot y_true vs. y_pred as a scatter plot
    
    Arguments:
    ----------
        y_true, y_pred: true & pred values
        train_test_ID: string. label to be appended to axis labels 'y_true' & 'y_pred'
        scale: 'linear' or 'log' scale to be used in the plot
        color: color to be used for the data points in the plot
        rect = tight_layout(rect=...) coordinates for plot size
    """
    
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(1,1)
    
    ax.plot(y_true, y_pred, 'o', color = color)
    ax.set_xlabel('y_true '+train_test_ID)
    ax.set_ylabel('y_pred '+train_test_ID)
    ax.set_xscale(scale)
    ax.set_yscale(scale)
    
    fig.tight_layout(rect = rect)
    
    plt.show()
    
def feature_importance(model, model_ID, feature_headers, 
                       max_labels = 30,
                       color = 'dodgerblue',
                       rect = (0, 0, 1, 1),
                      ):
    """
    Plot the feature importance for a given model
    
    Arguments:
    ----------
        model: the model object from which the feature importance will be derived
        model_ID: the type/ID of the model
            - valid arguments: 'RandomForest', 'DecisionTree'
        feature_headers: list of feature headers for labeling the plot
        max_labels: the max number of labels you want to plot. If more features than this are present, then the top and bottom half of the least and most important features will be plotted.
        color: default matplotlib color to use in the plot. If number of features>max_labels, the colors will be assigned automatically.
        rect: rectangular scaling coordinates for the plots tight_layout
    """
    valid_model_IDs = ['RandomForest','DecisionTree', 'xgboost']
    assert(model_ID in valid_model_IDs), 'Invalid model_ID passed. Valid model_IDs are:'+str(valid_model_IDs)
    
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    
    from . import feature_importance #import the function the build the df_feat_import
    
    df_feat_import = feature_importance.df(model, model_ID, feature_headers)
    
    fig, ax = plt.subplots(1,1)
    
    if df_feat_import.shape[0]>max_labels:

        bottom = df_feat_import.iloc[:int(max_labels/2), :]
        top = df_feat_import.iloc[-int(max_labels/2):, :]
        
        ax.bar(bottom['feature'], bottom['importance'], label = 'least important',
               yerr = bottom['stddev'], align="center", capsize=2)
        ax.bar(top['feature'], top['importance'], label = 'most important',
               yerr = top['stddev'], align="center", capsize=2)

        ax.set_xticklabels(list(bottom['feature'])+list(top['feature']), rotation=90)
        ax.legend()
    else:
        ax.bar(df_feat_import['feature'], df_feat_import['importance'],
               yerr=df_feat_import['stddev'], align="center", capsize=2,
               color = color)

        ax.set_xticklabels(df_feat_import['feature'], rotation=90)
    
    
    ax.set_ylabel('importance')
    ax.grid(which='both',visible=False)
    
    try:
        fig.tight_layout(rect=tight_layout_rect)
    except:
        None
    
    plt.show()
    
def confusion_matrix(y_true, y_pred, classes,
                      normalize=False,
                      title=None,
                      cmap=__plt__.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    
    import numpy as np
    import matplotlib.pyplot as plt

    from sklearn.metrics import confusion_matrix
    from sklearn.utils.multiclass import unique_labels
    
    if not title:
        if normalize:
            title = 'Normalized confusion matrix'
        else:
            title = 'Confusion matrix, without normalization\n'

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    fig, ax = plt.subplots()
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           # ... and label them with the respective list entries
           xticklabels=classes, yticklabels=classes,
           title=title,
           ylabel='True label',
           xlabel='Predicted label')

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    ax.grid(which='both',visible=False)
    fig.tight_layout()
    plt.show()

def False_pred_imgs(X, y, y_pred, label_encodings_dict = None):
    False_preds_mask = (y!=y_pred).any(axis=1)

    X_False_preds = X[False_preds_mask==True]
    y_true_False_preds = y[False_preds_mask==True]
    y_pred_False_preds = y_pred[False_preds_mask==True]

    n_columns = 3
    fig, ax_list = plt.subplots(1,n_columns)
    p=0
    for i in range(X_False_preds.shape[0]):
        True_label = y_true_False_preds[i,:]
        pred_label = y_pred_False_preds[i,:]

        if label_encodings_dict != None:
            True_label = [key for key in label_encodings_dict.keys() if [label_encodings_dict[key]]== True_label]
            pred_label = [key for key in label_encodings_dict.keys() if [label_encodings_dict[key]]== pred_label]
        title = 'True_label:'+str(True_label) + '\n' + \
                'pred_label:'+ str(pred_label) +'\n'

        if p > n_columns-1:
            fig.tight_layout(rect=(0,0,n_columns, 1))
            plt.show()

            p=0
            fig, ax_list = plt.subplots(1,n_columns)
            for ax in ax_list:
                ax.imshow(np.ones((256,256,3)))
                ax.grid(which='both',visible=False)
                ax.axis('off')

        ax_list[p].set_title(title)
        ax_list[p].imshow(X_False_preds[i,:,:,:])
        ax_list[p].axis('off')
        ax_list[p].grid(which='both',visible=False)

        p+=1
    