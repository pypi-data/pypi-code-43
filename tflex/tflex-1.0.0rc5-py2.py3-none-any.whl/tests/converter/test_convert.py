# -*- coding: utf-8 -*-
import tflex
import tensorflow as tf

FLAGS = tf.app.flags.FLAGS
FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('keras_model', '', "Directory to load the keras model.", short_name='k')
tf.app.flags.DEFINE_string('frozen_model', '', "Directory to load the frozen model.", short_name='f')
tf.app.flags.DEFINE_string('saved_model', '', "Directory to load the saved model.", short_name='s')
tf.app.flags.DEFINE_string('export_dir', 'models/model.tflex', "Directory to save the optimized graph.",
                           short_name='d')
tf.app.flags.DEFINE_string('input_arrays', 'input_1,input_2', "String of input node names.", short_name='i')
tf.app.flags.DEFINE_string('output_arrays', 'fc1000/Softmax', "String of output node names.", short_name='o')


def main(_):
    input_arrays = []
    output_arrays = []
    for name in FLAGS.input_arrays.split(','):
        input_arrays.append(name)
    for name in FLAGS.output_arrays.split(','):
        output_arrays.append(name)

    if FLAGS.keras_model:
        converter = tflex.Converter.from_keras_model(FLAGS.keras_model)
    elif FLAGS.frozen_model:
        converter = tflex.Converter.from_frozen_graph(FLAGS.frozen_model, input_arrays, output_arrays)
    elif FLAGS.saved_model:
        converter = tflex.Converter.from_saved_model(FLAGS.saved_model)
    else:
        raise Exception('keras_model or frozen_model or saved_model are required.')

    optimized_graph_def = converter.convert(FLAGS.export_dir)

    return optimized_graph_def


if __name__ == '__main__':
    tf.app.run()
