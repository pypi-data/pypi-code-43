from asyncio import Lock, gather, get_event_loop
from itertools import chain
from typing import List

from click import echo

from rye.base_executable import Executable
from rye.environment import Env
from rye.task import Task


class Application:
    _executables: List[Executable]

    def __init__(self, config, tasks=None, envs=None):
        self.config = config
        self.environments = {}
        self.tasks = {}
        self.loop = get_event_loop()
        self.loop.run_until_complete(self._build_tasks(tasks, envs))

    @property
    def executables(self):
        if not hasattr(self, "_executables"):
            self._executables = list(
                chain(self.environments.values(), self.tasks.values())
            )
        return self._executables

    async def _build_tasks(self, tasks_to_run, envs_to_run):
        lock = Lock()
        for task_name in tasks_to_run or self.config.default_tasks:
            with self.config.context(f"task.{task_name}"):
                for env in self.config.target_environments:
                    if envs_to_run and env not in envs_to_run:
                        continue
                    name = f"{env}#{task_name}"
                    env_name = f"{env}#{task_name}" if self.config.isolate else env
                    if env_name not in self.environments:
                        self.environments[env_name] = Env.build(
                            env_name, self.config, lock
                        )
                    self.tasks[name] = Task(
                        f"TASK {name}",
                        self.environments[env_name],
                        self.config.commands,
                        lock,
                    )

    async def async_build_envs(self, envs):
        env_tasks = (
            [e for e in self.environments.values() if e.name in envs]
            if envs
            else self.environments.values()
        )
        for task in env_tasks:
            task.install = False
        await self.main_loop(env_tasks)

    async def run_tasks(self):
        return await self.main_loop(self.executables)

    @staticmethod
    async def main_loop(executables):
        echo(f"Running tasks- {[t.name for t in executables]}")
        await gather(*[t.run() for t in executables])
        bad = 0
        for t in executables:
            if not t.is_good():
                echo(f"Task {t.name} failed")
                if t.writer.messages:
                    error = t.writer.messages[-1]
                else:
                    error = "NO OUTPUT"
                echo(f"    {error}")
                bad += 1

        echo(f"{len(executables) - bad} of {len(executables)} Succeeded")
        return bad

    def run(self):
        return self.loop.run_until_complete(self.run_tasks())

    def build_envs(self, envs):
        return self.loop.run_until_complete(self.async_build_envs(envs))
