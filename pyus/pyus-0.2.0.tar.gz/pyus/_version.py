import os
from pyus._build_utils.git import get_git_revision_extra


# Versioning inspired from scipy/numpy setup.py
# ---
# Semantic versioning (https://semver.org/)
MAJOR = 0
MINOR = 2
PATCH = 0
ISRELEASED = True
VERSION = '.'.join(map(str, (MAJOR, MINOR, PATCH)))

# Git directory
module_dir = os.path.dirname(__file__)
git_dir = os.path.abspath(os.path.join(module_dir, os.pardir, ".git"))

# Version
_version = VERSION
#   Add extra from git commit if not a release
if not ISRELEASED:
    git_rev_extra = get_git_revision_extra(path=git_dir)
    _version += git_rev_extra
