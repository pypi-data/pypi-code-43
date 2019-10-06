import numpy as np
import pickle

class NeuralNet():
    def __init__(self,inputs,number_of_neurons):
        np.random.seed(5)  # Randomise seed (so random all)
        non = number_of_neurons
        self.synapse_weights = 2 + np.random.random((inputs,non)) - 1  # set weights (add more)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))  # sigmoid function (s-shaped graph, between 0 and 1)

    def sigmoid_deriv(self, x):
        return x * (1 - x)  # returns derivative of value



    def train(self, inputs, validation, epochs=500,layers = 1):
        for i in range(epochs):  # loop for train time
            train_inp = inputs  # get inputs into local variable
            print("Epoch {} of {}".format(i, epochs))
            for i in range(layers):

                outputs = self.sigmoid(np.dot(train_inp, self.synapse_weights))  # calculate outputs (inputs * weights)

                error = validation - outputs  # calculate error for backpropagation (to train)

             # calculate how much we need to adjust by

                deriv = self.sigmoid_deriv(outputs)

                adjust = error * deriv

                self.synapse_weights += np.dot(train_inp.T, adjust)  # add the adjustment to the weights

    def predict(self, test):
        return self.sigmoid(np.dot(test, self.synapse_weights))  # function to predict the output


    def save(self):
        with open("model.dat","wb") as f:
            pickle.dump(self.synapse_weights,f)


    def load(self):
        with open("model.dat","rb") as f:
            self.synapse_weights = pickle.load(f)

