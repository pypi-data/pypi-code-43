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

import os

import numpy as np
import tensorflow as tf

from tensorforce.agents.policy_agent import PolicyAgent
from tensorforce.execution import Runner
from tensorforce.environments import OpenAIGym


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(v=tf.logging.ERROR)


def main():
    # Create an OpenAI-Gym environment
    environment = OpenAIGym('CartPole-v1')

    # Create the agent
    agent = PolicyAgent(
        states=environment.states(), actions=environment.actions(), max_episode_timesteps=200,
        # Model
        exploration=0.0, variable_noise=0.0,
        # MemoryModel
        memory=None, update=dict(unit='episodes', batch_size=30, frequency=10, sequence_length=8),
        # optimizer=dict(type='adam', learning_rate=1e-3),
        optimizer=dict(
            type='multi_step', optimizer=dict(type='adam', learning_rate=1e-3), num_steps=5
        ),
        # optimizer=dict(
        #     type='multi_step', num_steps=10, optimizer=dict(
        #         type='subsampling_step', fraction=0.33, optimizer=dict(
        #             type='adam', learning_rate=1e-3
        #         )
        #     )
        # ),
        # PolicyModel
        policy=None, network=dict(type='auto', internal_rnn=True),
        objective=dict(type='policy_gradient', ratio_based=True, clipping_value=0.2),
        reward_estimation=dict(
            horizon=20, discount=0.99, estimate_horizon='late', estimate_actions=False,
            estimate_terminal=True, estimate_advantage=False
        ),
        entropy_regularization=0.0,
        baseline_policy=None, baseline_network='auto',
        baseline_objective='state_value',
        # baseline_objective='same',
        baseline_optimizer=dict(type='adam', learning_rate=1e-3)
        # baseline_optimizer='same'
        # baseline_optimizer=dict(
        #     type='multi_step', optimizer=dict(type='adam', learning_rate=3e-3), num_steps=5
        # )
    )

    # Initialize the runner
    runner = Runner(agent=agent, environment=environment)

    def callback(r):
        if r.episode % 100 == 0:
            print('{}/{}'.format(
                float(np.mean(r.episode_rewards[-100:])),
                sum(reward == 200.0 for reward in r.episode_rewards[-100:])
            ), end=' ', flush=True)

    # Start the runner
    runner.run(num_episodes=2000, max_episode_timesteps=200, callback=callback, use_tqdm=False)
    runner.close()
    print()


if __name__ == '__main__':
    main()
