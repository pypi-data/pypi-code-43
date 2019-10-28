# -*- coding: utf-8 -*-
import tensorflow as tf
from tensorflow_estimator import estimator  # estimator import方便查看源代码
from tensorflow.python import feature_column  # feature_column import方便查看源代码


class EstimatorModelMixin(estimator.Estimator):
    """
    tensorflow estimator
    """
    @property
    def layers(self):
        return self._layers

    @property
    def estimator_model_fn(self):
        return self._estimator_model_fn

    @property
    def logits(self):
        return self._logits

    def __init__(self, layers=[], model_fn=None, params=None):
        self._layers = []
        self._logits = None
        if model_fn:
            self._estimator_model_fn = model_fn
        else:
            self.add(layers)
            self._estimator_model_fn = self.build_in_model_fn
        super().__init__(model_fn=self._estimator_model_fn, params=params)

    def build_in_model_fn(self, features, labels, mode, params)->estimator.EstimatorSpec:
        """
        build default model_fn
        :param features: i.e. _x->tf.tensor
        :param labels: i.e. _y->tf.tensor
        :param mode:
        :param params: e.g.
        params={
            'feature_columns': my_feature_columns,
            'hidden_units': [10, 10],
            'n_classes': 3
        }
        :return:
        """
        self.call_layers(features)
        if mode == estimator.ModeKeys.PREDICT:
            predictions = {
                'probabilities': tf.nn.softmax(self.logits),
                'logits': self.logits,
            }
            return estimator.EstimatorSpec(mode, predictions=predictions)

        # Compute predictions.
        predicted_classes = tf.argmax(self.logits, 1)
        # Compute loss.
        loss = tf.compat.v1.losses.sparse_softmax_cross_entropy(labels=labels, logits=self.logits)
        # Compute evaluation metrics.
        accuracy = tf.compat.v1.metrics.accuracy(labels=labels,
                                                 predictions=predicted_classes,
                                                 name='acc_op')
        metrics = {'accuracy': accuracy}
        tf.summary.scalar('accuracy', accuracy[1])
        if mode == estimator.ModeKeys.EVAL:
            return estimator.EstimatorSpec(
                mode, loss=loss, eval_metric_ops=metrics)
        # Create training op.
        assert mode == estimator.ModeKeys.TRAIN
        optimizer = tf.compat.v1.train.AdagradOptimizer(learning_rate=0.1)
        train_op = optimizer.minimize(loss, global_step=tf.compat.v1.train.get_global_step())
        return estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)

    def _call_model_fn(self, features, labels, mode, params)->estimator.EstimatorSpec:
        """Calls model function.

        Args:
          features: features dict.
          labels: labels dict.
          mode: `tf.estimator.ModeKeys`
          config: `tf.estimator.RunConfig`

        Returns:
          An `tf.estimator.EstimatorSpec` object.
        """
        return super()._call_model_fn(features, labels, mode, params)

    def add(self, layers=[]):
        """add layer list"""
        if layers:
            self._layers += layers

    def call_layers(self, _x: tf.Tensor=None, name="prediction"):
        """
        call layers
        :param _x:
        :param name:
        :return:
        """
        if self.layers is None or len(self.layers) < 1:
            return tf.constant(None)
        perdiction = self.layers[0](_x)
        for layer in self.layers[1:]:
            perdiction = layer(perdiction)
        self._logits = perdiction
        return self._logits

    def get_static_logits_output(self):
        last_layer = self._layers[0]
        for layer in self._layers[1:]:
            last_layer = layer(last_layer)
        return last_layer

    def get_static_first_input(self):
        return self._layers[0]

