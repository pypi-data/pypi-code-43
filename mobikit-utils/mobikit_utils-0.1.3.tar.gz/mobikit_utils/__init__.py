#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

# this is meant to fail for public installs
# we don't want to publically expose spatial package yet
try:
    from .spatial import spatial
except ImportError:
    pass

from . import utils
