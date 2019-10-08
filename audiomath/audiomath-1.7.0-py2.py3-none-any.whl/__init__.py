# $BEGIN_AUDIOMATH_LICENSE$
# 
# This file is part of the audiomath project, a Python package for
# recording, manipulating and playing sound files.
# 
# Copyright (c) 2008-2019 Jeremy Hill
# 
# audiomath is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# The audiomath distribution includes binaries from the third-party
# AVbin and PortAudio projects, released under their own licenses.
# See the respective copyright, licensing and disclaimer information
# for these projects in the subdirectories `audiomath/_wrap_avbin`
# and `audiomath/_wrap_portaudio` . It also includes a fork of the
# third-party Python package `pycaw`, released under its original
# license (see `audiomath/pycaw_fork.py`).
# 
# $END_AUDIOMATH_LICENSE$

"""
`audiomath` is a package for reading, manipulating, and writing
sound waveforms. It also lets you record and play sounds, with a
high degree of real-time control over playback.

To manipulate sound waveforms, plot them, and write them to disk,
use the `Sound` class.  Usually you would initialize a `Sound`
instance from a filename, or from a `numpy` array---in the latter
case your array would contain floating-point values in the range
[-1, +1], arranged samples-by-channels.

To play sounds, use the `Player` class.  You can initialize a
`Player` instance from a `Sound` instance, or from anything that
can be used to create one (e.g. a filename).  You can also supply
a sequence of `Sound` instances, or a sequence of filenames or a
`glob` pattern that matches multiple files: then you can have the
`Player` instance manage multiple "tracks".  Each `Player` will
only play one sound at a time: to overlap sounds, create multiple
`Player` instances.

To record a sound, use the `Record` function,  or the `Recorder`
class if you want to do it asynchronously. 
"""

#from . import DependencyManagement; DependencyManagement.Sabotage( 'numpy', 'matplotlib' ) # !!!! for debugging only
from . import Base;                 from .Base                 import *
from . import Functional;           from .Functional           import *
from . import GenericInterface;     from .GenericInterface     import *
from . import IO;                   from .IO                   import *    # anything except an uncompressed .wav file requires AVbin
from . import Graphics;             from .Graphics             import *    # requires matplotlib
from . import Meta;                 from .Meta                 import *
from . import BackEnd;              from .BackEnd              import *
from . import DependencyManagement; from .DependencyManagement import * 
from . import Signal; # and let's not import every symbol from there

from . import PortAudioInterface;   from .PortAudioInterface   import *    # we only do this as a concession to linting by PyCharm etc
BackEnd.Load()   # This is how back-ends are intended to be loaded. The default is .PortAudioInterface.  Others (as they are developed) won't be visible in PyCharm
