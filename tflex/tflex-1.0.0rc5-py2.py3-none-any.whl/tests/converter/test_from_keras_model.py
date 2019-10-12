# -*- coding: utf-8 -*-
import tflex
import argparse
import tensorflow as tf

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('keras_model', 'models/resnet50/resnet50.h5', "Directory to load the keras model.",
                           short_name='k')


def test_from_keras_model():
    converter = tflex.Converter.from_keras_model(FLAGS.keras_model)
    converter._print()


def main(_):
    # test from_keras_model() method.
    test_from_keras_model()


if __name__ == '__main__':
    tf.app.run()
