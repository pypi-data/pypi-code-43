# -*- coding: utf-8 -*-
""" Git helpers. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from os.path import join, exists


def load_gitignore(repo_path):
    """ Load exclude patterns from .gitignore

    :param str repo_path:
        Path to the git repo. The .gitignore file inside that repo will be
        used.
    :return List[str]:
        List of exclude patterns read from .gitignore.
    """
    gitignore_path = join(repo_path, '.gitignore')

    exclude_patterns = []

    if exists(gitignore_path):
        with open(gitignore_path) as fp:
            for line in fp.readlines():
                line = line.strip()

                if line.startswith('#'):
                    continue

                elif line.startswith('/'):
                    line = line[1:]

                if line:
                    exclude_patterns.append(line)

    return exclude_patterns
