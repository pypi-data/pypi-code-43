# Copyright 2018 Tensorforce Team. All Rights Reserved.
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
# ==============================================================================

from collections import OrderedDict

import tensorflow as tf

from tensorforce import TensorforceError, util
from tensorforce.core import parameter_modules
from tensorforce.core.utils import CircularBuffer


class DiscountedSum(CircularBuffer):

    def __init__(
        self, name, values_spec, horizon, discount, baseline_estimate, estimate_horizon,
        estimate_terminal, capacity=None, summary_labels=None
    ):
        if capacity is None:
            if not isinstance(horizon, int):
                raise TensorforceError.unexpected()
            capacity = horizon

        super().__init__(
            name=name, values_spec=values_spec, capacity=capacity, return_overwritten=True,
            summary_labels=summary_labels
        )

        # Horizon
        self.horizon = self.add_module(
            name='horizon', module=horizon, modules=parameter_modules, dtype='long'
        )

        # Discount
        self.discount = self.add_module(
            name='discount', module=discount, modules=parameter_modules
        )

        # Baseline estimate
        self.baseline_estimate = baseline_estimate

        # Estimate horizon
        self.estimate_horizon = estimate_horizon

        # Estimate terminal
        self.estimate_terminal = estimate_terminal

    def tf_reset(self, baseline=None):
        values = super().tf_reset()

        # Constants and parameters
        zero = tf.constant(value=0, dtype=util.tf_dtype(dtype='long'))
        one = tf.constant(value=1, dtype=util.tf_dtype(dtype='long'))
        horizon = self.horizon.value()
        discount = self.discount.value()

        assertions = list()
        # Check whether exactly one terminal, unless empty
        # assertions.append(
        #     tf.debugging.assert_equal(
        #         x=tf.count_nonzero(
        #             input_tensor=values['terminal'], dtype=util.tf_dtype(dtype='int')
        #         ),
        #         y=tf.constant(value=1, dtype=util.tf_dtype(dtype='int'))
        #     )
        # )
        # Check whether last value is terminal
        # assertions.append(
        #     tf.debugging.assert_equal(
        #         x=values['terminal'][-1],
        #         y=tf.constant(value=True, dtype=util.tf_dtype(dtype='bool'))
        #     )
        # )

        # Get number of values
        with tf.control_dependencies(control_inputs=assertions):
            value = values['terminal']
            num_values = tf.shape(input=value, out_type=util.tf_dtype(dtype='long'))[0]

            # Expand rewards beyond terminal
            terminal_zeros = tf.zeros(shape=(horizon,), dtype=util.tf_dtype(dtype='float'))
            rewards = tf.concat(values=(values['reward'], terminal_zeros), axis=0)

        # Horizon baseline value
        if self.estimate_horizon:
            # Baseline estimate
            states = OrderedDict()
            for name, state in values['states'].items():
                states[name] = state[horizon:]
            baseline_internals = OrderedDict()
            for name, internal in values['internals'].items():
                if name.startswith('baseline-'):
                    baseline_internals[name[9:]] = internal[horizon:]
            if self.baseline_estimate == 'state':
                horizon_estimate = baseline.states_value(
                    states=states, internals=baseline_internals
                )
            elif self.baseline_estimate == 'action':
                actions = values['actions'][horizon:]
                horizon_estimate = baseline.actions_value(
                    states=states, internals=baseline_internals, actions=actions
                )
            if self.estimate_terminal:
                terminal_estimate = horizon_estimate[-1]
                terminal_estimate = tf.fill(dims=(horizon,), value=terminal_estimate)
            else:
                terminal_estimate = terminal_zeros
            horizon_estimate = tf.concat(values=(horizon_estimate, terminal_estimate), axis=0)

        else:
            # Zero estimate
            horizon_estimate = tf.zeros(shape=(num_values,), dtype=util.tf_dtype(dtype='float'))

        # Calculate discounted sum
        def cond(discounted_sum, horizon):
            return tf.math.greater_equal(x=horizon, y=zero)

        def body(discounted_sum, horizon):
            # discounted_sum = tf.Print(discounted_sum, (horizon, discounted_sum, rewards[horizon:]), summarize=10)
            discounted_sum = discount * discounted_sum
            discounted_sum = discounted_sum + rewards[horizon: horizon + num_values]
            return discounted_sum, horizon - one

        values['reward'] = self.while_loop(
            cond=cond, body=body, loop_vars=(horizon_estimate, horizon), back_prop=False
        )[0]

        return values

    def tf_enqueue(self, baseline=None, **values):
        # Constants and parameters
        zero = tf.constant(value=0, dtype=util.tf_dtype(dtype='long'))
        one = tf.constant(value=1, dtype=util.tf_dtype(dtype='long'))
        capacity = tf.constant(value=self.capacity, dtype=util.tf_dtype(dtype='long'))
        horizon = self.horizon.value()
        discount = self.discount.value()

        assertions = list()
        # Check whether horizon at most capacity
        assertions.append(tf.debugging.assert_less_equal(x=horizon, y=capacity))
        # Check whether at most one terminal
        assertions.append(
            tf.debugging.assert_less_equal(
                x=tf.count_nonzero(
                    input_tensor=values['terminal'], dtype=util.tf_dtype(dtype='int')
                ),
                y=tf.constant(value=1, dtype=util.tf_dtype(dtype='int'))
            )
        )
        # Check whether, if any, last value is terminal
        assertions.append(
            tf.debugging.assert_equal(
                x=tf.reduce_any(input_tensor=values['terminal']), y=values['terminal'][-1]
            )
        )

        # # Discount mask
        # exponents = tf.range(limit=(horizon + one), dtype=util.tf_dtype(dtype='float'))
        # discounted_mask = tf.math.pow(x=discount, y=exponents)

        # Get number of overwritten values
        with tf.control_dependencies(control_inputs=assertions):
            value = values['terminal']
            num_values = tf.shape(input=value, out_type=util.tf_dtype(dtype='long'))[0]
            start = tf.maximum(x=self.buffer_index, y=capacity)
            limit = tf.maximum(x=(self.buffer_index + num_values), y=capacity)
            num_overwritten = limit - start

        def update_overwritten_rewards():
            # Get relevant buffer rewards
            buffer_limit = self.buffer_index + tf.minimum(
                x=(num_overwritten + horizon + one), y=capacity
            )
            buffer_indices = tf.range(start=self.buffer_index, limit=buffer_limit)
            buffer_indices = tf.mod(x=buffer_indices, y=capacity)
            rewards = tf.gather(params=self.buffers['reward'], indices=buffer_indices)

            # Get relevant values rewards
            values_limit = tf.maximum(x=(num_overwritten + horizon + one - capacity), y=zero)
            rewards = tf.concat(values=(rewards, values['reward'][:values_limit]), axis=0)
            rewards = rewards[:-1]

            # Horizon baseline value
            if self.estimate_horizon:
                # Baseline estimate
                buffer_indices = buffer_indices[horizon + one:]
                states = OrderedDict()
                for name, buffer in self.buffers['states'].items():
                    state = tf.gather(params=buffer, indices=buffer_indices)
                    states[name] = tf.concat(
                        values=(state, values['states'][name][:values_limit]), axis=0
                    )
                baseline_internals = OrderedDict()
                for name, buffer in self.buffers['internals'].items():
                    if name.startswith('baseline-'):
                        internal = tf.gather(params=buffer, indices=buffer_indices)
                        baseline_internals[name[9:]] = tf.concat(
                            values=(internal, values['internals'][name][:values_limit]), axis=0
                        )
                if self.baseline_estimate == 'state':
                    horizon_estimate = baseline.states_value(
                        states=states, internals=baseline_internals
                    )
                elif self.baseline_estimate == 'action':
                    actions = OrderedDict()
                    for name, buffer in self.buffers['actions'].items():
                        action = tf.gather(params=buffer, indices=buffer_indices)
                        actions[name] = tf.concat(
                            values=(action, values['actions'][name][:values_limit]), axis=0
                        )
                    horizon_estimate = baseline.actions_value(
                        states=states, internals=baseline_internals, actions=actions
                    )

            else:
                # Zero estimate
                horizon_estimate = tf.zeros(
                    shape=(num_overwritten,), dtype=util.tf_dtype(dtype='float')
                )

            # Calculate discounted sum
            def cond(discounted_sum, horizon):
                return tf.math.greater_equal(x=horizon, y=zero)

            def body(discounted_sum, horizon):
                # discounted_sum = tf.Print(discounted_sum, (horizon, discounted_sum, rewards[horizon:]), summarize=10)
                discounted_sum = discount * discounted_sum
                discounted_sum = discounted_sum + rewards[horizon: horizon + num_overwritten]
                return discounted_sum, horizon - one

            discounted_sum = self.while_loop(
                cond=cond, body=body, loop_vars=(horizon_estimate, horizon), back_prop=False
            )[0]

            # Overwrite buffer rewards
            indices = tf.range(
                start=self.buffer_index, limit=(self.buffer_index + num_overwritten)
            )
            indices = tf.mod(x=indices, y=capacity)
            indices = tf.expand_dims(input=indices, axis=1)
            assignment = self.buffers['reward'].scatter_nd_update(
                indices=indices, updates=discounted_sum
            )

            with tf.control_dependencies(control_inputs=(assignment,)):
                return util.no_operation()

        any_overwritten = tf.math.greater(x=num_overwritten, y=zero)
        updated_rewards = self.cond(
            pred=any_overwritten, true_fn=update_overwritten_rewards, false_fn=util.no_operation
        )

        with tf.control_dependencies(control_inputs=(updated_rewards,)):
            return super().tf_enqueue(**values)


    # def tf_enqueue(self, values):
    #     # Constants and parameters
    #     zero = tf.constant(value=0, dtype=util.tf_dtype(dtype='long'))
    #     one = tf.constant(value=1, dtype=util.tf_dtype(dtype='long'))
    #     capacity = tf.constant(value=self.capacity, dtype=util.tf_dtype(dtype='long'))
    #     horizon = self.horizon.value()
    #     discount = self.discount.value()
    #     with_baseline = one if self.baseline else zero

    #     # Discounted mask
    #     exponents = tf.range(limit=(horizon + one), dtype=util.tf_dtype(dtype='float'))
    #     discounted_mask = tf.math.pow(x=discount, y=exponents)

    #     # Get number of values
    #     value = next(iter(values.values()))
    #     num_values = tf.shape(input=value, out_type=util.tf_dtype(dtype='long'))[0]

    #     # Update buffer rewards
    #     def cond(index, ...):
    #         return index > 0

    #     def body(n, ...):
    #         # Future buffer reward indices
    #         buffer_start = self.buffer_index + n
    #         buffer_limit = self.buffer_index + tf.minimum(x=(n + one + horizon), y=capacity)
    #         buffer_indices = tf.range(start=buffer_start, limit=buffer_limit)
    #         buffer_indices = tf.mod(x=buffer_indices, y=capacity)

    #         # Get future buffer rewards
    #         with tf.control_dependencies(control_inputs=(buffer_indices,)):
    #             buffer_rewards = tf.gather(params=self.buffers['reward'], indices=buffer_indices)

    #         # Future values reward indices
    #         with tf.control_dependencies(control_inputs=(buffer_rewards,)):
    #         values_start = zero
    #         values_limit = tf.maximum(x=(n + one + horizon - capacity), y=zero)
    #         values_indices = tf.range(start=values_start, limit=values_limit)

    #         # Get future values rewards
    #         with tf.control_dependencies(control_inputs=(values_indices,)):
    #             values_rewards = tf.gather(params=values['reward'], indices=values_indices)

    #         # Baseline
    #         with tf.control_dependencies(control_inputs=(values_rewards,)):
    #             if self.baseline is None:
    #                 rewards = tf.concat(values=(buffer_rewards, values_rewards), axis=0)
    #             else:
    #                 self.cond(pred=(limit > zero), true_fn=(lambda: values['states'][values_limit], false_fn=(lambda: self.buffers['states'][buffer_limit])
    #                 rewards = tf.concat(values=(buffer_rewards, values_rewards, baseline_value), axis=0)

    #         # Write estimated reward
    #         with tf.control_dependencies(control_inputs=(rewards,)):
    #             index = tf.mod(x=(self.buffer_index + n), y=capacity)
    #             discounted_sum = tf.reduce_sum(input_tensor=(rewards * discounted_mask), axis=0)
    #             assignment = self.buffers['reward'].scatter_nd_update(
    #                 indices=[index], updates=discounted_sum
    #             )

    #     self.while_loop(
    #         cond=util.always_true,
    #         body=body,
    #     max_iterations=num_values)

    #     return super().tf_enqueue(values=values)
