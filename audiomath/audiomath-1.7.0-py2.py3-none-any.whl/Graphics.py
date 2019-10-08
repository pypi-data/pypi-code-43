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

__all__ = [
	
]

import sys

from . import Dependencies;         from .Dependencies import numpy
from . import DependencyManagement; from .DependencyManagement import LoadPyplot
from . import Base;                 from .Base import Sound

def Plot( self, hold=False, zeroBased=False, maxDuration=60, title=None, timeShift=0, timeScale=1 ):
	y = self.y
	if maxDuration is not None and maxDuration < self.duration:
		durationStr = 'infinite duration' if numpy.isinf( self.nSamples ) else 'nominal duration %g sec' % self.duration
		#typeStr = 'an array' if isinstance( y, numpy.ndarray ) else 'a ' + y.__class__.__name__
		typeStr = 'a %s' % self.__class__.__name__
		print( 'Plotting only the first %g seconds of %s of %s' % ( maxDuration, typeStr, durationStr ) )
		y = self[ :maxDuration ].y
	y = numpy.asarray( y ) / -2.0
	y = numpy.clip( y, -0.5, 0.5 )
	offset = numpy.arange( Base.NumberOfChannels( y ) )
	if not zeroBased: offset += 1
	y += offset
	t = numpy.arange( 0, Base.NumberOfSamples( y ) ) / float( self.fs )
	t += timeShift
	t *= timeScale

	plt = LoadPyplot()
	if not hold: plt.cla()
	h = plt.plot( t, y )
	ax = plt.gca()
	ax.set_yticks( offset )
	fmt = '%g'
	if not zeroBased: fmt = "'%s'" % fmt
	fmt = '[:,%s]' % fmt
	ax.yaxis.set_major_formatter( plt.FormatStrFormatter( fmt ) )
	ax.set_ylim( offset.max() + 1, offset.min() - 1 )
	ax.set_xlim( t[ 0 ], t[ -1 ] )
	if title is None: title = self.label
	if title: ax.set_title( title )
	ax.xaxis.grid( True )
	ax.yaxis.grid( True )
	#plt.draw()
	FinishFigure( zoom=True )
Sound.Plot = Plot

def FinishFigure( maximize=False, raise_=False, pan=False, zoom=False, wait=None, savefig=None ):
	plt = DependencyManagement.LoadPyplot()
	if not plt or not plt.get_fignums(): return
	ipythonIsRunning = 'IPython' in sys.modules
	if wait is None: wait = not ipythonIsRunning
	if ipythonIsRunning: plt.ion()
	elif wait: plt.ioff()
	plt.draw()
	try: toolbar = plt.gcf().canvas.toolbar
	except: toolbar = None
	if pan and toolbar is not None:
		try: turn_on_pan = ( toolbar._active is not 'PAN' )
		except: turn_on_pan = True
		if turn_on_pan: toolbar.pan( 'on' )
	if zoom and toolbar is not None:
		try: turn_on_zoom = ( toolbar._active is not 'ZOOM' )
		except: turn_on_zoom = True
		if turn_on_zoom: toolbar.zoom( 'on' )
	try: manager = plt.get_current_fig_manager()
	except: manager = None
	if maximize:
		try: plt.gcf().canvas._tkcanvas.master.wm_state( 'zoomed' )
		except: pass
		try: manager.window.state( 'zoomed' )
		except: pass
		try: manager.window.showMaximized()
		except: pass
		try: manager.frame.Maximize( True )
		except: pass
	if raise_:
		try: manager.window.raise_()
		except: pass
	if savefig: plt.gcf().savefig( savefig )
	if wait == 'block': plt.show( block=True )
	elif wait: plt.show()
