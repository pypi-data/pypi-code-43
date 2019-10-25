#
# Copyright (c) 2009, 2012, 2013, 2015, 2017
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE
#
from coils.core import Command, CoilsException

RETRIEVAL_MODE_SINGLE = 1
RETRIEVAL_MODE_MULTIPLE = 2


class GetCommand(Command):

    def __init__(self):
        Command.__init__(self)
        self.query_by = None
        self.set_single_result_mode()

    def set_multiple_result_mode(self):
        self.mode = RETRIEVAL_MODE_MULTIPLE

    def set_single_result_mode(self):
        self.mode = RETRIEVAL_MODE_SINGLE

    @property
    def single_result_mode(self):
        if (self.mode == RETRIEVAL_MODE_SINGLE):
            return True
        return False

    @property
    def multiple_result_mode(self):
        if (self.mode == RETRIEVAL_MODE_MULTIPLE):
            return True
        return False

    @property
    def limit(self):
        return self._limit

    def parse_parameters(self, **params):
        """
        ::get commands support the parameters id/ids and limit out-of-the-box
        A use of the parameter "id" will switch the command into single-
        result-mode while ids will switch it to multiple-result-mode.  Of
        course whatever is in run() can chage the mode.  Default limit of ::get
        is 150 items [which obviously only applies to multiple-result-mode].
        If id/ids are provided the attribute "query_by" will be set to
        "object_id".
        """
        Command.parse_parameters(self, **params)
        self.object_ids = []
        if (('id' in params) or ('ids' in params)):
            self.query_by = 'object_id'
            if ('id' in params):
                self.set_single_result_mode()
                self.object_ids.append(int(params['id']))
            elif ('ids' in params):
                self.set_multiple_result_mode()
                for object_id in params['ids']:
                    self.object_ids.append(int(object_id))
        self._limit = params.get('limit', None)
        # Limit (implemented 2010-10-22)
        if (self._limit is None):
            self._limit = 150
        else:
            self._limit = int(self._limit)

    def set_return_value(self, data, right='r', locks_enabled=True, ):
        """
        Determine what value will be the provided to the Command's consumer.
        This implementes access control as well as single/multiple result mode
        rules.
        """
        if isinstance(data, list):

            # Access checks are always disabled for contexts with admin role
            if ((self.access_check) and (not self._ctx.is_admin)):
                c = len(data)
                data = self._ctx.access_manager.filter_by_access(
                    right, data, locks_enabled=locks_enabled,
                )
                c = c - len(data)
                self.log.debug(
                    'access manager filtered out {0} objects.'.format(c, )
                )
            else:
                self.log.debug('access processing disabled!')

            """
            Single-Result mode returns a discrete item or None.  Multiple-
            Result mode returns a, possibly empty, list.  Always.
            """
            if self.single_result_mode:
                """
                IMPORTANT: in single result mode we return the FIRST
                candidate, subclasses can depend on this behavior in order
                to determine what candidate, when multiples exist, will
                be returned to the consumer.
                """
                if (len(data) > 0):
                    self._result = data[0]
                else:
                    """
                    In single-result mode the result of a ::get operation
                    with no result is always None.
                    """
                    self._result = None
            elif (self.multiple_result_mode):
                    self._result = data
            else:
                raise CoilsException('Unknown mode value')
            return
        elif (self.single_result_mode):
            # Single-result mode: return only one item, not a list
            if ((self.access_check) and (not self._ctx.is_admin)):
                data = self._ctx.access_manager.filter_by_access(
                    right, [data], locks_enabled=locks_enabled,
                )
                if (len(data) == 1):
                    """
                    IMPORTANT: in single result mode we return the FIRST
                    candidate, subclasses can depend on this behavior in order
                    to determine what candidate, when multiples exist, will
                    be returned to the consumer.
                    """
                    self._result = data[0]
                else:
                    """
                    In single-result mode the result of a ::get operation
                    with no result is always None.
                    """
                    self._result = None
            else:
                self._result = data
        else:
            # WARN: this is an odd exception. Might merit some refactoring???
            raise CoilsException('Data for Get result is not a list')
