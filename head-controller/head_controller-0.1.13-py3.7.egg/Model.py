import numpy as np
import head_controller.db as db
from sklearn.model_selection import train_test_split
from sklearn import svm


class Model():

    def __init__(self):

        self.clf=None

    def build_svc(self):
        '''
        Expects X to be in the original shape as collected so that a standard
        transformation can be made during prediction.
        '''

        X,y = db.get_training_data()
        self.o_shape = X.shape
        X.resize(X.shape[0],(X.shape[1]*X.shape[2]))
        self.clf = svm.SVC(kernel='linear', C=1).fit(X,y)
        return self

    def predict_dataset(self,X):

        assert self.clf !=None,'Model.build_svc(X,y) has not been run yet.'
        assert self.o_shape[1]*self.o_shape[2] == len(X.ravel()),'Got a different shape than expected in training model.'
        X.resize((self.o_shape[1]*self.o_shape[2]))
        y_pred = self.clf.predict(X)
        print('Pred:{}'.format(y_pred))
        return y_pred
