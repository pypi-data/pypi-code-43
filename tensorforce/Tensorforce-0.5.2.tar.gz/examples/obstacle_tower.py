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

from obstacle_tower_env import ObstacleTowerEnv

from tensorforce.agents import Agent
from tensorforce.execution import Runner


def run_episode(env):
    done = False
    reward = 0.0

    while not done:
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
    return reward


def run_evaluation(env):
    while not env.done_grading():
        run_episode(env)
        env.reset()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('environment_filename', nargs='?')
    # parser.add_argument('--docker_training', action='store_true')
    parser.add_argument('-a', '--agent', help="Agent configuration file")
    parser.add_argument('-n', '--network', default=None, help="Network specification file")
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

    environment = ObstacleTowerEnv(args.environment_filename, docker_training=True)

    agent = Agent.from_spec(spec=args.agent, environment=environment, network=args.network)

    runner = Runner(agent=agent, environment=environment)

    def callback(r):
        if r.episode % 100 == 0:
            print(
                "================================================\n"
                "Average secs/episode over 100 episodes: {time:0.2f}\n"
                "Average steps/sec over 100 episodes:    {timestep:0.2f}\n"
                "Average reward over 100 episodes:       {reward100:0.2f}\n"
                "Average reward over 500 episodes:       {reward500:0.2f}".format(
                    time=(sum(r.episode_times[-100:]) / 100.0),
                    timestep=(sum(r.episode_timesteps[-100:]) / sum(r.episode_times[-100:])),
                    reward100=(sum(r.episode_rewards[-100:]) / min(100.0, r.episode)),
                    reward500=(sum(r.episode_rewards[-500:]) / min(500.0, r.episode))
                )
            )
        return True

    if environment.is_grading():
        episode_reward = run_evaluation(environment)
    else:
        runner.run(
            num_timesteps=args.timesteps, num_episodes=args.episodes,
            max_episode_timesteps=args.max_episode_timesteps, deterministic=args.deterministic,
            callback=callback
        )

    environment.close()
