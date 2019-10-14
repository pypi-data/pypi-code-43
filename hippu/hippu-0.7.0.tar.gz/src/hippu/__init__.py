"""
Server.

Version:
    <major>.<minor>.<patch>

    Major:
        Compatibility / interface version.

        Revisions having the same major number should be fully backward
        compatible.

        Change in major number indicates that library is not fully
        backward compatible compared to previous version(s).

        Increasing major number zeros minor and patch numbers.

    Minor:
        Number of additions / new features not breaking backward compatibility.

        Increasing minor number zeros patch number.

    Patch:
        Number of fixes, improvements and internal changes (since previous major
        or minor update) that do not break backward compatibility.

        Patch does not add features or new functionality.

Credits:

Notes:
    Usage of os.<exit code> is not platform independent. 'exitstatus' module
    provides standard POSIX exit codes [https://pypi.org/project/exitstatus/].

"""
from ._meta import *  # pylint: disable=wildcard-import
from hippu.constant import HTTP
from .server import Server
from .service import BaseService
from .service import FileService
from .service import Service
from .filter import Filters

