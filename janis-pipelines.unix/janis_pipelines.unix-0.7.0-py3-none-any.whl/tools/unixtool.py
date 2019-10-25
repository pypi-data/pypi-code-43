from abc import ABC

from janis_core import CommandTool


class UnixTool(CommandTool, ABC):
    @staticmethod
    def tool_module():
        return "unix"

    @staticmethod
    def container():
        return "ubuntu:latest"

    @staticmethod
    def version():
        return "v1.0.0"
