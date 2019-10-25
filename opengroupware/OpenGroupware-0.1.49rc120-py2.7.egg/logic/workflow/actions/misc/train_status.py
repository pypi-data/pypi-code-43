#
# Copyright (c) 2014
#   Adam Tauno Williams <awilliam@whitemice.org>
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
import requests
from datetime import datetime
from coils.core import CoilsException
from coils.core.logic import ActionCommand

'''
TODO: Use the dixieland IP address from a server default
TODO: Use any defined HTTP proxy server
'''


class DixieLandTrainStatusAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "dixieland-trian-status"
    __aliases__ = ['dixielandTrainStatus', 'dixielandTrainStatusAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'text/html'

    def _build_url(self):

        return (
            'http://74.242.209.82/scripts/archivefinder.pl?seltrain={train}&'
            'selmonth={month}&selyear={year}&selday={day}'
            .format(
                train=self._train_id,
                month=self._select_date.month,
                year=self._select_date.year,
                day=self._select_date.day,
            )
        )

    def do_action(self):

        dixie_url = self._build_url

        response = requests.get(dixie_url)

        if not response.status_code == 200:
            raise CoilsException(
                'Unexpected response HTTP/{0} from dixieland'
                .format(response.status_code, )
            )

        self.wfile.write(response.text)

    def parse_action_parameters(self):

        self._train_id = self.process_label_substitutions(
            self.action_parameters.get(
                'trainId'
            )
        )

        self._select_date = datetime.strptime(
            self.process_label_substitutions(
                self.action_parameters.get(
                    'statusDate'
                )
            ),
            '%Y-%m-%d',
        )
