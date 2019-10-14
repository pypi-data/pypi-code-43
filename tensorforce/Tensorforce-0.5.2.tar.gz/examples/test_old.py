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
import sys

import numpy as np
import tensorflow as tf

from tensorforce.agents import Agent
from tensorforce.execution import Runner
from tensorforce.environments import OpenAIGym


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(v=tf.logging.ERROR)


def main():
    environment = OpenAIGym('CartPole-v1')

    agent = 'examples/configs/{}_cartpole.json'.format(sys.argv[1])

    runner = Runner(agent=agent, environment=environment)

    def callback(r):
        if r.episode % 100 == 0:
            print('{}/{}'.format(
                float(np.mean(r.episode_rewards[-100:])),
                sum(reward == 200.0 for reward in r.episode_rewards[-100:])
            ), end=' ', flush=True)

    runner.run(num_episodes=1000, max_episode_timesteps=200, callback=callback, use_tqdm=False)
    runner.close()
    print()


if __name__ == '__main__':
    main()
