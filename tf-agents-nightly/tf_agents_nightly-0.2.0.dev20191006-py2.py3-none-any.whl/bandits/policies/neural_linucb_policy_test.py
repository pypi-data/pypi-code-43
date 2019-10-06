# coding=utf-8
# Copyright 2018 The TF-Agents Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for tf_agents.bandits.policies.neural_linucb_policy."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized
import numpy as np
import tensorflow as tf
from tf_agents.bandits.policies import neural_linucb_policy
from tf_agents.networks import network
from tf_agents.specs import tensor_spec
from tf_agents.trajectories import time_step as ts
from tf_agents.utils import common
from tf_agents.utils import test_utils
from tensorflow.python.framework import test_util  # pylint:disable=g-direct-tensorflow-import  # TF internal


_POLICY_VARIABLES_OFFSET = 10.0


class DummyNet(network.Network):

  def __init__(self, name=None, obs_dim=2, encoding_dim=10):
    super(DummyNet, self).__init__(name, (), 'DummyNet')
    self._layers.append(
        tf.keras.layers.Dense(
            encoding_dim,
            kernel_initializer=tf.compat.v1.initializers.constant(
                np.ones([obs_dim, encoding_dim])),
            bias_initializer=tf.compat.v1.initializers.constant(
                np.zeros([encoding_dim]))))

  def call(self, inputs, unused_step_type=None, network_state=()):
    inputs = tf.cast(inputs, tf.float32)
    for layer in self.layers:
      inputs = layer(inputs)
    return inputs, network_state


def get_reward_layer(num_actions=5, encoding_dim=10):
  return tf.keras.layers.Dense(
      num_actions,
      activation=None,
      kernel_initializer=tf.compat.v1.initializers.constant(
          np.ones([encoding_dim, num_actions])),
      bias_initializer=tf.compat.v1.initializers.constant(
          np.array(range(num_actions))))


def test_cases():
  return parameterized.named_parameters(
      {
          'testcase_name': '_batch1_numtrainsteps0',
          'batch_size': 1,
          'actions_from_reward_layer': False,
      }, {
          'testcase_name': '_batch4_numtrainsteps10',
          'batch_size': 4,
          'actions_from_reward_layer': True,
      })


