import random

import numpy as np
import scipy.signal
import tensorflow as tf

seed = 1
random.seed(seed)
np.random.seed(seed)
tf.set_random_seed(seed)
DTYPE = tf.float32


def discount(x, gamma):
    assert x.ndim >= 1
    return scipy.signal.lfilter([1], [1, -gamma], x[::-1], axis=0)[::-1]


def gauss_prob_val(mu, logstd, x):
    std = np.exp(logstd)
    var = np.square(std)
    gp = np.exp(-np.square(x - mu) / (2 * var)) / ((2 * np.pi) ** .5 * std)
    return np.prod(gp, axis=1)


def gauss_prob(mu, logstd, x):
    std = tf.exp(logstd)
    var = tf.square(std)
    gp = tf.exp(-tf.square(x - mu) / (2 * var)) / ((2 * np.pi) ** .5 * std)
    return tf.reduce_prod(gp, [1])


def gauss_log_prob(mu, logstd, x):
    var = tf.exp(2 * logstd)
    gp = -tf.square(x - mu) / (2 * var) - .5 * tf.log(tf.constant(2 * np.pi)) - logstd
    return tf.reduce_sum(gp, [1])


def gauss_selfKL_firstfixed(mu, logstd):
    mu1, logstd1 = map(tf.stop_gradient, [mu, logstd])
    mu2, logstd2 = mu, logstd
    return gauss_KL(mu1, logstd1, mu2, logstd2)


def gauss_KL(mu1, logstd1, mu2, logstd2):
    var1 = tf.exp(2 * logstd1)
    var2 = tf.exp(2 * logstd2)
    kl = tf.reduce_sum(logstd2 - logstd1 + (var1 + tf.square(mu1 - mu2)) / (2 * var2) - 0.5)
    return kl


def gauss_ent(mu, logstd):
    h = tf.reduce_sum(logstd + tf.constant(0.5 * np.log(2 * np.pi * np.e), tf.float32))
    return h


def gauss_sample(mu, logstd):
    return mu + tf.exp(logstd) * tf.random_normal(tf.shape(logstd))


def CategoricalPD_sample(logits):
    u = tf.random_uniform(tf.shape(logits))
    return tf.argmax(logits - tf.log(-tf.log(u)), axis=-1)

#
# def var_shape(x):
#     out = [k.value for k in x.get_shape()]
#     assert all(isinstance(a, int) for a in out), \
#         "shape function assumes that shape is fully known"
#     return out

#
# def numel(x):
#     return np.prod(var_shape(x))
#
#
# def flatgrad(loss, var_list):
#     grads = tf.gradients(loss, var_list)
#     reshaped = [tf.reshape(grad, [numel(v)]) for (v, grad) in zip(var_list, grads)]
#     return tf.concat(reshaped, 0)
#
#
# def intprod(x):
#     return int(np.prod(x))

#
# class SetFromFlat(object):
#     def __init__(self, var_list, dtype=tf.float32):
#         shapes = list(map(var_shape, var_list))
#         total_size = np.sum([intprod(shape) for shape in shapes])
#
#         self.theta = theta = tf.placeholder(dtype, [total_size])
#         start = 0
#         assigns = []
#         for (shape, v) in zip(shapes, var_list):
#             size = intprod(shape)
#             assigns.append(tf.assign(v, tf.reshape(theta[start:start + size], shape)))
#             start += size
#         self.op = tf.group(*assigns)
#
#     def __call__(self, theta):
#         get_session().run(self.op, feed_dict={self.theta: theta})
#
#
# class GetFlat(object):
#     def __init__(self, var_list):
#         self.op = tf.concat(values=[tf.reshape(v, [numel(v)]) for v in var_list], axis=0)
#
#     def __call__(self):
#         return get_session().run(self.op)

