# -*- coding: utf-8 -*-
"""
bazel build tensorflow/python/tools:test_import_graph_get_tensors && \
bazel-bin/tensorflow/python/tools/test_import_graph_get_tensors \
    -f=models/resnet50/resnet50.tflex \
    2>&1 | tee logs/resnet50.log
"""

import tflex
import tensorflow as tf

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('tflex_file', 'models/resnet50/resnet50.tflex', "Directory to load the optimized model.",
                           short_name='t')


def test_import_graph():
    graph, input_arrays, output_arrays = tflex.utils.import_graph(FLAGS.tflex_file)

    return graph, input_arrays, output_arrays


def test_get_tensors(graph, tensor_names):
    tensors = tflex.utils.get_tensors(graph, tensor_names)
    print("The tensors of %s is: %s" % (tensor_names, tensors))
    return tensors


def main(_):
    graph, input_arrays, output_arrays = test_import_graph()

    test_get_tensors(graph, input_arrays)
    test_get_tensors(graph, output_arrays)


if __name__ == '__main__':
    tf.app.run()
