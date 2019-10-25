from forecastlib.models.ClassificationMLModel import ClassificationMLModel
from sklearn.metrics import confusion_matrix
import pandas as pd


class ClassificationTrainer(object):
    def __init__(self, train_data: pd.DataFrame, test_data: pd.DataFrame, label_name: str, features):
        self.features = features
        self.X_train = train_data[features]
        self.X_test = test_data[features]
        self.y_train = train_data[label_name]
        self.y_test = test_data[label_name]

    def Train(self, classifier):
        # self.classifier = self.GetClassifier()
        self.classifier = classifier
        self.model = self.classifier.fit(self.X_train, self.y_train)
        return self.model

    def Test(self):
        y_predict = self.model.predict(self.X_test)
        self.accuracy = self.model.score(self.X_test, self.y_test)
        print("Accuracy: " + str(self.accuracy))
        return confusion_matrix(self.y_test, y_predict)

    def Scale(self):
        self.X_train = self.featureScaler.fit_transform(self.X_train)
        self.X_test = self.featureScaler.transform(self.X_test)

    def GetModel(self):
        return ClassificationMLModel(self.model, self.features)