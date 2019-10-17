import os
from hashlib import md5
from pathlib import Path
from shutil import rmtree
from typing import Dict

from rye.base_executable import Executable
from rye.config import Environment


class Env(Executable):
    _hashcontents: bytes

    def __init__(self, name, config_env: Environment, global_lock=None):
        super().__init__(prefix=f"ENV {name}", global_lock=global_lock)
        self.name = name
        self.depends_files = [Path(file) for file in config_env.depends_files]
        self.location = Path(*config_env.location).resolve()
        self.create_command = config_env.create_command
        if config_env.python:
            self.create_command += ["-p", config_env.python]
        self.install_command = config_env.install_command
        self.setup_commands = config_env.setup_commands
        self.clean_existing = config_env.clean_existing
        self.install = True

    def should_rebuild(self) -> bool:
        """We take all the files listed in dependency files and save
        a hash of their contents at <base_location>/.<name>. So if any
        of those files change, we rebuild the virtualenv. This checks
        if we should do the rebuild
        """
        if not self.location.exists():
            return True
        if not (self.hashpath.exists() and self.hashpath.read_bytes() == self.hashdata):
            if self.clean_existing:
                rmtree(self.location, ignore_errors=True)
            return True
        return False

    @property
    def hashdata(self) -> bytes:
        if not hasattr(self, "_hashcontents"):
            contents = md5()
            for file in self.depends_files:
                contents.update(file.read_bytes())
            self._hashcontents = contents.digest()
        return self._hashcontents

    @property
    def hashpath(self) -> Path:
        return self.location.parent / Path(f".{self.name}")

    def write_hash(self):
        self.hashpath.write_bytes(self.hashdata)

    def env(self) -> Dict[str, str]:
        env = os.environ.copy()
        env["PATH"] = f"{self.location.joinpath('bin')}:{ env['PATH']}"
        env["VIRTUAL_ENV"] = f"{self.location}"
        return env

    async def run(self):
        self.writer.write("Preparing Env")
        if not self.should_rebuild():
            self.set_done()
            return
        # We dont run the create command if recycling existing venv
        if self.clean_existing or not self.location.exists():
            await self.run_command(self.create_command, os.environ.copy())
        for command in self.setup_commands:
            await self.run_command(command, self.env())

        # Build / install commands have a lot of issues running in
        # parallel, so run this step with a global lock
        if self.install:
            await self.run_locked(self.install_command, self.env())

        # If any of the tasks have set the bad flag, remove any files we created
        if not self.is_good():
            self.writer.write("Env failed to create")
            if self.clean_existing:
                rmtree(self.location, ignore_errors=True)
        else:
            self.writer.write("Env created")
            self.write_hash()
        self.set_done()

    @classmethod
    def build(cls, env_name, config, global_lock):
        env = config.environment(name=env_name)
        return cls(name=env_name, global_lock=global_lock, config_env=env)
