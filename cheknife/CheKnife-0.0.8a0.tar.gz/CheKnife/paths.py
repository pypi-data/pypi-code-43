import os
import six
from CheKnife.errors import ParameterError


def mktree(abs_path):
    if not abs_path:
        raise ParameterError("No valid path suplied to mktree: {}".format(abs_path))
    if not os.path.isdir(abs_path):
        try:
            if six.PY3:
                os.makedirs(abs_path, exist_ok=True)
            elif six.PY2:
                os.makedirs(abs_path)

        except IOError:
            raise PermissionError('Error creating directory: {} Check user permissions'.format(abs_path))
    return True


class Tree(object):
    paths = []

    def __init__(self, root_path, exclude=None):
        if exclude is None:
            self.exclude = []
        else:
            self.exclude = exclude
        self.root_path = root_path
        self.path_list(root_path)

    def path_list(self, root):
        for filename in os.listdir(root):
            if filename not in self.exclude:
                full_path = os.path.join(root, filename)

                if not os.path.isdir(full_path):
                    self.paths.append(full_path)
                else:
                    self.path_list(full_path)

    @property
    def list(self):
        self.paths = []
        self.path_list(self.root_path)
        return self.paths


def split_path(file_path):
    path, filename = os.path.split(file_path)
    filename, file_extension = os.path.splitext(filename)
    return {'path': path, 'filename': filename, 'extension': file_extension, 'type': file_extension.replace('.', '')}


def mv(from_path, to_path):
    os.rename(from_path, to_path)
