"""
Base types for system command wrappers
"""

from __future__ import annotations

import functools
import shutil
from typing import List

from healer.config import CONFIG
from healer.support.process import Command
from healer.support.process import ExecuteResult
from healer.support.process import execute_process_flow
from healer.support.process import execute_process_unit
from healer.support.typing import WithTypeName


def missing_required_list() -> List[str]:
    required_list = CONFIG.get_list('wrapper', 'required_list')
    missing_list = []
    for command in required_list:
        try:
            system_command(command)
        except Exception:
            missing_list.append(command)
    return missing_list


@functools.lru_cache()
def system_command(command:str) -> str:
    path = shutil.which(command)
    if path:
        return path
    else:
        raise RuntimeError(f'Missing system command: {command}')


def make_option_assign (name, value=None) -> List[str]:
    if value is None:
        return [f"--{name}"]
    else:
        return [f"--{name}={value}"]


def make_option_TrueFalseValue (name, value=None) -> List[str]:
    if value is True:
        return [f"--{name}"]
    elif value is False:
        return [f"--no-{name}"]
    elif value is None:
        return [f"--{name}"]
    else:
        return [f"--{name}", value]


class Base(WithTypeName, object):

    base:'Base' = None

    binary:str
    option_list: List[str]

    def __str__(self):
        return f"{self.type_name()}({self.full_command()})"

    def __init__(self, section):
        super().__init__()
        self.with_config(section)

    def with_config(self, section):
        binary = CONFIG[section]['binary']
        option_list = CONFIG.get_list(section, 'option_list')
        return self.with_params(binary, option_list)

    def with_params(self, binary:str, option_list:List[str]):
        self.binary = system_command(binary)
        self.option_list = option_list
        return self

    def with_binary(self, binary):
        self.binary = binary
        return self

    def with_option (self, name, value=None):
        self.option_list.extend(make_option_TrueFalseValue(name, value))
        return self

    def has_success(self, command) -> bool:
        result = self.execute_unit(command)
        return result.rc == 0

    def base_command(self) -> Command:
        if self.base:
            return self.base.full_command()
        else:
            return []

    def full_command(self, command:Command=[]) -> Command:
        return self.base_command() + [self.binary] + self.option_list + command

    def execute_unit(self, command:Command=[], stdin:str=None) -> ExecuteResult:
        return execute_process_unit(
            command=self.full_command(command),
            stdin=stdin,
        )

    def execute_flow(self, command:Command=[], stdin:str=None) -> ExecuteResult:
        return execute_process_flow(
            command=self.full_command(command),
            stdin=stdin,
            react_stdout=self.react_stdout,
            react_stderr=self.react_stderr,
        )

    def execute_unit_sert(self, command:Command=[], stdin=None) -> ExecuteResult:
        result = self.execute_unit(
            command=command,
            stdin=stdin,
        )
        result.assert_return()
        return result
