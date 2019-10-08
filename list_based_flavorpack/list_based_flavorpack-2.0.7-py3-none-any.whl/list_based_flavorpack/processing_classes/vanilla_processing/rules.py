'''
    Copyright 2018 SerialLab, CORP

    This file is part of ListBasedFlavorpack.

    RandomFlavorpack is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    RandomFlavorpack is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with RandomFlavorpack.  If not, see <http://www.gnu.org/licenses/>.
'''
from rest_framework import status
from serialbox.rules.common import PreprocessingRule
from serialbox.rules.errors import RuleError


class OddNumberError(RuleError):

    def __init__(self, detail=None):
        self.default_detail = ('No odd number requests are allowed! '
                               'To disable this remove the OddNumberError '
                               'rule from the GENERATOR_PREPROCESSING_RULES settings.')
        # NOTE:
        # the status is 400 by default, just including here as an example!!!
        self.status_code = status.HTTP_400_BAD_REQUEST
        RuleError.__init__(self, detail=detail)


class NoOddRequests(PreprocessingRule):
    '''
    Example rule that doesn't allow requests for odd numbers.
    '''

    def execute(self, request, pool, region, size):
        # check the size
        if size % 2 != 0:
            raise OddNumberError()
