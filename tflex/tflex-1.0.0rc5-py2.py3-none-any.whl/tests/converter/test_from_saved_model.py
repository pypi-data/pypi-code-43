# -*- coding: utf-8 -*-
import tflex
import tensorflow as tf

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('saved_model', 'models/resnet50/', "Directory to load the saved model.", short_name='s')


def test_from_saved_model():
    converter = tflex.Converter.from_saved_model(FLAGS.saved_model)
    converter._print()


def main(_):
    # test from_saved_model() method.
    test_from_saved_model()


if __name__ == '__main__':
    tf.app.run()
