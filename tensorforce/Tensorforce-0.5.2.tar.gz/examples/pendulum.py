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


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(v=tf.logging.ERROR)


num_episodes = 750


def main():
    reward = [list() for _ in range(num_episodes)]
    ms_per_timestep = [list() for _ in range(num_episodes)]

    for n in range(10):
        print('run', n + 1, end=' ', flush=True)
        environment = OpenAIGym('Pendulum-v0')

        agent = PPO(
            states=environment.states(), actions=environment.actions(),
            max_episode_timesteps=environment.max_episode_timesteps(),
            network=[dict(type='dense', size=32), dict(type='dense', size=32)],
            batch_size=8, update_frequency=1, learning_rate=0.001813150053725916,
            subsampling_fraction=0.36311833373631697, optimization_steps=4,
            likelihood_ratio_clipping=0.1703853966061285, discount=0.8861086463000614,
            estimate_terminal=True,
            critic_network=[dict(type='dense', size=32), dict(type='dense', size=32)],
            critic_optimizer=dict(
                type='multi_step', optimizer=dict(type='adam', learning_rate=0.0014819954404143476),
                num_steps=18
            ),
            entropy_regularization=0.010008788962053457
        )

        runner = Runner(agent=agent, environment=environment)

        def callback(r):
            reward[r.episode - 1].append(float(np.mean(r.episode_rewards[-20:])))
            ms_per_timestep[r.episode - 1].append(float(np.mean(r.episode_seconds[-20:]) * 1000.0 / np.mean(r.episode_timesteps[-20:])))
            return True

        runner.run(num_episodes=num_episodes, callback=callback)  # , use_tqdm=False
        runner.close()
        print()

    figure, axis1 = plt.subplots()
    xs = np.arange(len(reward))
    axis1.plot(xs, np.median(reward, axis=1), color='green', linewidth=2.0)
    axis1.fill_between(xs, np.amin(reward, axis=1), np.amax(reward, axis=1), color='green', alpha=0.4)
    axis2 = axis1.twinx()
    axis2.plot(xs, np.median(ms_per_timestep, axis=1), color='blue', linewidth=2.0)
    axis2.fill_between(xs, np.amin(ms_per_timestep, axis=1), np.amax(ms_per_timestep, axis=1), color='blue', alpha=0.4)
    plt.savefig(os.path.join('examples', 'pendulum.png'))


if __name__ == '__main__':
    main()
