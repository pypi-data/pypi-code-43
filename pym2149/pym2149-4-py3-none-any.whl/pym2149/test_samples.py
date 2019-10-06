# Copyright 2014, 2018, 2019 Andrzej Cichocki

# This file is part of pym2149.
#
# pym2149 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pym2149 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pym2149.  If not, see <http://www.gnu.org/licenses/>.

from .config import ConfigName
import unittest, samples, re

wordpattern = re.compile(r'\S+')
statetobatterypower = {'charging': False, 'fully-charged': False, 'discharging': True}

def batterypower():
    try:
        from lagoon import upower
    except ImportError:
        return # Run all tests.
    def states():
        for line in upower('--show-info', '/org/freedesktop/UPower/devices/battery_C173').stdout.decode().splitlines():
            words = wordpattern.findall(line)
            if 2 == len(words) and 'state:' == words[0]:
                yield words[1]
    state, = states()
    return statetobatterypower[state]

class TestSamples(unittest.TestCase):

    def test_samples(self):
        if batterypower():
            return
        samples.mainimpl(ConfigName(args = []))
