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

import matplotlib
import os
import sys

import numpy as np
import tensorflow as tf

from tensorforce.agents import PPO
from tensorforce.execution import Runner
from tensorforce.environments import OpenAIGym

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(v=tf.logging.ERROR)


num_episodes = 200


def main():
    num_timesteps = [list() for _ in range(num_episodes)]
    reward = [list() for _ in range(num_episodes)]
    ms_per_timestep = [list() for _ in range(num_episodes)]

    for n in range(10):
        print('run', n + 1, end=' ', flush=True)
        environment = OpenAIGym('PongNoFrameskip-v4')

        agent = PPO(
            states=environment.states(), actions=environment.actions(),
            max_episode_timesteps=environment.max_episode_timesteps(),
            network='auto',
            batch_size=12, update_frequency=1, learning_rate=0.001813150053725916,
            subsampling_fraction=0.9131375430837279, optimization_steps=5,
            likelihood_ratio_clipping=0.09955676846552193, discount=0.9985351346308641,
            estimate_terminal=True,
            critic_network='auto',
            critic_optimizer=dict(
                type='multi_step', optimizer=dict(type='adam', learning_rate=0.003670157218888348),
                num_steps=10
            ),
            entropy_regularization=0.0011393096635237982
        )

        runner = Runner(agent=agent, environment=environment)

        def callback(r):
            num_timesteps[r.episode - 1].append(float(np.mean(r.episode_timesteps[-20:])))
            reward[r.episode - 1].append(float(np.mean(r.episode_rewards[-20:])))
            ms_per_timestep[r.episode - 1].append(float(np.mean(r.episode_seconds[-20:]) * 1000.0 / np.mean(r.episode_timesteps[-20:])))
            return True

        runner.run(num_episodes=num_episodes, callback=callback)  # , use_tqdm=False
        runner.close()

        for n in range(runner.episode, len(num_timesteps)):
            num_timesteps[n].append(num_timesteps[runner.episode - 1][-1])
            reward[n].append(reward[runner.episode - 1][-1])
            ms_per_timestep[n].append(ms_per_timestep[runner.episode - 1][-1])
        print()

    palette = iter(sns.color_palette())
    figure, axis1 = plt.subplots()
    color = next(palette)
    xs = [n + 1 for n in range(num_episodes)]
    mean = np.mean(num_timesteps, axis=1)
    std = np.std(num_timesteps, axis=1)
    axis1.plot(xs, mean, color=color)
    axis1.fill_between(xs, mean - std, mean + std, color=color, alpha=0.5)
    axis1.fill_between(xs, np.amin(num_timesteps, axis=1), np.amax(num_timesteps, axis=1), color=color, alpha=0.3)

    color = next(palette)
    mean = np.mean(reward, axis=1)
    std = np.std(reward, axis=1)
    axis1.plot(xs, mean, color=color)
    axis1.fill_between(xs, mean - std, mean + std, color=color, alpha=0.5)
    axis1.fill_between(xs, np.amin(reward, axis=1), np.amax(reward, axis=1), color=color, alpha=0.3)
    axis1.set_ylabel('reward')
    axis1.legend(['ts', 'rew'], loc='upper right')

    axis2 = axis1.twinx()
    color = next(palette)
    mean = np.mean(ms_per_timestep, axis=1)
    std = np.std(ms_per_timestep, axis=1)
    axis2.plot(xs, mean, color=color)
    axis2.fill_between(xs, mean - std, mean + std, color=color, alpha=0.5)
    axis2.fill_between(xs, np.amin(ms_per_timestep, axis=1), np.amax(ms_per_timestep, axis=1), color=color, alpha=0.3)
    axis2.set_ylabel('ms/ts')
    axis2.legend(['ms/ts'], loc='upper left')

    # plt.legend(['ts', '', '', 'rew', '', '', 'ms/ts', '', ''], bbox_to_anchor=(1.05, 1), loc=2)
    plt.savefig(os.path.join('examples', 'test6.png'), bbox_inches='tight')


if __name__ == '__main__':
    main()
