#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

class MobikitException(Exception):
    """generic exception raised from within the mobikit library"""


class AuthException(MobikitException):
    def __init__(self):
        self.message = "You have not passed in a authorization token. Try using mobikit.set_api_key(<your token string>)"
        Exception.__init__(self, self.message)
