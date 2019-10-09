from mcutk.exceptions import (ProjectNotFound, ProjectParserError, InstallError)

__all__ = ["appfactory", "factory"]



def appfactory(name):
    """Return specific APP class.

    Example 1, basic:
        >>> APP = appfactory('iar')
        <mcutk.apps.iar.APP object at 0x1023203>

    Example 2, get the latest instance by scanning your system:
        >>> app = appfactory('iar').get_latest()
        >>> print app.path
        C:/program files(x86)/IAR Systems/IAR Workbench/
        >>> print app.version
        8.22.2

    Example 3, create app instance directly:
        >>> APP = appfactory('iar')
        >>> app = APP('/path/to/ide', version='1.0.0')
        >>> print app.path
        C:/program files(x86)/IAR Systems/IAR Workbench/
        >>> print app.version
        8.22.2

    Example 4, load and parse the project:
        >>> project = appfactory('iar').Project('/path/to/project')
        >>> print project.name
        hello_world
        >>> print project.targets
        ['debug', 'release']

    """
    import importlib
    try:
        idemodule = importlib.import_module("mcutk.apps.%s"%(name))
        appcls = getattr(idemodule, "APP")
        projcls = getattr(idemodule, "Project")
        appcls.Project = projcls
    except ImportError:
        return None

    return appcls



def factory(name):
    """Return specific app module"""
    import importlib
    try:
        idemodule = importlib.import_module("mcutk.apps.%s"%(name))
    except ImportError:
        pass
    return idemodule
