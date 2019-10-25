#
# Copyright (c) 2015
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

import yaml
from datetime import datetime, date

try:
    import json
except:
    import simplejson as json


def coils_json_encode(data, wfile, allow_none=True, ):
    """
    Encode the data to JSON using an enocder method to manage special types.
    """

    def _encode(o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%dT%H:%M:%S')
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        if isinstance(o, date):
            return list(o)
        raise TypeError(
            'Unable to serialize type "{0}" in JSON'
            .format(type(o), )
        )

    return json.dump(data, wfile, default=_encode, )


def coils_yaml_encode(data, wfile, allow_none=True, ):
    """
    Encode the data to YAML using the OpenGroupware Coils default formatting
    of two spaces and default-flow-style disabled.
    """

    return yaml.dump(data, wfile, default_flow_style=False, indent=2, )

def coils_yaml_encode_to_string(data, allow_none=True, ):
    """
    Encode the data to YAML using the OpenGroupware Coils default formatting
    of two spaces and default-flow-style disabled.
    """

    return yaml.dump(data, default_flow_style=False, indent=2, )

def coils_yaml_decode(rfile, allow_none=True, ):
    """
    Decode the data from a YAML stream
    """

    return yaml.load(rfile)
