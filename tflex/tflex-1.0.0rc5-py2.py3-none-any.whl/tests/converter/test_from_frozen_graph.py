# -*- coding: utf-8 -*-
import tflex
import tensorflow as tf

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('frozen_model', 'models/resnet50/resnet50.pb', "Directory to load the frozen model.",
                           short_name='f')
tf.app.flags.DEFINE_string('input_arrays', 'input_1', "String of input node names.", short_name='i')
tf.app.flags.DEFINE_string('output_arrays', 'fc1000/Softmax', "String of output node names.", short_name='o')


def test_from_frozen_graph():
    input_arrays = []
    output_arrays = []
    for name in FLAGS.input_arrays.split(','):
        input_arrays.append(name)
    for name in FLAGS.output_arrays.split(','):
        output_arrays.append(name)
    converter = tflex.Converter.from_frozen_graph(FLAGS.frozen_graph_def,
                                                  input_arrays,
                                                  output_arrays)
    converter._print()


def main(_):
    # test from_frozen_graph() method.
    test_from_frozen_graph()


if __name__ == '__main__':
    tf.app.run()
