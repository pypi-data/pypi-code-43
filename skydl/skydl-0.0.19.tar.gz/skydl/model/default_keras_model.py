# -*- coding: utf-8 -*-
import tensorflow as tf
import tensorflow_datasets as tfds
import numpy as np
from skydl.model.default_keras_net import DefaultKerasNet
from skydl.model.default_model import DefaultModel
from tensorflow.python import keras  # 或from tensorflow import keras
from tensorflow_estimator import estimator  # estimator import方便查看源代码


class DefaultKerasModel(DefaultModel):
    """
    default keras model implements
    find a issue: Unable to use FeatureColumn with Keras Functional API #27416  https://github.com/tensorflow/tensorflow/issues/27416
    """
    @property
    def model(self)->keras.Sequential:
        """定义keras.Model返回值类型便于IDE找到对应的静态类"""
        return self._model

    def __init__(self, name=None, keras_layers=[], keras_inputs=None, keras_outputs=None, loss=None, optimizer=None, metrics=None, weights=None):
        self._keras_layers = keras_layers
        self._keras_inputs = keras_inputs
        self._keras_outputs = keras_outputs
        super().__init__(name=name, loss=loss, optimizer=optimizer, metrics=metrics, weights=weights)

    def build_network(self):
        return DefaultKerasNet(self.name if self.name else self.__class__.__name__, self.parser_args,
                               self._keras_layers, keras_inputs=self._keras_inputs, keras_outputs=self._keras_outputs)

    def load_data(self, *args, **kwargs):
        # return batched_train_dataset, batched_validation_dataset, batched_evaluate_dataset
        pass

    def compile(self, loss=keras.losses.sparse_categorical_crossentropy, optimizer=keras.optimizers.Adam(), metrics=["accuracy"]):
        if not self.is_training_phase() and not self.is_evaluation_phase():
            return self
        # with self.distribute_strategy.scope():  报错 ValueError: We currently do not support distribution strategy with a `Sequential` model that is created without `input_shape`/`input_dim` set in its first layer or a subclassed model.
        # with self.distribute_strategy.scope():
        self.loss = loss
        self.optimizer = optimizer
        self.metrics = metrics
        super().compile(loss=self.loss, optimizer=self.optimizer, metrics=self.metrics)
        # restore weights from latest checkpoint
        latest_checkpoint = tf.train.latest_checkpoint(self.get_model_checkpoint_dir())
        if latest_checkpoint:
            self.model.get_proxy().load_weights(latest_checkpoint)
            self.log.info("already called load_weights from: " + latest_checkpoint)
        self.model.get_proxy().compile(optimizer=self.optimizer,
                               loss=self.loss,
                               metrics=self.metrics)
        return self

    def model_to_estimator(self, keras_model_path=None,
                           custom_objects=None,
                           model_dir=None,
                           config=None) -> estimator.Estimator:
        """
        从编译的Keras模型创建Estimator，需要调用model_to_estimator方法
        注意：
        需要先执行compile()
        keras model subclass必须继承于超类keras.Sequential才能成功执行model_to_estimator()
        :return: estimator
        """
        # config = tf.estimator.RunConfig(train_distribute=self.distribute_strategy) # 报错：ValueError: Only TensorFlow native optimizers are supported with DistributionStrategy.
        # estimator = tf.keras.estimator.model_to_estimator(self.model, config=config)
        return keras.estimator.model_to_estimator(keras_model=self.model,
                                                   keras_model_path=keras_model_path,
                                                   custom_objects=custom_objects,
                                                   model_dir=model_dir,
                                                   config=config)

    def fit_callbacks(self):
        """
        keras fit callbacks
        :return:
        """
        # Function for decaying the learning rate.
        # You can define any decay function you need.
        def decay(epoch):
            if epoch < 3:
                return 1e-3
            elif 3 <= epoch < 7:
                return 1e-4
            else:
                return 1e-5

        class PrintLR(tf.keras.callbacks.Callback):
            def on_epoch_end(self, epoch, logs=None):
                print('\nLearning rate for epoch {} is {}'.format(epoch+1, self.model.optimizer.lr.numpy()))  # this self is inner class self, so no need set self.model.get_proxy()
        callbacks = [
            tf.keras.callbacks.TensorBoard(log_dir='./logs', histogram_freq=0, write_graph=True, write_images=True),
            keras.callbacks.ModelCheckpoint(self.get_model_checkpoint_dir() + "/" + self.latest_model_filename,
                                            verbose=1,
                                            save_weights_only=True),
            keras.callbacks.LearningRateScheduler(decay),
            PrintLR()
        ]
        return callbacks

    def fit(self, *args, **kwargs):
        return self

    def evaluate(self, *args, **kwargs):
        return self

    def serving(self, *args, **kwargs):
        # restore weights from latest checkpoint
        latest_checkpoint = tf.train.latest_checkpoint(self.get_model_checkpoint_dir())
        if latest_checkpoint:
            self.model.get_proxy().load_weights(latest_checkpoint)
            self.log.info("already called load_weights from: " + latest_checkpoint)
        saved_serving_path = self.parser_args.model_checkpoint_path + "/serving/models/" + self.model.name() + "/" + self.parser_args.model_version

        _, evaluate_dataset, _ = self.load_data()
        # prediction mode
        for batched_examples in tfds.as_numpy(evaluate_dataset.take(1)):
            test_batched_features, test_batched_labels = batched_examples
        predictions = self.model.get_proxy().predict(test_batched_features)
        print("serving predict, real:", np.argmax(predictions[0]), test_batched_labels[0])

        # save model for tf serving
        if not self.model.get_proxy().inputs:
            for batched_examples in tfds.as_numpy(evaluate_dataset.take(1)):
                test_batched_features, test_batched_labels = batched_examples
                self.model.get_proxy()._set_inputs(test_batched_features)
        tf.saved_model.save(self.model.get_proxy(), saved_serving_path)
        return self

    def predict(self, *args, **kwargs):
        """python版的预测接口，返回预测结果"""
        return None

