# -*- coding: utf-8 -*-
import tflex
import argparse
import tensorflow as tf
import numpy as np
import os
import time
import cv2
# from keras.preprocessing import image
from imagenet_utils import decode_predictions, preprocess_input
from tensorflow.python.client import timeline

DEVICE_LOG = False
TENSORBOARD_LOG = False
TIMELINE_LOG = False
LOG_DIR = 'models/vgg19/log'


def main(_):
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = '3'
    os.environ["TF_CPP_MIN_VLOG_LEVEL"] = '0'
    optimized_graph, input_arrays, output_arrays = tflex.utils.import_graph(args.tflex_file)
    input_tensors = tflex.utils.get_tensors(optimized_graph, input_arrays)
    output_tensors = tflex.utils.get_tensors(optimized_graph, output_arrays)
    print(input_tensors)
    print(output_tensors)

    sess = tf.Session(graph=optimized_graph)

    if TENSORBOARD_LOG:
        tf.summary.FileWriter(LOG_DIR, sess.graph)
    if TIMELINE_LOG:
        run_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
        run_metadata = tf.RunMetadata()
    else:
        run_options = None
        run_metadata = None

    image_init = cv2.imread(args.image_file)
    img = cv2.resize(image_init, (input_tensors[0].shape[2], input_tensors[0].shape[1]))
    img = np.array(img, dtype=str(input_tensors[0].dtype).split("'")[1])
    img[:, :, 0] -= 103.94
    img[:, :, 1] -= 116.78
    img[:, :, 2] -= 123.68
    img_expanded = np.expand_dims(img, axis=0)
    print('Input image shape:', img_expanded.shape)
    #
    probs = sess.run(output_tensors[0], feed_dict={input_tensors[0]: img_expanded}, options=run_options,
                     run_metadata=run_metadata)

    print('Predicted:', decode_predictions(probs))

    if TIMELINE_LOG:
        tl = timeline.Timeline(run_metadata.step_stats)
        ctf = tl.generate_chrome_trace_format()
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        with open('%s/timeline.%.6f.json' % (LOG_DIR, time.time()), 'w') as f:
            f.write(ctf)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--tflex_file',
        type=str,
        default='models/resnet_101/resnet_101.tflex',
        help='Directory to load the .tflex file.'
    )
    parser.add_argument(
        '--image_file',
        type=str,
        default='cat.png'
    )
    args = parser.parse_args()
    tf.app.run()
