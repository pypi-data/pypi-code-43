"""Pretraining on TPUs."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from absl import app
from absl import flags
import absl.logging as _logging  # pylint: disable=unused-import

import numpy as np

import tensorflow as tf

from xlnet import model_utils, tpu_estimator, function_builder, data_utils

FLAGS = flags.FLAGS


def get_model_fn():
  """doc."""
  def model_fn(features, labels, mode, params):
    """doc."""
    #### Training or Evaluation
    is_training = (mode == tf.estimator.ModeKeys.TRAIN)
    assert is_training

    #### Retrieve `mems` from `params["cache"]`
    mems = {}
    idx = 0
    if FLAGS.mem_len > 0:
      mems["mems"] = params["cache"]

    #### Get loss from inputs
    total_loss, new_mems, monitor_dict = function_builder.get_loss(
        FLAGS, features, labels, mems, is_training)

    #### Turn `new_mems` into `new_cache`
    new_cache = []
    if FLAGS.mem_len > 0:
      new_cache += new_mems["mems"]

    #### Check model parameters
    num_params = sum([np.prod(v.shape) for v in tf.trainable_variables()])
    tf.logging.info("#params: {}".format(num_params))

    #### Configuring the optimizer
    train_op, learning_rate, gnorm = model_utils.get_train_op(
        FLAGS, total_loss)
    monitor_dict["lr"] = learning_rate
    monitor_dict["gnorm"] = gnorm

    #### Customized initial checkpoint
    scaffold_fn = model_utils.init_from_checkpoint(FLAGS, global_vars=True)

    #### Creating host calls
    host_call = function_builder.construct_scalar_host_call(
        monitor_dict=monitor_dict,
        model_dir=FLAGS.model_dir,
        prefix="train/",
        reduce_fn=tf.reduce_mean)

    #### Constucting training TPUEstimatorSpec with new cache.
    train_spec = tf.contrib.tpu.TPUEstimatorSpec(
        mode=mode, loss=total_loss, train_op=train_op, host_call=host_call,
        scaffold_fn=scaffold_fn)

    train_spec.cache = new_cache

    return train_spec

  return model_fn


def get_cache_fn(mem_len):
  """doc."""
  tf_float = tf.bfloat16 if FLAGS.use_bfloat16 else tf.float32
  def cache_fn(batch_size):
    mems = []
    if FLAGS.mem_len > 0:
      for _ in range(FLAGS.n_layer):
        zeros = tf.zeros(
            [mem_len, batch_size, FLAGS.d_model],
            dtype=tf_float)
        mems.append(zeros)

    return mems

  if mem_len > 0:
    return cache_fn
  else:
    return None


def get_input_fn(split):
  """doc."""
  assert split == "train"
  batch_size = FLAGS.train_batch_size

  input_fn, record_info_dict = data_utils.get_input_fn(
      tfrecord_dir=FLAGS.record_info_dir,
      split=split,
      bsz_per_host=batch_size // FLAGS.num_hosts,
      seq_len=FLAGS.seq_len,
      reuse_len=FLAGS.reuse_len,
      bi_data=FLAGS.bi_data,
      num_hosts=FLAGS.num_hosts,
      num_core_per_host=FLAGS.num_core_per_host,
      perm_size=FLAGS.perm_size,
      mask_alpha=FLAGS.mask_alpha,
      mask_beta=FLAGS.mask_beta,
      uncased=FLAGS.uncased,
      num_passes=FLAGS.num_passes,
      use_bfloat16=FLAGS.use_bfloat16,
      num_predict=FLAGS.num_predict)

  return input_fn, record_info_dict


def main(unused_argv):
  del unused_argv  # Unused

  tf.logging.set_verbosity(tf.logging.INFO)

  assert FLAGS.seq_len > 0
  assert FLAGS.perm_size > 0

  FLAGS.n_token = data_utils.VOCAB_SIZE
  tf.logging.info("n_token {}".format(FLAGS.n_token))

  if not tf.gfile.Exists(FLAGS.model_dir):
    tf.gfile.MakeDirs(FLAGS.model_dir)

  # Get train input function
  train_input_fn, train_record_info_dict = get_input_fn("train")

  tf.logging.info("num of batches {}".format(
      train_record_info_dict["num_batch"]))

  # Get train cache function
  train_cache_fn = get_cache_fn(FLAGS.mem_len)

  ##### Get model function
  model_fn = get_model_fn()

  ##### Create TPUEstimator
  # TPU Configuration
  run_config = model_utils.configure_tpu(FLAGS)

  # TPU Estimator
  estimator = tpu_estimator.TPUEstimator(
      model_fn=model_fn,
      train_cache_fn=train_cache_fn,
      use_tpu=FLAGS.use_tpu,
      config=run_config,
      params={"track_mean": FLAGS.track_mean},
      train_batch_size=FLAGS.train_batch_size,
      eval_on_tpu=FLAGS.use_tpu)

  #### Training
  estimator.train(input_fn=train_input_fn, max_steps=FLAGS.train_steps)


if __name__ == "__main__":
  app.run(main)
