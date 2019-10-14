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
    # Gym arguments
    parser.add_argument('-g', '--gym', help="Gym environment id")
    parser.add_argument(
        '-i', '--import-modules', help="Import module(s) required for gym environment"
    )
    # Runner arguments
    parser.add_argument('-e', '--episodes', type=int, default=None, help="Number of episodes")
    parser.add_argument('-t', '--timesteps', type=int, default=None, help="Number of timesteps")
    parser.add_argument(
        '-m', '--max-episode-timesteps', type=int, default=None,
        help="Maximum number of timesteps per episode"
    )
    parser.add_argument(
        '-d', '--deterministic', action='store_true', default=False,
        help="Choose actions deterministically"
    )
    args = parser.parse_args()

    if args.import_modules is not None:
        for module in args.import_modules.split(','):
            importlib.import_module(name=module)

    best_performance = 0.0

    for iteration in range(1000):
        print('iteration', iteration, flush=True)
        environment = OpenAIGym(gym_id='CartPole-v1')

        batch_size = randint(5, 50)
        frequency = randint(1, batch_size)
        memory = (batch_size + 1) * 200
        learning_rate = 10.0 ** uniform(-5.0, -2.0)
        baseline_learning_rate = 10.0 ** uniform(-5.0, -2.0)
        subsampling_fraction = uniform(0.2, 1.0)
        optimization_steps = randint(int(1.0 / subsampling_fraction) + 1, 30)

        agent_spec = dict(
            type='ppo', network=dict(type='auto', size=64, depth=2, internal_rnn=True),
            update_mode=dict(unit='episodes', batch_size=batch_size, frequency=frequency),
            memory=memory, discount=0.99, entropy_regularization=None,
            baseline_mode='states', baseline=dict(type='network', network='auto'),
            baseline_optimizer=dict(type='adam', learning_rate=baseline_learning_rate),
            gae_lambda=None, likelihood_ratio_clipping=0.2,
            step_optimizer=dict(type='adam', learning_rate=learning_rate),
            subsampling_fraction=subsampling_fraction, optimization_steps=optimization_steps
        )

        agent = Agent.from_spec(spec=agent_spec, environment=environment)

        runner = Runner(agent=agent, environment=environment)

        def callback(r):
            r.performance = sum(r.episode_rewards[-100:]) / min(100.0, r.episode)
            return r.performance < 190.0

        runner.run(num_episodes=1000, max_episode_timesteps=200, callback=callback, use_tqdm=False)

        if runner.performance > best_performance:
            print(runner.performance, runner.episode, flush=True)
            print(agent_spec, flush=True)
            best_performance = runner.performance

        runner.close()


if __name__ == '__main__':
    main()
