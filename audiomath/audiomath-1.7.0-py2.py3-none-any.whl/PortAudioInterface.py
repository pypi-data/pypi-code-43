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
This submodule contains PortAudio-specific implementations of high-
level `Player` and `Recorder` classes. They inherit their API-user-
facing functionality, as well as their code for manipulating raw
`Sound` data, from `GenericInterface.GenericPlayer` and
`GenericInterface.GenericRecorder`.   The PortAudio-specific
subclasses act as intermediaries between the generic stuff and the
objects and functions in the `_wrap_portaudio` submodule.

This submodule also contains various global functions for listing
and selecting the available sound devices and their host APIs.

The `PortAudioInterface` is the default playing/recording back-end
for `audiomath`.  Therefore, all the symbols exported by this
submodule are also available at the top level `audiomath.*`
namespace (at least until another back-end is written, and loaded
with `audiomath.BackEnd.Load()`).
"""
__all__ = [
	# from _wrap_portaudio:
	'PORTAUDIO', 'SetDefaultVerbosity', 
	'GetHostApiInfo', 'GetDeviceInfo', 'FindDevice', 'FindDevices', 'Tabulate',
	'Stream',
	# from here:
	'GetOutputDevice', 'SetOutputDevice', 'Player',
	'GetInputDevice',  'SetInputDevice',  'Recorder', 'Record',
]

import time

from . import GenericInterface

from . import _wrap_portaudio; from ._wrap_portaudio import \
	Stream, PORTAUDIO, SetDefaultVerbosity, GetHostApiInfo, GetDeviceInfo, FindDevice, FindDevices, Tabulate

SINGLE_OUTPUT_STREAM = True   # seems to *need* to be True for ASIO (otherwise only the first sound can be played: others are silenced); also drastically cuts down Player() initialization time when True (from 100-200ms down to <1ms)
DEFAULT_OUTPUT_DEVICE = None
def SetOutputDevice( device ):
	"""
	Set the specified `device` as the default device to be
	used for `Player` objects.  The `device` argument may
	be the device index, one or more words from the device
	name, or the full device record from `GetDeviceInfo()`
	or `FindDevices()`.
	
	See also:  `GetOutputDevice()`
	"""
	global DEFAULT_OUTPUT_DEVICE
	record = FindDevice( id=device )
	DEFAULT_OUTPUT_DEVICE = record[ 'index' ]
	return record
	
def GetOutputDevice():
	"""
	Return the default output device, if any has been set.
	
	See also:  `SetOutputDevice()`
	"""
	device = DEFAULT_OUTPUT_DEVICE
	if device is None: return None
	return FindDevice( id=device )

SINGLE_INPUT_STREAM = True
DEFAULT_INPUT_DEVICE = None
def SetInputDevice( device ):
	"""
	Set the specified `device` as the default device to be
	used for `Recorder` objects.  The `device` argument may
	be the device index, one or more words from the device
	name, or the full device record from `GetDeviceInfo()`
	or `FindDevices()`.
	
	See also:  `GetInputDevice()`
	"""
	global DEFAULT_INPUT_DEVICE
	record = FindDevice( id=device )
	DEFAULT_INPUT_DEVICE = record[ 'index' ]
	return record
	
def GetInputDevice():
	"""
	Return the default input device, if any has been set.
	
	See also:  `SetInputDevice()`
	"""
	device = DEFAULT_INPUT_DEVICE
	if device is None: return None
	return FindDevice( id=device )
	

class Player( GenericInterface.GenericPlayer ):
	__doc__ = GenericInterface.GenericPlayer.__doc__ # weirdly necessary for sphinx
	__stream = __verbose = None
	def __init__( self, sound, device=None, stream=None, resample=False, verbose=None, **kwargs ):
		"""
		Args:
			sound (str, Sound, Queue, None):
				`Sound` instance to play (or sequence of `Sound`
				instances in a `list` or `Queue`).  Alternatively,
				supply any argument that is also a valid input to
				the `Sound` or `Queue` constructors (e.g. a filename,
				list of filenames, or file glob pattern).
			
			device (int, str, dict, Stream, None):
				Optionally use this argument to specify the
				device/stream to use for playback---as an integer
				index, a device name, a full device record from
				`FindDevice()`, or (fastest of all) an already-open
				`Stream` instance.
				
			stream (int, str, dict, Stream, None):
				Synonymous with `device`, for compatibility.
			
			resample (bool):
				Specifies how to handle potential mismatch between
				the sampling frequency of the sound data
				`self.sound.fs` and the sampling frequency of the
				output stream `self.stream.fs`.  If true, replace
				`self.sound` with a copy resampled to the stream's
				preferred rate. If false, simply adjust playback
				speed accordingly.
				
			verbose (bool, None):
				Verbosity for debugging. If `None`, inherit from the
				setting specified by `SetDefaultVerbosity()`, if any.
			
			**kwargs:
				passed through to `.Set()` to initialize properties
				of the `Player` instance.
		"""
		if stream is None and device is not None: stream = device
		if device is None and stream is not None: device = stream
		if device != stream: raise ValueError( 'the `stream` and `device` arguments are synonymous---they cannot take different values unless one is left as `None`' )
		self.__stream = None
		self.__verbose = verbose
		if self.verbose: print( '%r is being initialized' % self )
		global SINGLE_OUTPUT_STREAM, DEFAULT_OUTPUT_DEVICE
		if stream is None: stream = DEFAULT_OUTPUT_DEVICE
		mode = 'oo' if stream is None else None
		deviceRecord = stream.outputDevice if isinstance( stream, Stream ) else stream if isinstance( stream, dict ) else None
		deviceIndex = stream if isinstance( stream, int ) else None
		if deviceIndex is None:
			if deviceRecord is None: deviceRecord = FindDevice( id=stream, mode=mode )
			deviceIndex = deviceRecord[ 'index' ]
		if not SINGLE_OUTPUT_STREAM:
			if deviceRecord is None: deviceRecord = GetDeviceInfo()[ deviceIndex ]
			if any( word.startswith( 'ASIO' ) for word in deviceRecord[ 'name' ].upper().split() ):
				SINGLE_OUTPUT_STREAM = True
		if SINGLE_OUTPUT_STREAM:
			alreadyInitialized = isinstance( SINGLE_OUTPUT_STREAM, Stream )
			if not isinstance( stream, Stream ):
				if alreadyInitialized and deviceIndex == SINGLE_OUTPUT_STREAM.outputDevice[ 'index' ]: stream = SINGLE_OUTPUT_STREAM
				else: stream = Stream( device=deviceIndex )
			#if alreadyInitialized and stream and stream is not SINGLE_OUTPUT_STREAM: raise RuntimeError( 'cannot create multiple Streams' )
			self.__stream = stream if stream else SINGLE_OUTPUT_STREAM if alreadyInitialized else Stream( mode=mode )
			if not alreadyInitialized: SINGLE_OUTPUT_STREAM = self.__stream
			if not DEFAULT_OUTPUT_DEVICE: DEFAULT_OUTPUT_DEVICE = self.__stream.outputDevice[ 'index' ]
		else:
			self.__stream = stream if isinstance( stream, Stream ) else Stream( device=deviceIndex, mode=mode )
			
		super( Player, self ).__init__( sound=sound, **kwargs )
		if self.sound:
			soundFs = self.sound.fs
			streamFs = self.__stream.fs
			if soundFs != streamFs:
				if resample:
					if self.verbose: print( '%r is resampling its sound from %g to %g Hz' % ( self, soundFs, streamFs ) )
					self.Resample( streamFs )
				else:
					if self.verbose: print( '%r will play at %g * nominal speed to match stream rate of %g Hz' % ( self, self._sampleRateEqualizationFactor, streamFs ) )
		self.__stream._AddOutputCallback( self._OutputCallback )

	def _Profile( self, seconds=5, type='cProfile', **kwargs ):
		wasPlaying = self.playing
		self.Play( **kwargs )
		if type in [ 'line_profiler' ]: profArgs = { type : self._OutputCallback }
		else: profArgs = { type : True }
		self.__stream.StartProfiling( **profArgs )
		try: time.sleep( seconds )
		except KeyboardInterrupt: pass
		t = self.__stream.StopProfiling()
		if not wasPlaying: self.Pause()
		return t
		
	@property
	def stream( self ):
		return self.__stream

	@property
	def verbose( self ):
		if self.__verbose is not None: return self.__verbose
		return self.__stream.verbose if self.__stream else False
	@verbose.setter
	def verbose( self, value ):
		self.__verbose = value
	
	def __del__( self ):
		if self.verbose: print( '%r is being deleted' % self )
		self.Pause()
		global SINGLE_OUTPUT_STREAM
		if self.__stream is SINGLE_OUTPUT_STREAM:
			if SINGLE_OUTPUT_STREAM._RemoveOutputCallback( self ) == 0: # if nobody is using it any more,
				SINGLE_OUTPUT_STREAM = True # let the global Stream instance get garbage-collected
		self.__stream = None


class Recorder( GenericInterface.GenericRecorder ):
	__doc__ =   GenericInterface.GenericRecorder.__doc__ # weirdly necessary for sphinx
	__stream = __verbose = None
	def __init__( self, seconds, device=None, stream=None, start=True, loop=False, verbose=None, **kwargs ):
		"""
		Args:
			seconds (float, Sound):
				number of seconds to pre-allocate for recording,
				or an already-pre-allocated `Sound` instance into
				which to record
				
			device (int, str, dict, Stream):
				specification of the device/stream to use for
				recording (as an index, name, full device record
				from `FindDevice()`, or already-open `Stream`
				instance)
				
			stream (int, str, dict, Stream):
				synonymous with `device`, for compatibility
			
			start (bool):
				whether to start recording immediately
			
			loop (bool):
				whether to record indefinitely, treating `self.sound`
				as a circular buffer, or simply stop when the capacity
				of `self.sound` is reached
							
			verbose (bool, None):
				verbosity for debugging. If `None`, inherit
				from the setting specified by `SetDefaultVerbosity()`,
				if any
				
			**kwargs:
				passed through to `.Set()` to initialize properties
				of the `Recorder` instance.
		"""
		if stream is None and device is not None: stream = device
		if device is None and stream is not None: device = stream
		if device != stream: raise ValueError( 'the `stream` and `device` arguments are synonymous---they cannot take different values unless one is left as `None`' )
		
		self.__stream = None
		self.__verbose = verbose
		if self.verbose: print( '%r is being initialized' % self )
		global SINGLE_INPUT_STREAM, DEFAULT_INPUT_DEVICE
		if stream is None: stream = DEFAULT_INPUT_DEVICE
		if SINGLE_INPUT_STREAM:
			alreadyInitialized = isinstance( SINGLE_INPUT_STREAM, Stream )
			if not isinstance( stream, Stream ):
				stream = FindDevice( id=stream, mode='i' if stream is None else None )[ 'index' ]
				if alreadyInitialized and stream == SINGLE_INPUT_STREAM.inputDevice[ 'index' ]: stream = SINGLE_INPUT_STREAM
				else: stream = Stream( device=stream, mode='i' )
			#if alreadyInitialized and stream and stream is not SINGLE_INPUT_STREAM: raise RuntimeError( 'cannot create multiple Streams' )
			self.__stream = stream if stream else SINGLE_INPUT_STREAM if alreadyInitialized else Stream( mode='i' )
			if not alreadyInitialized: SINGLE_INPUT_STREAM = self.__stream
		else:
			if stream is None: stream = DEFAULT_INPUT_DEVICE
			self.__stream = stream if isinstance( stream, Stream ) else Stream( device=stream, mode='i' )
		if not DEFAULT_INPUT_DEVICE: DEFAULT_INPUT_DEVICE = self.__stream.inputDevice[ 'index' ]
			
		stream = self.__stream
		super( Recorder, self ).__init__( seconds=seconds, fs=stream.fs, numberOfChannels=stream.nInputChannels, sampleFormat=stream.sampleFormat[ 'numpy' ], start=start, loop=loop, **kwargs )
		
		self.__stream._AddInputCallback( self._InputCallback )

	@property
	def stream( self ):
		return self.__stream
		
	@property
	def verbose( self ):
		if self.__verbose is not None: return self.__verbose
		return self.__stream.verbose if self.__stream else False
	@verbose.setter
	def verbose( self, value ):
		self.__verbose = value
	
	def __del__( self ):
		if self.verbose: print( '%r is being deleted' % self )
		self.Pause()
		global SINGLE_INPUT_STREAM
		if self.__stream is SINGLE_INPUT_STREAM:
			if SINGLE_INPUT_STREAM._RemoveInputCallback( self ) == 0: # if nobody is using it any more,
				SINGLE_INPUT_STREAM = True # let the global Stream instance get garbage-collected
		self.__stream = None


Record = Recorder.MakeRecording
