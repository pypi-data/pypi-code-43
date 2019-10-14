# -*- coding: utf-8 -*-
import os
import math
import time
import tflex
import traceback
import numpy as np
import tensorflow as tf
from tensorflow.python.platform import tf_logging

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('tflex_file', 'models/resnet50/resnet50.tflex', "Directory to load the optimized model.",
                           short_name='t')
tf.app.flags.DEFINE_string('data_root', 'imagenet/val/', "Directory to load the imagenet validation dataset.",
                           short_name='d')
tf.app.flags.DEFINE_string('preprocessed_data_root', 'imagenet/imagenet_val_224_1000_resnet50.npy',
                           "Directory to load preprocessed imagenet validation dataset.",
                           short_name='p')
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


def execute_graph(sess, image_list, label_list, input_tensors, output_tensors, top_n=1):
    accuracy = 0.0
    img_list = []
    lab_list = []
    timings = []
    image_arrays = np.load(FLAGS.preprocessed_data_root)
    image_arrays = image_arrays[:10]

    nb_batches = int(math.ceil(float(len(image_arrays)) / FLAGS.batch_size))
    assert nb_batches * FLAGS.batch_size >= len(image_arrays)
    for batch in range(nb_batches):
        timings = []
        start = batch * FLAGS.batch_size
        end = min(len(image_arrays), start + FLAGS.batch_size)
        cur_batch_size = end - start

        img_list[:cur_batch_size] = image_arrays[start:end]
        lab_list[:cur_batch_size] = label_list[start:end]
        feed_dict = {input_tensors[0]: img_list}
        tstart = time.time()
        cur_corr_preds = sess.run(output_tensors[0], feed_dict=feed_dict)
        elapsed_time = time.time() - tstart
        if batch > 0:
            timings.append(elapsed_time)
        accuracy += equal(top_predictions(cur_corr_preds[:cur_batch_size], top_n, FLAGS.ids_are_one_indexed),
                          lab_list)
        print('time of %s batch is %.5f s' % (batch, elapsed_time))

    assert end >= len(image_arrays)
    accuracy /= len(image_arrays)
    return accuracy, timings


def main(_):
    tf_logging.set_verbosity(tf_logging.INFO)
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = '3'
    os.environ["TF_CPP_MIN_VLOG_LEVEL"] = '0'
    try:
        optimized_graph, input_arrays, output_arrays = tflex.utils.import_graph(FLAGS.tflex_file)
        optimized_graph = tflex.utils.set_device(optimized_graph, '/device:FPGA:1')

        input_tensors = tflex.utils.get_tensors(optimized_graph, input_arrays)
        output_tensors = tflex.utils.get_tensors(optimized_graph, output_arrays)
        print(input_tensors)
        print(output_tensors)
        sess1 = tf.Session(graph=optimized_graph)

        optimized_graph = tflex.utils.set_device(optimized_graph, '/device:FPGA:0')
        sess2 = tf.Session(graph=optimized_graph)
        # Load the data.
        image_list, label_list = prepare_sample_list(FLAGS.data_root)

        accuracy_1, timings_1 = execute_graph(sess1, image_list, label_list, input_tensors, output_tensors,
                                          FLAGS.top_n)
        accuracy_2, timings_2 = execute_graph(sess2, image_list, label_list, input_tensors, output_tensors,
                                          FLAGS.top_n)
        tf_logging.info(
            'Inference for %s and import successfully: Top %s Accuracy: %.5f , Average Time: %.5f s' % (
                FLAGS.tflex_file.split('/')[-1], FLAGS.top_n, accuracy_1, np.mean(timings_1)))
        tf_logging.info(
            'Inference for %s and import successfully: Top %s Accuracy: %.5f , Average Time: %.5f s' % (
                FLAGS.tflex_file.split('/')[-1], FLAGS.top_n, accuracy_2, np.mean(timings_2)))

    except Exception as e:
        traceback.print_exc()
        tf_logging.error('Inference for %s but failure : %s' % (FLAGS.tflex_file.split('/')[-1], e))


if __name__ == '__main__':
    tf.app.run()
