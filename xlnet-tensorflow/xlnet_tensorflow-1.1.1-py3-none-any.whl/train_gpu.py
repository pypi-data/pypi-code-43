"""Pretraining on GPUs."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os, sys
import math
import json
import time
import numpy as np

from absl import flags
import absl.logging as _logging  # pylint: disable=unused-import

import tensorflow as tf

from xlnet import data_utils, model_utils, function_builder
from xlnet.gpu_utils import assign_to_gpu, average_grads_and_vars

FLAGS = flags.FLAGS


def get_model_fn():
  def model_fn(features, labels, mems, is_training):
    #### Get loss from inputs
    total_loss, new_mems, monitor_dict = function_builder.get_loss(
        FLAGS, features, labels, mems, is_training)

    #### Check model parameters
    num_params = sum([np.prod(v.shape) for v in tf.trainable_variables()])
    tf.logging.info('#params: {}'.format(num_params))

    # GPU
    assert is_training
    all_vars = tf.trainable_variables()
    grads = tf.gradients(total_loss, all_vars)
    grads_and_vars = list(zip(grads, all_vars))

    return total_loss, new_mems, grads_and_vars

  return model_fn


def single_core_graph(is_training, features, mems):
  model_fn = get_model_fn()

  model_ret = model_fn(
      features=features,
      labels=None,
      mems=mems,
      is_training=is_training)

  return model_ret


def create_mems_tf(bsz_per_core):
  mems = [tf.placeholder(dtype=tf.float32,
                         shape=[FLAGS.mem_len, bsz_per_core, FLAGS.d_model])
          for layer in range(FLAGS.n_layer)]

  return mems


def initialize_mems_np(bsz_per_core):
  mems_np = [np.zeros(shape=[FLAGS.mem_len, bsz_per_core, FLAGS.d_model],
                      dtype=np.float32)
             for layer in range(FLAGS.n_layer)]

  return mems_np


def train(ps_device):
  ##### Get input function and model function

  train_input_fn, record_info_dict = data_utils.get_input_fn(
      tfrecord_dir=FLAGS.record_info_dir,
      split="train",
      bsz_per_host=FLAGS.train_batch_size,
      seq_len=FLAGS.seq_len,
      reuse_len=FLAGS.reuse_len,
      bi_data=FLAGS.bi_data,
      num_hosts=1,
      num_core_per_host=1, # set to one no matter how many GPUs
      perm_size=FLAGS.perm_size,
      mask_alpha=FLAGS.mask_alpha,
      mask_beta=FLAGS.mask_beta,
      uncased=FLAGS.uncased,
      num_passes=FLAGS.num_passes,
      use_bfloat16=FLAGS.use_bfloat16,
      num_predict=FLAGS.num_predict)

  # for key, info in record_info_dict.items():
  tf.logging.info("num of batches {}".format(record_info_dict["num_batch"]))

  ##### Create input tensors / placeholders
  bsz_per_core = FLAGS.train_batch_size // FLAGS.num_core_per_host

  params = {
      "batch_size": FLAGS.train_batch_size # the whole batch
  }
  train_set = train_input_fn(params)

  example = train_set.make_one_shot_iterator().get_next()

  if FLAGS.num_core_per_host > 1:
    examples = [{} for _ in range(FLAGS.num_core_per_host)]
    for key in example.keys():
      vals = tf.split(example[key], FLAGS.num_core_per_host, 0)
      for device_id in range(FLAGS.num_core_per_host):
        examples[device_id][key] = vals[device_id]
  else:
    examples = [example]

  ##### Create computational graph
  tower_mems, tower_losses, tower_new_mems, tower_grads_and_vars = [], [], [], []

  for i in range(FLAGS.num_core_per_host):
    reuse = True if i > 0 else None
    with tf.device(assign_to_gpu(i, ps_device)), \
        tf.variable_scope(tf.get_variable_scope(), reuse=reuse):

      # The mems for each tower is a dictionary
      mems_i = {}
      if FLAGS.mem_len:
        mems_i["mems"] = create_mems_tf(bsz_per_core)

      loss_i, new_mems_i, grads_and_vars_i = single_core_graph(
          is_training=True,
          features=examples[i],
          mems=mems_i)

      tower_mems.append(mems_i)
      tower_losses.append(loss_i)
      tower_new_mems.append(new_mems_i)
      tower_grads_and_vars.append(grads_and_vars_i)

  ## average losses and gradients across towers
  if len(tower_losses) > 1:
    loss = tf.add_n(tower_losses) / len(tower_losses)
    grads_and_vars = average_grads_and_vars(tower_grads_and_vars)
  else:
    loss = tower_losses[0]
    grads_and_vars = tower_grads_and_vars[0]

  ## get train op
  train_op, learning_rate, gnorm = model_utils.get_train_op(FLAGS, None,
      grads_and_vars=grads_and_vars)
  global_step = tf.train.get_global_step()

  ##### Training loop
  # initialize mems
  tower_mems_np = []
  for i in range(FLAGS.num_core_per_host):
    mems_i_np = {}
    for key in tower_mems[i].keys():
      mems_i_np[key] = initialize_mems_np(bsz_per_core)
    tower_mems_np.append(mems_i_np)

  saver = tf.train.Saver()

  gpu_options = tf.GPUOptions(allow_growth=True)

  model_utils.init_from_checkpoint(FLAGS, global_vars=True)

  with tf.Session(config=tf.ConfigProto(allow_soft_placement=True,
      gpu_options=gpu_options)) as sess:
    sess.run(tf.global_variables_initializer())

    fetches = [loss, tower_new_mems, global_step, gnorm, learning_rate, train_op]

    total_loss, prev_step = 0., -1
    while True:
      feed_dict = {}
      for i in range(FLAGS.num_core_per_host):
        for key in tower_mems_np[i].keys():
          for m, m_np in zip(tower_mems[i][key], tower_mems_np[i][key]):
            feed_dict[m] = m_np

      fetched = sess.run(fetches, feed_dict=feed_dict)

      loss_np, tower_mems_np, curr_step = fetched[:3]
      total_loss += loss_np

      if curr_step > 0 and curr_step % FLAGS.iterations == 0:
        curr_loss = total_loss / (curr_step - prev_step)
        tf.logging.info("[{}] | gnorm {:.2f} lr {:8.6f} "
            "| loss {:.2f} | pplx {:>7.2f}, bpc {:>7.4f}".format(
            curr_step, fetched[-3], fetched[-2],
            curr_loss, math.exp(curr_loss), curr_loss / math.log(2)))
        total_loss, prev_step = 0., curr_step

      if curr_step > 0 and curr_step % FLAGS.save_steps == 0:
        save_path = os.path.join(FLAGS.model_dir, "model.ckpt")
        saver.save(sess, save_path)
        tf.logging.info("Model saved in path: {}".format(save_path))

      if curr_step >= FLAGS.train_steps:
        break


def main(unused_argv):
  del unused_argv  # Unused

  tf.logging.set_verbosity(tf.logging.INFO)

  # Get corpus info
  FLAGS.n_token = data_utils.VOCAB_SIZE
  tf.logging.info("n_token {}".format(FLAGS.n_token))

  if not tf.gfile.Exists(FLAGS.model_dir):
    tf.gfile.MakeDirs(FLAGS.model_dir)

  train("/gpu:0")


if __name__ == "__main__":
  tf.app.run()
