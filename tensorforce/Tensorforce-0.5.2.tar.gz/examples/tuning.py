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

import argparse
import importlib
from random import randint, uniform

from tensorforce.agents import Agent
from tensorforce.environments import OpenAIGym
from tensorforce.execution import Runner


def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    best_performance = 0.0
    best_episode = 0

    for iteration in range(1000):
        print('iteration', iteration, best_performance, flush=True)

        batch_size = int(10.0 ** uniform(1.0, 3.0))
        frequency = max(10, int(0.5 ** randint(1.0, 4.0) * batch_size))
        capacity = 5000
        learning_rate = 10.0 ** uniform(-5.0, -2.0)
        horizon = 50
        # baseline_learning_rate = 10.0 ** uniform(-5.0, -2.0)
        # subsampling_fraction = uniform(0.2, 1.0)
        # optimization_steps = randint(int(1.0 / subsampling_fraction) + 1, 30)

        agent = dict(
            agent='policy',
            network=dict(type='auto', internal_rnn=False),
            memory=dict(type='replay', capacity=capacity),
            update=dict(unit='timesteps', batch_size=batch_size, frequency=frequency),
            optimizer=dict(type='adam', learning_rate=learning_rate),
            objective=dict(type='policy_gradient', ratio_based=False, clipping_value=0.0, mean_over_actions=False),
            reward_estimation=dict(horizon=horizon, discount=0.99, estimate_horizon=False, estimate_actions=False, estimate_terminal=False, estimate_advantage=False),
            l2_regularization=0.0, entropy_regularization=0.0
        )

        runner = Runner(agent=agent, environment=dict(environment='gym', level='CartPole-v1'))

        performance_threshold = runner.environment.max_episode_timesteps() - horizon

        def callback(r):
            r.performance = sum(r.episode_rewards[-100:]) / min(100.0, r.episode)
            return r.performance < performance_threshold

        runner.run(num_episodes=1000, callback=callback, use_tqdm=False)

        if best_performance < performance_threshold and runner.performance > best_performance:
            print(runner.performance, runner.episode, flush=True)
            print(agent, flush=True)
            best_performance = runner.performance
            best_episode = runner.episode

        elif runner.performance > performance_threshold:
            print(runner.performance, runner.episode, flush=True)
            print(agent, flush=True)
            best_episode = runner.episode

        runner.close()


if __name__ == '__main__':
    main()
