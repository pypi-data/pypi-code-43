# -*- coding: utf-8 -*-
import tensorflow as tf
# 这样import keras可以查看keras源代码
from tensorflow.python import keras


class KerasModelMixin(keras.Sequential):
    """
    参考: Training and Serving ML models with tf.keras  https://medium.com/tensorflow/training-and-serving-ml-models-with-tf-keras-fd975cc0fa27
    https://github.com/tensorflow/docs/blob/master/site/en/r2/tutorials/keras/basic_classification.ipynb
    https://www.tensorflow.org/guide/keras?hl=zh_cn
    注意：keras model subclass必须继承于超类keras.Sequential才能成功执行model_to_estimator()
    """
    @property
    def logits(self):
        return self._logits

    def __init__(self, layers=[], keras_inputs=None, keras_outputs=None):
        super().__init__()
        self._logits = None
        self._keras_inputs = keras_inputs
        self._keras_outputs = keras_outputs
        if keras_inputs is None or keras_outputs is None:
            self.add(layers)
        else:
            # TODO self._init_graph_network(inputs=keras_inputs, outputs=keras_outputs)
            pass

    def add(self, layers=[]):
        """add layer list"""
        self._layers += layers

    def call_layers(self, _x:tf.Tensor=None, name="prediction"):
        """_x: input layer tensor"""
        if self.layers is None or len(self.layers) < 1:
            return tf.constant(None)
        perdiction = self.layers[0](_x)
        for layer in self.layers[1:]:
            perdiction = layer(perdiction)
        self._logits = perdiction
        return self._logits

    def get_static_logits_output(self):
        if self._keras_outputs:
            return self._outputs
        else:
            last_layer = self._layers[0]
            for layer in self._layers[1:]:
                last_layer = layer(last_layer)
            return last_layer

    def get_static_first_input(self):
        if self._keras_inputs:
            return self._inputs
        else:
            return self._layers[0]

    def call(self, _x: tf.Tensor=None, training: bool=True) -> tf.Tensor:
        """Run the keras model layers."""
        # super().call(_x, training)
        return self.call_layers(_x)

