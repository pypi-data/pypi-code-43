import pandas as pd
import numpy as np
from collections import deque
import random

class Sequence_builder:
    def __init__(self):
        pass

    def fit_transform(self, data_frame, target_list, sequence_length, prediction_length=1, shuffle=False, labels=None):

        if (prediction_length < 1):
            raise ValueError('Invalid value for prediction_length')

        if (sequence_length < 1):
            raise ValueError('Invalid value for sequence_length')
            
        target_data_frame = pd.DataFrame()
        
        for p in range(prediction_length):
            for target_label in target_list:
                target_data_frame['future_' + target_label + '_step_t+' +
                                  str(p+1)] = data_frame[target_label].shift(-(p+1))

        # create sequences
        all_sequences = []
        seq = deque(maxlen=sequence_length)

        if (isinstance(data_frame, pd.DataFrame)):
            for index, row in data_frame.iterrows():
                seq.append(list(row))
                if (len(seq) == sequence_length):
                    all_sequences.append(np.array(seq, dtype='float'))
        else:
            raise TypeError('No pandas dataframe detected')

        # convert dataframes to numpy array
        X = np.array(all_sequences)
        y = np.array(target_data_frame)

        # remove rows with nans: the last prediction_length lines
        X = np.delete(X, np.s_[-prediction_length:], axis=0)
        y = np.delete(y, np.s_[-prediction_length:], axis=0)

        # remove rows with nans: the first sequence_length-1 lines
        y = np.delete(y, np.s_[0:sequence_length-1], axis=0)

        # optional: class labels for checking unsupervised results
        if (labels is not None):
            # convert the labels to a numpy array
            labels = labels.as_matrix(columns=labels.columns)
            # drop specific rows
            labels = np.delete(labels, np.s_[-prediction_length:], axis=0)
            labels = np.delete(labels, np.s_[0:sequence_length-1], axis=0)

        # shuffle the sequences if the user sets this parameter
        if (shuffle):
            permutation = np.random.permutation(len(X))
            X = X[permutation]
            y = y[permutation]
            if (labels is not None):
                labels = labels[permutation]

        return X, y, labels


if __name__ == '__main__':
    pass
