import logging
import os
import pathlib
import shutil
from mimetypes import guess_type

from dq.logging import error

logger = logging.getLogger(__name__)

# Incomplete list of textual types. These types are suitable for gzip.
TEXT_TYPES = set([
    'application/ecmascript',
    'application/javascript',
    'application/json',
    'application/x-javascript',
    'application/xhtml+xml',
    'application/xml',
    'image/svg+xml',
    'text/css',
    'text/csv',
    'text/html',
    'text/javascript',
    'text/markdown',
    'text/markdown',
    'text/plain',
    'text/xml',
])


def mkdirp(path):
    """Safely mkdir, creating all parent folders if they don't yet exist.

    This doesn't raise an error if the folder already exists. However, it does
    raise ``FileExistsError`` if the path points to an existing file.

    :param string path: The path to the folder to be created.
    """
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def rmrf(path):
    """Remove a path like rm -rf.

    :param string path: The path to remove.
    """
    try:
        shutil.rmtree(path)
    except NotADirectoryError:
        os.remove(path)
    except FileNotFoundError:
        return


def traverse(path, callback):
    """Traverse a directory recursively, performing a task.

    :param string path: The path of the directory.
    :param func callback: A callback applied to each child file and directory.
        It takes 2 arguments, the relative path from the root, and whether the
        item is a directory.
    """
    if not os.path.isdir(path):
        raise (
            NotADirectoryError(20, 'Not a directory', path)
            if os.path.exists(path) else
            FileNotFoundError(2, 'No such file or directory', path)
        )

    path = os.path.join(path, '')
    pathlen = len(path)
    for cwd, dirs, files in os.walk(path):
        for d in dirs:
            callback(os.path.join(cwd, d)[pathlen:], True)
        for f in files:
            callback(os.path.join(cwd, f)[pathlen:], False)


def fileinfo(path):
    """Information of a file.

    This function throws an error if the path is not a valid file. To suppress
    errors, use ``safe_fileinfo`` instead.

    :param string path: The path to the file.
    :returns string mime: The MIME type of the file, such as text/plain.
    :returns int size: The size (in bytes) of the file.
    :returns string encoding: The encoding of the file, like gzip. This is
        suitable for use as the Content-Encoding header.
    """
    mime, encoding = guess_type(path)
    size = os.path.getsize(path)
    return mime, size, encoding


def safe_fileinfo(path):
    """Retrive information of a file without throwing an error.

    If the path is invalid, None, 0, None will be returned.

    :param string path: The path to the file.
    :returns string mime: The MIME type of the file, such as text/plain.
    :returns int size: The size (in bytes) of the file.
    :returns string encoding: The encoding of the file, like gzip. This is
        suitable for use as the Content-Encoding header.
    """
    try:
        return fileinfo(path)
    except Exception as e:
        error(logger, 'Error getting fileinfo', {'path': path, 'error': e})
        return None, 0, None
