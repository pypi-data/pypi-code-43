from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM, Dropout
from tensorflow.keras import optimizers
from tensorflow.keras.models import Model
import tensorflow.keras.models
import numpy as np


class Predictor:
    learning_rate = 0.001

    decay_lr = 0

    loss_fn = 'mean_squared_error'

    def __init__(self, output_activation, ft_range, lr=0.001):
        self.model = None
        self.output_activation = output_activation
        self.ft_range = ft_range
        self.learning_rate = lr

    def predict(self, input):
        return self.model.predict(input)

    def classify(self, input):
        return self.model.predict_proba(input), self.model.predict_classes(input)

    def load_model(self, path):
        self.model = tensorflow.keras.models.load_model(path)
        self.model._make_predict_function()

    def get_model(self, shape, num_forecasts, inner_activation='tanh'):
        model = Sequential()
        # Shape = (Samples, Timesteps, Features)
        model.add(LSTM(units=128, input_shape=shape,
                       return_sequences=False, activation=inner_activation))
        model.add(Dropout(0.2))

        model.add(Dense(units=num_forecasts, activation=self.output_activation))

        opt = optimizers.Adagrad(lr=self.learning_rate, decay=self.decay_lr)
        # opt = optimizers.rmsprop(lr=0.01)
        model.compile(optimizer=opt, loss=self.loss_fn, metrics=['mae'])
        model.summary()
        return model

    def get_model_configurable(self, shape, num_classes, inner_activation='tanh', num_dense_layers=2, num_units_per_layer=64, loss='mae', metrics=['mse']):
        model = Sequential()
        # Input arrays of shape (*, layers[1])
        # Output = arrays of shape (*, layers[1] * 16)
        model.add(LSTM(units=int(num_units_per_layer), input_shape=shape,
                       return_sequences=True, activation=inner_activation))
        for i in range(1,num_dense_layers-1):
            model.add(LSTM(units=int(num_units_per_layer),
                       return_sequences=True, activation=inner_activation))
        model.add(LSTM(units=int(num_units_per_layer), input_shape=shape,
                       return_sequences=False, activation=inner_activation))
        model.add(Dropout(0.2))
        model.add(Dense(units=num_classes, activation=self.output_activation))

        # opt = optimizers.Adagrad(lr=self.learning_rate, epsilon=None, decay=self.decay_lr)
        opt = optimizers.RMSprop(lr=self.learning_rate)
        model.compile(optimizer=opt, loss=loss, metrics=metrics)
        model.summary()
        self.model = model
        return model