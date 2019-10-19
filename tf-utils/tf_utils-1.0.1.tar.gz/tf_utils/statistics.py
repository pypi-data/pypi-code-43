import numpy as np
import tensorflow as tf

from . import tf_utils as U


class TensorBoardSummary:
    writer = None

    def __init__(self, dir_name, scalar_keys=[], histogram_keys=[]):
        self.dir_name = dir_name
        if TensorBoardSummary.writer is None:
            TensorBoardSummary.writer = U.FileWriter(dir_name)
        self.scalar_keys = scalar_keys
        self.histogram_keys = histogram_keys
        self.scalar_summaries = []
        self.scalar_summaries_ph = []
        self.histogram_summaries_ph = []
        self.histogram_summaries = []
        with tf.variable_scope('summary'):
            for k in scalar_keys:
                ph = tf.placeholder('float32', None, name=k + '.scalar.summary')
                sm = tf.summary.scalar(k + '.scalar.summary', ph)
                self.scalar_summaries_ph.append(ph)
                self.scalar_summaries.append(sm)
            for k in histogram_keys:
                ph = tf.placeholder('float32', None, name=k + '.histogram.summary')
                sm = tf.summary.scalar(k + '.histogram.summary', ph)
                self.histogram_summaries_ph.append(ph)
                self.histogram_summaries.append(sm)
        try:
            self.summaries = tf.summary.merge(self.scalar_summaries + self.histogram_summaries)
        except ValueError:
            self.summaries = tf.summary.merge_all()

    def add_weights(self, weights, name_scope):
        """
        Adds weights from the list for the summary for each name_scope.
        Name scope should be in the name of the weight so the weight can be added to summary.
        For example: name_scope = ['kernel', 'bias']
        :param weights:
        :param name_scope:
        :return:
        """
        for v in weights:
            for ns in name_scope:
                if ns in v.name:
                    with tf.name_scope(ns):
                        self.variable_summaries(v)

    def variable_summaries(self, var):
        """
        Adds a summary of a single weight variable
        :param var:
        :return:
        """
        with tf.name_scope('summaries'):
            mean = tf.reduce_mean(var)
            tf.summary.scalar('mean', mean)
            with tf.name_scope('stddev'):
                stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
            tf.summary.scalar('stddev', stddev)
            tf.summary.scalar('max', tf.reduce_max(var))
            tf.summary.scalar('min', tf.reduce_min(var))
            tf.summary.histogram('histogram', var)

    def add_all_weights_summary(self, feed_dict, epoch):
        sess = U.get_session()
        summaries = sess.run(self.summaries, feed_dict)
        TensorBoardSummary.writer.add_summary(summaries, epoch)

    def add_all_summary(self, values, epoch):
        if np.sum(np.isnan(values) + 0) != 0:
            return
        sess = U.get_session()
        keys = self.scalar_summaries_ph + self.histogram_summaries_ph
        feed_dict = {}
        for k, v in zip(keys, values):
            feed_dict.update({k: v})
        summaries_str = sess.run(self.summaries, feed_dict)
        TensorBoardSummary.writer.add_summary(summaries_str, epoch)
