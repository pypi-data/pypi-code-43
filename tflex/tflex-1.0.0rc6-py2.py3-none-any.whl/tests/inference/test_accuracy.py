# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import ast
import math
import argparse
import numpy as np
import tensorflow as tf

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('frozen_model', 'models/resnet50/resnet50.pb', "Directory to load the optimized model.",
                           short_name='f')
tf.app.flags.DEFINE_string('data_root', 'imagenet/val/', "Directory to load the imagenet validation dataset.",
                           short_name='d')
tf.app.flags.DEFINE_string('preprocessed_data_root', 'imagenet/imagenet_val_224_1000_resnet50.npy',
                           "Directory to load preprocessed imagenet validation dataset.",
                           short_name='p')
tf.app.flags.DEFINE_string('input_arrays', 'input_1,input_2', "String of input node names.", short_name='i')
tf.app.flags.DEFINE_string('output_arrays', 'fc1000/Softmax', "String of output node names.", short_name='o')
tf.app.flags.DEFINE_integer('batch_size', '1', "The batch size will be baked into input placeholder.",
                            short_name='b')
tf.app.flags.DEFINE_integer('top_n', '1', "top n predicted class indices",
                            short_name='n')
tf.app.flags.DEFINE_boolean('ids_are_one_indexed', 'False',
                            "whether to increment passed IDs by 1 to account for the background category.",
                            short_name='id')


def prepare_sample_list(data_root):
    image_list = []
    label_list = []
    label = 0
    if os.path.isdir(data_root):
        for s in sorted(os.listdir(data_root)):
            newDir = os.path.join(data_root, s)
            for p in sorted(os.listdir(newDir)):
                image_list.append(os.path.join(newDir, p.split('/')[-1]))
                label_list.append(int(label))
            label += 1
    else:
        print('data_root need to be a direcctory !')

    return image_list, label_list


def execute_graph(sess, image_list, label_list, r_input, r_output, top_n=1):
    accuracy = 0.0
    img_list = []
    lab_list = []
    image_arrays = np.load(FLAGS.preprocessed_data_root)
    image_arrays = image_arrays[:100]
    nb_batches = int(math.ceil(float(len(image_arrays)) / FLAGS.batch_size))
    assert nb_batches * FLAGS.batch_size >= len(image_arrays)
    for batch in range(nb_batches):
        start = batch * FLAGS.batch_size
        end = min(len(image_arrays), start + FLAGS.batch_size)
        cur_batch_size = end - start

        img_list[:cur_batch_size] = image_arrays[start:end]
        lab_list[:cur_batch_size] = label_list[start:end]
        feed_dict = {r_input: img_list}

        cur_corr_preds = sess.run(r_output, feed_dict=feed_dict, options=None,
                                  run_metadata=None)
        accuracy += equal(top_predictions(cur_corr_preds[:cur_batch_size], top_n, FLAGS.ids_are_one_indexed),
                          lab_list)
        print('accuracy of %s batch is %.5f' % (batch, accuracy))

    assert end >= len(image_arrays)
    accuracy /= len(image_arrays)

    print('Top %s Accuracy: %.5f' % (top_n, accuracy))


def top_predictions(result, n, ids_are_one_indexed=False):
    """Get the top n predictions given the array of softmax results."""
    # We only care about the first example.
    ids_array = []
    for i in range(len(result)):
        probabilities = result[i]
        # Get the ids of most probable labels. Reverse order to get greatest first.
        ids = np.argsort(probabilities)[::-1]
        ids_array.append(ids[:n] - int(ids_are_one_indexed))
    print('predicted result id', ids_array)
    return ids_array


def equal(x, y):
    count = 0.0
    for i in range(len(x)):
        for id in x[i]:
            if id == y[i]:
                count += 1
                break
    print('The number of correctly predicted at each batch', count)
    return count


def main(_):
    input_arrays = []
    output_arrays = []
    for name in FLAGS.input_arrays.split(','):
        input_arrays.append(name)
    for name in FLAGS.output_arrays.split(','):
        output_arrays.append(name)
    graph = tf.Graph()
    with graph.as_default():
        graph_def = tf.GraphDef()
        with tf.gfile.GFile(FLAGS.frozen_model, 'rb') as fid:
            serialized_graph = fid.read()
            graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(graph_def)
        r_input = graph.get_tensor_by_name('import/' + input_arrays[0] + ':0')
        r_output = graph.get_tensor_by_name('import/' + output_arrays[0] + ':0')
        print(r_input)
        print(r_output)

    sess = tf.Session(graph=graph)
    # Load the data.
    image_list, label_list = prepare_sample_list(FLAGS.data_root)
    # Inference
    execute_graph(sess, image_list, label_list, r_input, r_output, FLAGS.top_n)


if __name__ == '__main__':
    tf.app.run()
