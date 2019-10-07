#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

from mobikit.config import config
from mobikit.exceptions import AuthException
from functools import wraps


def token_required(func):
    @wraps(func)
    def _token_required(*args, **kwargs):
        if config.api_token is None:
            raise AuthException
        return func(*args, **kwargs)

    return _token_required