@test_util.run_all_in_graph_and_eager_modes
class NeuralLinUCBPolicyTest(parameterized.TestCase, test_utils.TestCase):

  def setUp(self):
    super(NeuralLinUCBPolicyTest, self).setUp()
    self._obs_dim = 2
    self._obs_spec = tensor_spec.TensorSpec([self._obs_dim], tf.float32)
    self._time_step_spec = ts.time_step_spec(self._obs_spec)
    self._num_actions = 5
    self._alpha = 1.0
    self._action_spec = tensor_spec.BoundedTensorSpec(
        shape=(),
        dtype=tf.int32,
        minimum=0,
        maximum=self._num_actions - 1,
        name='action')
    self._encoding_dim = 10

  @property
  def _a(self):
    a_for_one_arm = 1.0 + 4.0 * tf.eye(self._encoding_dim, dtype=tf.float32)
    return [a_for_one_arm] * self._num_actions

  @property
  def _b(self):
    return [tf.constant(r * np.ones(self._encoding_dim), dtype=tf.float32)
            for r in range(self._num_actions)]

  @property
  def _num_samples_per_arm(self):
    a_for_one_arm = tf.constant([1], dtype=tf.float32)
    return [a_for_one_arm] * self._num_actions

  def _time_step_batch(self, batch_size):
    return ts.TimeStep(
        tf.constant(
            ts.StepType.FIRST, dtype=tf.int32, shape=[batch_size],
            name='step_type'),
        tf.constant(0.0, dtype=tf.float32, shape=[batch_size], name='reward'),
        tf.constant(1.0, dtype=tf.float32, shape=[batch_size], name='discount'),
        tf.constant(np.array(range(batch_size * self._obs_dim)),
                    dtype=tf.float32, shape=[batch_size, self._obs_dim],
                    name='observation'))

  @test_cases()
  def testBuild(self, batch_size, actions_from_reward_layer):
    policy = neural_linucb_policy.NeuralLinUCBPolicy(
        DummyNet(),
        self._encoding_dim,
        get_reward_layer(),
        actions_from_reward_layer=actions_from_reward_layer,
        cov_matrix=self._a,
        data_vector=self._b,
        num_samples=self._num_samples_per_arm,
        epsilon_greedy=0.0,
        time_step_spec=self._time_step_spec)

    self.assertEqual(policy.time_step_spec, self._time_step_spec)

  @test_cases()
  def testObservationShapeMismatch(self, batch_size, actions_from_reward_layer):
    policy = neural_linucb_policy.NeuralLinUCBPolicy(
        DummyNet(),
        self._encoding_dim,
        get_reward_layer(),
        actions_from_reward_layer=actions_from_reward_layer,
        cov_matrix=self._a,
        data_vector=self._b,
        num_samples=self._num_samples_per_arm,
        epsilon_greedy=0.0,
        time_step_spec=self._time_step_spec)

    current_time_step = ts.TimeStep(
        tf.constant(
            ts.StepType.FIRST, dtype=tf.int32, shape=[batch_size],
            name='step_type'),
        tf.constant(0.0, dtype=tf.float32, shape=[batch_size], name='reward'),
        tf.constant(1.0, dtype=tf.float32, shape=[batch_size], name='discount'),
        tf.constant(np.array(range(batch_size * (self._obs_dim + 1))),
                    dtype=tf.float32, shape=[batch_size, self._obs_dim + 1],
                    name='observation'))
    with self.assertRaisesRegexp(
        ValueError, r'Observation shape is expected to be \[None, 2\].'
        r' Got \[%d, 3\].' % batch_size):
      policy.action(current_time_step)

  @test_cases()
  def testActionBatch(self, batch_size, actions_from_reward_layer):

    policy = neural_linucb_policy.NeuralLinUCBPolicy(
        DummyNet(),
        self._encoding_dim,
        get_reward_layer(),
        actions_from_reward_layer=tf.constant(
            actions_from_reward_layer, dtype=tf.bool),
        cov_matrix=self._a,
        data_vector=self._b,
        num_samples=self._num_samples_per_arm,
        epsilon_greedy=0.0,
        time_step_spec=self._time_step_spec)

    action_step = policy.action(self._time_step_batch(batch_size=batch_size))
    self.assertEqual(action_step.action.dtype, tf.int32)
    self.evaluate(tf.compat.v1.global_variables_initializer())
    action_fn = common.function_in_tf1()(policy.action)
    action_step = action_fn(self._time_step_batch(batch_size=batch_size))
    actions_ = self.evaluate(action_step.action)
    self.assertAllGreaterEqual(actions_, self._action_spec.minimum)
    self.assertAllLessEqual(actions_, self._action_spec.maximum)

  @test_cases()
  def testActionBatchWithVariablesAndPolicyUpdate(
      self, batch_size, actions_from_reward_layer):

    a_list = []
    a_new_list = []
    b_list = []
    b_new_list = []
    num_samples_list = []
    num_samples_new_list = []
    for k in range(1, self._num_actions + 1):
      a_initial_value = k + 1 + 2 * k * tf.eye(
          self._encoding_dim, dtype=tf.float32)
      a_for_one_arm = tf.compat.v2.Variable(a_initial_value)
      a_list.append(a_for_one_arm)
      b_initial_value = tf.constant(
          k * np.ones(self._encoding_dim), dtype=tf.float32)
      b_for_one_arm = tf.compat.v2.Variable(b_initial_value)
      b_list.append(b_for_one_arm)
      num_samples_initial_value = tf.constant([1], dtype=tf.float32)
      num_samples_for_one_arm = tf.compat.v2.Variable(num_samples_initial_value)
      num_samples_list.append(num_samples_for_one_arm)

      # Variables for the new policy (they differ by an offset).
      a_new_for_one_arm = tf.compat.v2.Variable(
          a_initial_value + _POLICY_VARIABLES_OFFSET)
      a_new_list.append(a_new_for_one_arm)
      b_new_for_one_arm = tf.compat.v2.Variable(
          b_initial_value + _POLICY_VARIABLES_OFFSET)
      b_new_list.append(b_new_for_one_arm)
      num_samples_for_one_arm_new = tf.compat.v2.Variable(
          num_samples_initial_value + _POLICY_VARIABLES_OFFSET)
      num_samples_new_list.append(num_samples_for_one_arm_new)

    policy = neural_linucb_policy.NeuralLinUCBPolicy(
        encoding_network=DummyNet(),
        encoding_dim=self._encoding_dim,
        reward_layer=get_reward_layer(),
        actions_from_reward_layer=tf.constant(
            actions_from_reward_layer, dtype=tf.bool),
        cov_matrix=a_list,
        data_vector=b_list,
        num_samples=num_samples_list,
        epsilon_greedy=0.0,
        time_step_spec=self._time_step_spec)

    new_policy = neural_linucb_policy.NeuralLinUCBPolicy(
        encoding_network=DummyNet(),
        encoding_dim=self._encoding_dim,
        reward_layer=get_reward_layer(),
        actions_from_reward_layer=tf.constant(
            actions_from_reward_layer, dtype=tf.bool),
        cov_matrix=a_new_list,
        data_vector=b_new_list,
        num_samples=num_samples_new_list,
        epsilon_greedy=0.0,
        time_step_spec=self._time_step_spec)

    action_step = policy.action(self._time_step_batch(batch_size=batch_size))
    new_action_step = new_policy.action(
        self._time_step_batch(batch_size=batch_size))
    self.assertEqual(action_step.action.shape, new_action_step.action.shape)
    self.assertEqual(action_step.action.dtype, new_action_step.action.dtype)

    self.evaluate(tf.compat.v1.global_variables_initializer())
    self.evaluate(new_policy.update(policy))

    action_fn = common.function_in_tf1()(policy.action)
    action_step = action_fn(self._time_step_batch(batch_size=batch_size))
    new_action_fn = common.function_in_tf1()(new_policy.action)
    new_action_step = new_action_fn(
        self._time_step_batch(batch_size=batch_size))

    actions_, new_actions_ = self.evaluate(
        [action_step.action, new_action_step.action])
    self.assertAllEqual(actions_, new_actions_)


if __name__ == '__main__':
  tf.test.main()
