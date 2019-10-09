from mcutk.exceptions import ToolchainError
from mcutk.apps import appfactory



def build_project(tool_name, tool_path, project_path, tool_version=None,
    target=None, logfile=None, workspace=None, timeout=300):
    """A simple shortcut method to build C/C++ projects for embedded toolchains.

    Arguments:
        tool_name {string} -- toolchain name, like: iar, mdk, mcux, armgcc...
        tool_path {string} -- toolchain installation root directory
        project_path {string} -- project root directory or project path
        workspace {string} -- workspace directory for Eclipse based toolchains
        timeout {int} -- timeout for build
        tool_version {string} -- set toolchain version
        target {string} -- project configuration, debug/release
        logfile {string} -- log file path (default: {None})

    Raises:
        ToolchainError -- raise on unsupported toolchain
        IOError -- raise on toolchain is not ready

    Returns:
        mcutk.apps.BuildResult -- build result
    """

    tool = appfactory(tool_name)
    if not tool:
        raise ToolchainError('unsupported tool: %s'%tool_name)

    toolchain = tool(tool_path, version=tool_version)
    if not toolchain.is_ready:
        raise IOError('tool is not ready to use, please check the tool path!')

    project = tool.Project.frompath(project_path)

    if target:
        target = project.map_target(target)
    else:
        target = project.targets[0]

    ret = toolchain.build_project(project, target, logfile, workspace=workspace, timeout=timeout)

    return ret



