from janis_core import Array, ToolInput, ToolOutput, WildcardSelector, File
from ..data_types.tarfile import TarFile
from .unixtool import UnixTool


class Untar(UnixTool):
    @staticmethod
    def tool():
        return "untar"

    def friendly_name(self):
        return "Tar (unarchive)"

    @staticmethod
    def base_command():
        return ["tar", "xf"]

    def inputs(self):
        return [ToolInput("tarfile", TarFile, position=0)]

    def outputs(self):
        return [ToolOutput("out", Array(File), glob=WildcardSelector("*.java"))]
