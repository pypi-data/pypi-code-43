#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

class MobikitUtilsError(Exception):
    """Generic mobikit utils error; can be used as a catch-all for calls to mobikit-utils methods."""

    pass


class MetadataError(MobikitUtilsError):
    """A generic error within the metadata service."""

    pass
