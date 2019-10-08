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
	'Sound',
	'TestSound',
	'Concatenate', 'Cat', 'Stack',
	'Silence', 'MakeRise', 'MakePlateau', 'MakeFall', 'MakeHannWindow',
	'SecondsToSamples', 'SamplesToSeconds',
	'ACROSS_SAMPLES', 'ACROSS_CHANNELS',
]

import os
import copy

from . import Dependencies; from .Dependencies import numpy

ACROSS_SAMPLES  = 0
ACROSS_CHANNELS = 1
DEFAULT_DTYPE_IN_MEMORY = 'f4'

class SoundBug( Exception ): pass

def IsActuallyNumpyArray( x ):
	return isinstance( x, numpy.ndarray )
def ActsLikeNumpyArray( x ):
	return hasattr( x, 'ndim' ) and hasattr( x, 'shape' ) and hasattr( x, 'size' )


DTYPES = dict(
	int8    = ( '<i1',  8, 1, True,  float( 2 **  7 ) ),
	int16   = ( '<i2', 16, 2, True,  float( 2 ** 15 ) ),
	int32   = ( '<i4', 32, 4, True,  float( 2 ** 31 ) ),
	int64   = ( '<i8', 64, 8, True,  float( 2 ** 63 ) ),
	uint8   = ( '<u1',  8, 1, False, float( 2 **  7 ) ), # yes that's correct
	uint16  = ( '<u2', 16, 2, False, float( 2 ** 15 ) ), # yes that's correct
	uint32  = ( '<u4', 32, 4, False, float( 2 ** 31 ) ), # yes that's correct
	uint64  = ( '<u8', 64, 8, False, float( 2 ** 63 ) ), # yes that's correct
	float32 = ( '<f4', 32, 4, True,  None ),
	float64 = ( '<f8', 64, 8, True,  None ),
)
for entry in list( DTYPES.values() ): DTYPES[ entry[ 0 ] ] = DTYPES[ entry[ 0 ][ 1: ] ] = entry
DTYPES[ None ] = DTYPES[ '<i2' ] # default

generator = type( ( x for x in '' ) )
def _AsSequence( x, breakStrings=False, breakArrays=False ):
	if not breakStrings and isinstance( x, str ): return [ x ]
	if not breakArrays and isinstance( x, numpy.ndarray ): return [ x ]
	if isinstance( x, ( dict, set ) ): return [ x ]
	if isinstance( x, generator ): return list( x )
	try: return list( x )
	except: return [ x ]
	
def _FlattenSequence( args, breakStrings=False, breakArrays=False ):
	return [ arg for item in args for arg in _AsSequence( item, breakStrings=breakStrings, breakArrays=breakArrays ) ]

def SecondsToSamples( seconds, fs, rounding='round' ):
	"""
	Convert seconds to samples given sampling frequency `fs`
	(expressed in Hz). `seconds` may be a scalar, or a
	sequence or array. The `rounding` approach may be
	`'floor'`, `'round'`, `'ceil'`, `'none'` or `'int'`.
	The `'int'` option rounds in the same way as `'floor'`
	but returns integers---all other options return
	floating-point numbers.
	
	See also: `SamplesToSeconds()`
	"""
	if hasattr( fs, 'fs' ): fs = fs.fs
	if seconds is None or fs is None: return None
	try: len( seconds )
	except: pass
	else: seconds = numpy.asarray( seconds, dtype=float )
	samples = seconds * ( fs / 1.0 )
	if rounding in [ 'int', int ]:
		try: samples = samples.astype( int )
		except: samples = int( samples )
	elif rounding == 'floor': samples = numpy.floor( samples )
	elif rounding == 'ceil':  samples = numpy.ceil( samples ) # just for completeness
	elif rounding in [ 'round', round ]: samples = numpy.round( samples )
	elif not rounding or rounding.lower() == 'none': pass
	else: raise ValueError( 'unrecognized `rounding` option %r' % rounding )
	return samples

def SamplesToSeconds( samples, fs ):
	"""
	Convert samples to seconds given sampling frequency
	`fs` (expressed in Hz). `samples` may be a scalar, or
	a sequence or array. The result is returned in
	floating-point.
	
	See also: `SecondsToSamples()`
	"""
	if hasattr(fs, 'fs'): fs = fs.fs
	if samples is None or fs is None: return None
	try: len( samples )
	except: pass
	else: samples = numpy.asarray( samples, dtype=float )
	return samples * ( 1.0 / fs )

def NumberOfSamples( a ):
	"""
	Return the number of samples in an array `a`, or in a
	`Sound` instance `a` that contains an array `a.y`.
	"""
	if hasattr( a, 'sound' ) and hasattr( a.sound, 'y' ) and hasattr( a.sound.y, 'shape' ): a = a.sound.y
	elif hasattr( a, 'y' ) and hasattr( a.y, 'shape' ): a = a.y
	try: len( a.shape )
	except: raise SoundBug( 'NumberOfSamples() function called on something other than a numpy.array' )
	if len( a.shape ) <= ACROSS_SAMPLES: return 1
	return a.shape[ ACROSS_SAMPLES ]

def NumberOfChannels(a):
	"""
	Return the number of channels in an array `a`, or in a
	`Sound` instance `a` that contains an array `a.y`.
	"""
	if hasattr( a, 'sound' ) and hasattr( a.sound, 'y' ) and hasattr( a.sound.y, 'shape' ): a = a.sound.y
	elif hasattr( a, 'y' ) and hasattr( a.y, 'shape' ): a = a.y
	try: len( a.shape )
	except: raise SoundBug( 'NumberOfChannels() function called on something other than a numpy.array' )
	if len( a.shape ) <= ACROSS_CHANNELS: return 1
	return a.shape[ ACROSS_CHANNELS ]

def infer_dtype( thing ):
	if hasattr( thing, 'sound' ) and hasattr( thing.sound, 'y' ) and hasattr( thing.sound.y, 'dtype' ): dtype = thing.sound.y.dtype
	elif hasattr( thing, 'y' ) and hasattr( thing.y, 'dtype' ): dtype = thing.y.dtype
	elif hasattr( thing, 'dtype' ): dtype = thing.dtype
	elif hasattr( thing, 'dtype_in_memory' ): dtype = thing.dtype_in_memory
	else: dtype = thing
	return dtype

def Silence( nsamp, nchan, dtype=DEFAULT_DTYPE_IN_MEMORY, dc=0 ):
	"""
	Return a `numpy.array` containing the specified number of
	samples `nsamp` x channels `nchan`, all set to a constant
	value `dc`.
	"""
	dtype = infer_dtype( dtype )
	if nsamp < 0: nsamp = 0
	z = numpy.zeros( _SubscriptHelper( int( round( nsamp ) ), int( round( nchan ) ) ), dtype )
	if dc: z += dc
	return z
	
def MakeRise( duration, fs=1000, hann=False ):
	"""
	Return a single-channel `Sound` object of the specified
	`duration` in seconds at the specified sampling frequency
	`fs` in Hz, containing a "fade-in" envelope (i.e. a ramp
	from 0 to 1). If `hann` is True, use a raised-cosine
	profile instead of a linear ramp.
	
	See also: `MakePlateau()`, `MakeFall()`, `MakeHannWindow()`
	"""
	y = numpy.linspace( 0.0, 1.0, SecondsToSamples( duration, fs ) ).astype( DEFAULT_DTYPE_IN_MEMORY )
	y = numpy.expand_dims( y, ACROSS_CHANNELS )
	if hann: y = 0.5 - 0.5 * numpy.cos( y * numpy.pi )
	return Sound( y, fs=fs )

def MakePlateau( duration, fs=1000, dc=1.0 ):
	"""
	Return a single-channel `Sound` object of the specified
	`duration` in seconds at the specified sampling frequency
	`fs` in Hz, containing a constant `dc` value.
	
	See also: `MakeRise()`, `MakeFall()`, `MakeHannWindow()`
	"""
	y = Silence( SecondsToSamples( duration, fs ), 1, dtype=DEFAULT_DTYPE_IN_MEMORY, dc=dc )
	return Sound( y, fs=fs )
	
def MakeFall( duration, fs=1000, hann=False ):
	"""
	Return a single-channel `Sound` object of the specified
	`duration` in seconds at the specified sampling frequency
	`fs` in Hz, containing a "fade-out" envelope (i.e. a ramp
	from 1 to 0). If `hann` is True, use a raised-cosine
	profile instead of a linear ramp.
	
	See also: `MakeRise()`, `MakePlateau()`, `MakeHannWindow()`
	"""
	y = numpy.linspace( 1.0, 0.0, SecondsToSamples( duration, fs ) ).astype( DEFAULT_DTYPE_IN_MEMORY )
	y = numpy.expand_dims( y, ACROSS_CHANNELS )
	if hann: y = 0.5 - 0.5 * numpy.cos( y * numpy.pi )
	return Sound( y, fs=fs )

def MakeHannWindow( duration, fs=1000, plateau_duration=0 ):
	"""
	Return a single-channel `Sound` object of the specified
	`duration` in seconds at the specified sampling frequency
	`fs` in Hz, containing a Hann or Tukey window---i.e. a
	raised-cosine "fade-in", followed by an optional plateau,
	followed by a raised-cosine "fade-out".
	
	See also: `MakeRise()`, `MakePlateau()`, `MakeFall()`
	"""
	risetime = ( float( duration ) - float( plateau_duration ) ) / 2.0
	r = MakeRise( risetime, fs=fs, hann=True )
	f = MakeFall( risetime, fs=fs, hann=True )
	ns = SecondsToSamples( duration, fs ) - r.NumberOfSamples() - f.NumberOfSamples()
	if ns > 0: p = Silence( ns, 1, dc=1.0 )
	else: p = 0.0
	return r % p % f

def Concatenate( *args ):
	"""
	Concatenate sounds in time, to make a new `Sound` instance
	containing a new array.

	You can also concatenate `Sound` instances using the `%`
	operator, and can modifying an existing `Sound` instance
	`s` (replacing its array `s.y`) using `%=`::
	
		s = s1 % s2
		s %= s1
	
	Note that, in the above examples, either `s1` or `s2` may
	also be a numeric scalar:  `s %= 0.5` appends half a second
	of silence to `s`.
	"""
	args = _FlattenSequence( args )
	nchan = 1
	fs = None
	s = None
	for arg in args:
		if isinstance( arg, Sound ):
			if s is None: s = arg.copy()

			if nchan == 1: nchan = arg.NumberOfChannels()
			elif not arg.NumberOfChannels() in ( 1, nchan ): raise ValueError( 'incompatible numbers of channels' )

			if fs is None: fs = float( arg.fs )
			elif fs != arg.fs: raise ValueError( 'incompatible sampling frequencies' )
	if s is None:
		raise TypeError( 'no Sound object found' )
	for i, arg in enumerate( args ):
		if isinstance(arg, Sound):
			dat = arg.y
			if NumberOfChannels(dat) == 1 and nchan > 1:
				dat = dat.repeat(nchan, axis=ACROSS_CHANNELS)
		elif isinstance(arg, numpy.ndarray):
			dat = arg
		elif isinstance(arg,float) or isinstance(arg,int):
			nsamp = round(float(arg) * fs)
			nsamp = max(0, nsamp)
			dat = Silence(nsamp, nchan, s)
		else:
			raise TypeError( "don't know how to concatenate type %s" % arg.__class__.__name__ )
		args[i] = dat
	s.y = numpy.concatenate( args, axis=ACROSS_SAMPLES )
	return s
Cat = Concatenate

def Stack( *args ):
	"""
	Stack multiple Sound objects to make a new multi-channel
	`Sound` object (appending silence to the end of each
	argument where necessary to equalize lengths).
	
	You can also stack channels of `Sound` instances using
	the `&` operator, and can modifying an existing `Sound`
	instance `s` (replacing its array `s.y`) using `&=`::
	
		s = s1 & s2
		s &= s1
	"""
	args = _FlattenSequence( args )
	for arg in args:
		if not isinstance( arg, Sound ): raise TypeError( "arguments must be Sound objects (or sequences thereof)" )
	out = args.pop( 0 ).copy()
	while args: out &= args.pop( 0 )
	return out	

def _SubscriptHelper( samples=None, channels=None ):
	subs = [ None, None ]
	subs[ ACROSS_SAMPLES ] = samples
	subs[ ACROSS_CHANNELS ] = channels
	return tuple( subs )

def _PanHelper( v, nchan=None, norm='inf' ):
	
	try:
		nchan = int( nchan )
	except:
		if nchan is not None: nchan = NumberOfChannels( nchan )
	
	if isinstance( v, ( tuple, list, numpy.ndarray ) ):
		v = numpy.array( v, dtype='float' )
		v = v.ravel()
		if len( v )==1:
			v = float( v[ 0 ] ) # scalar numpy value
		else:
			# Interpret any kind of multi-element tuple/list/array
			# as a per-channel list of volumes. Just standardize its
			# shape and size. Ignore the `norm` parameter.
			if nchan is None: nchan = len( v )
			elif len( v ) < nchan: v = numpy.tile( v, numpy.ceil( float( nchan ) / len( v ) ) )
			if len( v ) > nchan: v = v[ :nchan ]
			v.shape = _SubscriptHelper( 1, nchan )
	else:
		v = float( v ) # could be converting from a custom class with a __float__ method
		
	if isinstance( v, float ):
		# Interpret any kind of scalar as a stereo pan value in the
		# range -1 to +1. Normalize according to the specified `norm`.
		if nchan is None: nchan = 2
		v = 0.5 + 0.5 * numpy.clip( [ -v, v ], -1.0, 1.0 )
		if nchan > 2: v = numpy.tile( v, int( nchan / 2 ) )
		if len( v ) == nchan - 1: v = numpy.concatenate( ( v, [ 1.0 ] ) )
		if isinstance( norm, str)  and norm.lower() == 'inf': norm = numpy.inf
		if norm in [ numpy.inf, 'inf', 'INF' ]: v /= max( v )
		else: v /= sum( v ** norm ) ** ( 1.0 / { 0.0:1.0 }.get( norm, norm ) )
		v = _PanHelper( v, nchan=nchan )

	return v

def _InterpolateSamples( y, xi ):
	x = numpy.arange( float( NumberOfSamples( y ) ) )
	yi = numpy.zeros( _SubscriptHelper( len( xi ), NumberOfChannels( y ) ), dtype='float' )
	sub = [ slice( None ), slice( None ) ]
	for sub[ ACROSS_CHANNELS ] in range( NumberOfChannels( y ) ):
		tsub = tuple( sub )
		yi[ tsub ] = numpy.interp( x=xi, xp=x, fp=y[ tsub ] )
	return yi

def _ChannelIndices( *indices ):
	return [ 
		int( index ) - int( isinstance( index, str ) )
		for item in indices
		for index in (
			item if isinstance( item, ( tuple, list, str ) ) else [ item ]
		)
	]

class Sound( object ):
	"""
	`Sound` is a class for editing and writing sound files.
	(If your main aim is simply to play back existing sounds
	from disk, you probably want to start with a `Player`
	instead.)
	
	A `Sound` instance `s` is a wrapper around a numpy array
	`s.y` which contains a floating-point representation of
	a (possibly multi-channel) sound waveform. Generally the
	array values are in the range [-1, +1].

	The wrapper makes it easy to perform certain common
	editing and preprocessing operations using Python
	operators, such as:
	
	Numerical operations:
	
		- The `+` and `-` operators can be used to superimpose
		  sounds (even if lengths do not match).
		  
		- The `*` and `/` operators can be used to scale
		  amplitudes (usually by a scalar numeric factor, but
		  you can also use a list of scaling factors to scale
		  channels separately, or window a signal by multiplying
		  two objects together).
		  
		- The `+=`, `-=`, `*=` and `/=` operators work as you
		  might expect, modifying a `Sound` instance's data array
		  in-place.
	 
	Concatenation of sound data in time:
	
		The syntax `s1 % s2` is the same as `Concatenate( s1, s2 )`:
		it returns a new `Sound` instance containing a new array
		of samples, in which the samples of `s1` and `s2` are
		concatenated in time.
		
		Either argument may be a scalar,  so `s % 0.4` returns a
		new object with 400 msec of silence appended, and `0.4 % s`
		returns a new object with 400 msec of silence pre-pended.
	
		Concatenation can be performed in-place with `s %= arg`
		or equivalently using the instance method
		`s.Concatenate( arg1, arg2, ... )`: in either case the
		instance `s` gets its internal sample array replaced by
		a new array.
	
	Creating multichannel objects:
	
		The syntax `s1 & s2` is the same as `Stack( s1, s2 )`:
		it returns a new `Sound` instance containing a new array
		of samples, comprising the channels of `s1` and the
		channels of `s2`. Either one may be automatically
		padded with silence at the end as necessary to ensure
		that the lengths match.
		
		Stacking may be performed in-place with `s1 &= s2` or
		equivalently with the instance method
		`s1.Stack( s2, s3, ... )`:  in either case instance
		`s1` gets its internal sample array replaced by a new
		array.

	Slicing, expressed in units of seconds:
	
		The following syntax returns Sound objects wrapped
		around slices into the original array::

			s[:0.5]   #  returns the first half-second of `s`
			s[-0.5:]  #  returns the last half-second of `s`
			
			s[:, 0]   # returns the first channel of `s`
			s[:, -2:] # returns the last two channels of `s`
			s[0.25:0.5, [0,1,3]] # returns a particular time-slice of the chosen channels
			
		Where possible, the resulting `Sound` instances'
		arrays are *views* into the original sound data.
		Therefore, things like  `s[2.0:-1.0].AutoScale()`
		or  `s[1.0:2.0] *= 2` will change the specified
		segments of the *original* sound data in `s`.
		Note one subtlety, however::
		
		    # Does each of these examples modify the selected segment of `s` in-place?
		                                      
			s[0.1:0.2,  :] *= 2            # yes
			q = s[0.1:0.2,  :];  q *= 2    # yes  (`q.y` is a view into `s.y`)
			
			s[0.1:0.2, ::2] *= 2           # yes
			q = s[0.1:0.2, ::2];  q *= 2   # yes  (`q.y` is a view into `s.y`)
			
			s[0.1:0.2, 0] *= 2             # yes (creates a copy, but then uses `__setitem__` on the original)
			q = s[0.1:0.2, 0];  q *= 2     # - NO (creates a copy, then just modifies the copy in-place)
			
			s[0.1:0.2, [1,3]] *= 2         # yes (creates a copy, but then uses `__setitem__` on the original)
			q = s[0.1:0.2, [1,3]];  q *= 2 # - NO (creates a copy, then just modifies the copy in-place)
	
	"""
	
	def __init__(self, source=None, fs=None, nchan=2, dtype=None, bits=None, label=None ):
		"""
		A `Sound` instance may be constructed in any of the
		following ways::
		
			s = Sound( '/path/to/some/sound_file.wav' )
			s = Sound( some_other_Sound_instance )   # creates a shallow copy
			s = Sound( y, fs )                       # where `y` is a numpy array
			s = Sound( duration_in_seconds, fs )     # creates silence
			s = Sound( raw_bytes, fs, nchan=2 )
				
		Args:
			source:
				a filename, another `Sound` instance, a `numpy`
				array, a scalar numeric value indicating the
				desired duration of silence in seconds, or a
				buffer full of raw sound data, as in the examples
				above.
			
			fs (float):
				sampling frequency, in Hz. If `source` is a
				filename or another `Sound` instance, the default
				value will be inferred from that source. Otherwise
				the default value is 44100.
			
			nchan (int):
				number of channels.   If `source` is a filename,
				another `Sound` instance, or a `numpy` array, the
				default value will be inferred from that source.
				Otherwise the default value is 2.
			
			dtype (str):
				Sound data are always represented internally in
				floating-point. However, the `dtype` argument
				specifies the `Sound` instance's `.dtype_encoded`
				property, which dictates the format in which
				the instance imports or exports raw data by
				default.
			
			bits (int):
				This is another way of initializing the instance's
				`.dtype_encoded` property (see `dtype`, above),
				assuming integer encoding. It should be 8, 16, 24
				or 32.   If `dtype` is specified, this argument
				is ignored.  Otherwise, the default value is 16.
			
			label (str):
				An optional string to be assigned to the `.label`
				attribute of the `Sound` instance. 
		"""
		if nchan is None: nchan = 2
		if isinstance( nchan, Sound ) or ActsLikeNumpyArray( nchan ): nchan = NumberOfChannels( nchan )
		if isinstance( dtype, Sound ): dtype = dtype.dtype_encoded
		elif ActsLikeNumpyArray( dtype ): dtype = dtype.dtype
		
		self.__y = numpy.zeros( ( 0, nchan ), dtype=DEFAULT_DTYPE_IN_MEMORY )
		self.__fs = None
		self.__revision = 0
		self.__compression = ( 'NONE', 'not compressed' )
		self.__dtype_encoded = None
		self._wavFileHandleOpenForWriting = None

		self.filename = None
		self.label = label
		
		if isinstance( source, Sound ):
			self.__y = source.__y
			self.__fs = source.__fs
			self.filename = source.filename
			self.label = source.label
			self.__compression = source.__compression
			self.__dtype_encoded = source.__dtype_encoded
			source = None
		
		if dtype: self.dtype_encoded = dtype
		if self.__dtype_encoded is None and bits is None: bits = 16
		if bits is not None: self.bits = bits   # NB: changes self.__dtype_encoded
		
		if self.__fs is None and fs is None:
			if hasattr( source, 'fs' ): fs = source.fs  # convenience for wrapping Synth objects
			else: fs = 44100
		if fs is not None:
			if hasattr( fs, 'fs' ): fs = fs.fs
			self.fs = fs

		if isinstance( source, ( int, float ) ): self.y = Silence( SecondsToSamples( source, self ), nchan, dtype=dtype )
		elif ActsLikeNumpyArray( source ): self.y = source
		elif source is not None:
			self.Read( source )
			if self.label is None and self.filename:
				self.label = os.path.splitext( os.path.basename( self.filename ) )[ 0 ]

	
	def Copy( self, empty=False ):
		"""
		Create a new `Sound` instance whose array `.y` is
		a deep copy of the original instance's array. With
		`empty=True` the resulting array will be empty,
		but will have the same number of channels as the
		original.
		
		Note that most other preprocessing methods return
		`self` as their output argument.  This makes it
		easy to choose between modifying an instance in-
		place and creating a modified copy. For example::
		
			s.Reverse()             # reverse `s` in-place
			t = s.Copy().Reverse()  # create a reversed copy of `s`
		
		"""
		y = self.__y
		if empty and y is not None: self.__y = y[ :0 ]
		c = copy.deepcopy( self )
		self.__y = y
		return c
	copy = Copy
	
	@property
	def y( self ):
		"""
		`numpy` array containing the actual sound sample data.
		"""
		return self.__y
	@y.setter
	def y( self, value ):
		if not ActsLikeNumpyArray( value ): value = numpy.array( value, dtype=DEFAULT_DTYPE_IN_MEMORY )
		if value.ndim > 2: raise ValueError( "too many dimensions" )
		while value.ndim < 2: value = value[ :, None ]
		self.__y = value
	
	@property
	def fs( self ):
		"""
		Sampling frequency, in Hz.
		"""
		return self.__fs
	@fs.setter
	def fs( self, value ):
		if hasattr( value, 'fs' ): value = value.fs
		self.__fs = float( value )
	
	@property
	def revision( self ): return self.__revision
	
	@property
	def compression( self ): return self.__compression
	@compression.setter
	def compression( self, value ):
		if not isinstance( value, ( tuple, list ) ) or len( value ) != 2 or not isinstance( value[ 0 ], str ) or not isinstance( value[ 1 ], str ):
			raise ValueError( ".compression must be a sequence of two strings" )
		self.__compression = value
	
	@property
	def bits( self ):
		"""
		Bit depth of each sample in each channel, *when encoded*
		(not necessarily as represented in memory for manipulation
		and visualization).
		"""
		canonical_dtype, nbits, nbytes, signed, factor = DTYPES[ self.__dtype_encoded ]; return nbits
	@bits.setter
	def bits( self, value ): self._SetBitDepth( value )
	nbits = bits
	
	@property
	def bytes( self ):
		"""
		Numner of bytes used to represent each sample of each channel,
		*when encoded* (not necessarily as represented in memory for
		manipulation and visualization).
		"""
		return int( numpy.ceil( self.bits / 8.0 ) )
	nbytes = bytes
	
	@property
	def dtype_encoded( self ): return self.__dtype_encoded
	@dtype_encoded.setter
	def dtype_encoded( self, value ): canonical_dtype, nbits, nbytes, signed, factor = DTYPES[ value ]; self.__dtype_encoded = canonical_dtype
	
	@property
	def dtype_in_memory( self ): return self.__y.dtype.name
	@dtype_in_memory.setter
	def dtype_in_memory( self, value ): self.__y = self.__y.astype( value )
	
	def _SetBitDepth(self, bits):
		if   bits ==  8: dtype = '<u1'  # yep
		elif bits == 16: dtype = '<i2'
		elif bits == 24: dtype = '<i4'
		elif bits == 32: dtype = '<i4'
		elif isinstance( bits, str ): dtype = bits.lower()
		else: raise ValueError( 'unrecognized bit precision' )
		
		dtype, nbits, nbytes, signed, factor = DTYPES[ dtype ]
		if dtype != self.__dtype_encoded: self._BumpRevision()
		self.__dtype_encoded = dtype

	def Bulk( self, encoded=False ):
		"""
		Return the number of bytes occupied by the sound
		waveform...
		
		`encoded=False`:
			...currently, in memory.
			
		`encoded=True`:
			...if it were to be encoded according to the
			currently-specified `.dtype_encoded` and written
			to disk in an uncompressed format (excluding
			the bytes required to store any format header).
		"""
		return self.y.size * ( self.bytes if encoded else self.y.dtype.itemsize )

	def NumberOfChannels( self ):
		"""
		Returns the number of channels.
		"""
		return NumberOfChannels( self )
		
	def NumberOfSamples( self ):
		"""
		Returns the length of the sound in samples.
		"""
		return NumberOfSamples( self )
	
	def Duration(self):
		"""
		Returns the duration of the sound in seconds.
		"""
		return float( self.NumberOfSamples() ) / float( self.fs )
	
	def Amplitude( self, norm=2, threshold=0.0 ):
		"""
		Returns a 1-D `numpy` array containing the estimated amplitude
		of each channel.  With `norm=2`, that's the root-mean-square
		amplitude, whereas `norm=1` would get you the mean-absolute
		amplitude.
		
		Note that, depending on the content, the mean may reflect
		not only how loud the content is *when* it happens, but also
		how often it happens.  For example, loud speech with a lot of
		pauses might have a lower RMS than continuous quiet speech.
		This would make it difficult to equalize the volumes of the
		two speech signals. To work around this, use the `threshold`
		argument. It acts as a noise-gate: in each channel, the
		average will only include samples whose absolute value reaches
		or exceeds `threshold` times that channel's maximum (so the
		`threshold` value itself is relative, expressed as a proportion
		of each channel's maximum---this makes the noise-gate invariant
		to simple rescaling).
		"""
		y = [ abs( channel.y ) for channel in self.SplitChannels() ]
		norm = float( norm )
		if numpy.isinf( norm ): amp = [ yi.max() for yi in y ]
		elif norm == 0: amp = [ ( yi > threshold * yi.max() ).mean() for yi in y ]
		else: amp = [ ( yi[ yi >= threshold * yi.max() ] ** norm ).mean() ** ( 1. / norm ) for yi in y ]
		return numpy.array( amp )
			
	rms = property( Amplitude )
		
	nChannels = numberOfChannels = nchan = property( NumberOfChannels )
	nSamples  = numberOfSamples  = nsamp = property( NumberOfSamples  )
	duration  = property( Duration )
		
	def __repr__(self):
		s = "<%s.%s instance at 0x%08X>" % ( self.__class__.__module__, self.__class__.__name__, id( self ) )
		if self.label or self.filename: s += '\n   '
		if self.label: s += ' label: %s' % self.label
		if self.filename: s += ' (file %s)' % self.filename
		s += '\n'
		s += '    %g bits, %g channels, %s samples @ %g Hz = %g sec' % ( self.bits, self.NumberOfChannels(), self.NumberOfSamples(), self.fs, self.Duration() )
		return s
			
	def str2dat( self, raw, nsamp=None, nchan=None, dtype=None ):
		if dtype is None: dtype = self.__dtype_encoded
		else: dtype = dtype.lower()
		canonical_dtype, nbits, nbytes, signed, factor = DTYPES[ dtype ]
		if nchan is None: nchan = self.NumberOfChannels()
		y = numpy.fromstring( raw, dtype=canonical_dtype )
		if nsamp is None: nsamp = int( y.size / nchan )
		y.shape = ( nsamp, nchan )
		y = y.astype( self.dtype_in_memory )
		if factor:
			if not signed: y -= factor
			y /= factor
		return y

	def dat2str(self, data=None, dtype=None):
		"""
		Converts from a `numpy.array` to a string. `data`
		defaults to the whole of `s.y`
		
		The string output contains raw bytes which can be
		written, for example, to an open audio stream.
		"""
		if isinstance(data,str): return data
		if data is None: data = self.y
		if dtype is None: dtype = self.__dtype_encoded
		else: dtype = dtype.lower()
		canonical_dtype, nbits, nbytes, signed, factor = DTYPES[ dtype ]
		nchan = NumberOfChannels(data)
		nsamp = NumberOfSamples(data)
		if nchan != self.NumberOfChannels():
			raise ValueError( 'data has a different number of channels from object' )
		if factor:
			data = data * factor
			data = numpy.clip(data, -factor, factor - 1)
			if not signed: data += factor
			#data += 0.5 # in principle the astype method should perform a floor() operation, so adding 0.5 first should be a good idea. however, for some reason it doesn't correctly reconstruct the original raw data when this is added
		data = data.astype( dtype )
		data = data.tostring()
		return data

	def Concatenate( self, *args ):
		"""
		Concatenate the instance, in time, with the specified
		arguments (which may be other `Sound` instances and/or
		numpy arrays and/or numeric scalars indicating durations
		of silent intervals in seconds). Replace the sample
		array `self.y` with the result. Similar results can be
		obtained with the `%=` operator or the global function
		`Concatenate()`.
		"""
		s = Concatenate( self, *args )
		self.y = s.y
		return self._BumpRevision()
	Cat = Concatenate
	
	def Stack( self, *args ):
		"""
		Stack the instance, across channels, with the specified
		arguments (which may be other `Sound` instances and/or
		numpy arrays). Replace the sample array `self.y` with
		the result. Similar results can be obtained with the
		`&=` operator or the global function `Stack()`.
		"""
		args = _FlattenSequence( args )
		while args: self &= args.pop( 0 )
		return self._BumpRevision()
		
	def AutoScale( self, max_abs_amp=0.95 ):
		"""
		Remove the median from each channel (see `.Center()`)
		and then rescale the waveform so that its maximum
		absolute value (across all channels) is `max_abs_amp`.
		The array `self.y` is modified in place.
		"""
		self.Center()
		m = abs( self.y ).max()
		self.y *= ( max_abs_amp / m )
		return self._BumpRevision()
	
	def Center( self ):
		"""
		Remove the DC offset from each channel by subtracting
		the median value.
		"""
		try: med = numpy.median( self.y, axis=ACROSS_SAMPLES ) # newer numpy versions only
		except: med = numpy.median( self.y ) # older numpy versions only (grr!)
		self.y -= numpy.expand_dims( med, ACROSS_SAMPLES )
		return self._BumpRevision()
		
	def Reverse( self ):
		"""
		Reverse the sound in time. The array `self.y` is 
		modified in-place.
		"""
		self.y.flat = self.y[ _SubscriptHelper( slice( None, None, -1 ), slice( None ) ) ].flat
		return self._BumpRevision()			
	
	def Fade( self, risetime=0, falltime=0, hann=False ):
		"""
		If `risetime` is greater than zero, it denotes the
		duration (in seconds) over which the sound is to be
		faded-in at the beginning.
		
		If `falltime` is greater than zero, it denotes the
		duration of the corresponding fade-out at the end.
		
		If `hann` is true, then a raised-cosine function is
		used for fading instead of a linear ramp.
		
		The array `self.y` is modified in-place.
		"""
		if risetime: self[ :float( risetime ) ]  *= MakeRise( risetime, fs=self.fs, hann=hann )
		if falltime: self[ -float( falltime ): ] *= MakeFall( falltime, fs=self.fs, hann=hann )
		return self._BumpRevision()
	
	def Cut( self, start=None, stop=None, units='seconds' ):
		"""
		Shorten the instance's internal sample array by taking
		only samples from `start` to `stop`.  Either end-point
		may be `None`. Either may be a positive number of
		seconds (measured from the start) or a negative number
		of seconds (measured from the end).
		"""
		nSamples = NumberOfSamples( self )
		if   units in [ 's', 'sec', 'seconds' ]: fs = float( self.fs )
		elif units == 'samples': fs = 1.0
		elif units in [ 'ms', 'msec', 'milliseconds' ]: fs = self.fs / 1000.0
		else: raise ValueError( 'unrecognized `units` option %r' % units )
		if start is None: start = 0.0
		if  stop is None:  stop = nSamples / fs
		if start < 0.0: start += nSamples / fs
		if  stop < 0.0:  stop += nSamples / fs
		start = max( 0,        int( round( start * fs ) ) )
		stop  = min( nSamples, int( round(  stop * fs ) ) )
		stop = max( start, stop )
		self.y = self.y[ _SubscriptHelper( slice( start, stop ), slice( None ) ) ].copy()
		return self._BumpRevision()
		
	def Trim(self, threshold=0.05, tailoff=0.2, buildup=0):
		"""
		Remove samples from the beginning and end of a sound,
		according to amplitude.
		
		The new waveform will start `buildup` seconds prior to
		the first sample on which the absolute amplitude in any
		channel exceeds `threshold`. It will end `tailoff`
		seconds after the *last* sample on which `threshold` is
		exceeded.
		"""
		y = numpy.max(abs(self.y), axis=ACROSS_CHANNELS)
		start,stop = numpy.where(y>threshold)[0][[0,-1]]
		start -= round(float(buildup) * float(self.fs))
		start = max(start, 0)
		stop += round(float(tailoff) * float(self.fs))
		stop = min(stop, self.NumberOfSamples())
		return self.Cut( start, stop, units='samples' )
		
	def IsolateChannels( self, ind, *moreIndices ):
		"""
		Select particular channels, discarding the others.
		The following are all equivalent, for selecting the
		first two channels::
		
			t = s.IsolateChannels(0, 1)       # ordinary 0-based indexing
			t = s.IsolateChannels([0, 1])
			t = s.IsolateChannels('1', '2')   # when you use strings, you
			t = s.IsolateChannels(['1', '2']) # can index the channels
			t = s.IsolateChannels('12')       # using 1-based numbering
		
		Equivalently, you can also use slicing notation,
		selecting channels via the second dimension::
		
			t = s[:, [0, 1]]
			t = s[:, '12'] # again, strings mean 1-based indexing
		
		"""
		ind = _ChannelIndices( ind, *moreIndices )
		self.y = self.y[ _SubscriptHelper( slice( None ), ind ) ]
		return self._BumpRevision()
	
	def MixDownToMono(self):
		"""
		Average the sound waveforms across all channels,
		replacing `self.y` with the single-channel result.
		"""
		self.y = numpy.expand_dims( self.y.mean( axis=ACROSS_CHANNELS ), ACROSS_CHANNELS )
		return self._BumpRevision()
	
	def PadEndTo(self, seconds):
		"""
		Append silence to the instance's internal array as
		necessary to ensure that the total duration is at
		least the specified number of `seconds`.
		"""
		if isinstance(seconds, Sound):
			seconds = seconds.Duration()
		extra_sec = seconds - self.Duration()
		if extra_sec > 0.0:
			s = Concatenate(self, extra_sec)
			self.y = s.y
		return self._BumpRevision()
	
	def PadStartTo(self, seconds):
		"""
		Prepend silence to the instance's internal array as
		necessary to ensure that the total duration is at
		least the specified number of `seconds`.
		"""
		if isinstance(seconds, Sound):
			seconds = seconds.Duration()
		extra_sec = seconds - self.Duration()
		if extra_sec > 0.0:
			s = Concatenate(extra_sec, self)
			self.y = s.y
		return self._BumpRevision()
	
	def Resample( self, newfs ):
		"""
		Change the instance's sampling frequency. Replace
		its internal array with a new array, interpolated
		at the new sampling frequency `newfs` (expressed
		in Hz).
		"""
		if hasattr( newfs, 'fs' ): newfs = newfs.fs
		if newfs != self.fs:
			newN = self.NumberOfSamples() * newfs / self.fs
			self.y = _InterpolateSamples( self.y, numpy.linspace( 0, self.NumberOfSamples(), newN, endpoint=False ) )
			self.fs = newfs
		return self._BumpRevision()

	def Left( self ):
		"""
		Return a new `Sound` instance containing a view of
		alternate channels, starting at the first.
		"""
		s = self.copy() # new instance...
		alternate = slice( 0, None, 2 )
		s.y = self.y[ _SubscriptHelper( slice( None ), alternate ) ]  # ...but a view into the original array
		return s

	def Right( self ):
		"""
		Return a new `Sound` instance containing a view of
		alternate channels, starting at the second (unless
		there is only one channel, in which case return that).
		"""
		s = self.copy() # new instance...
		alternate = slice( 1 if self.NumberOfChannels() > 1 else 0, None, 2 )
		s.y = self.y[ _SubscriptHelper( slice( None ), alternate ) ]  # ...but a view into the original array
		return s
		
	def SplitChannels( self, nChannelsEach=1 ):
		"""
		Return a list of new `Sound` instances, each
		containing a view into the original data, each
		limited to `nChannelsEach` consecutive channels.
		"""
		return [ self[ :, start : start + nChannelsEach ] for start in range( 0, self.NumberOfChannels(), nChannelsEach ) ]
	

	def _BumpRevision(self):
		self.__revision += 1
		return self
		
	def _PrepareForArithmetic( self, other, equalize_channels=True, equalize_duration=True ):
		if IsActuallyNumpyArray( other ) and other.ndim <= 1 and other.size <= 32:
			other = other.tolist()
		if isinstance( other, Sound ):
			if self.fs != other.fs:
				raise ValueError( 'incompatible sampling rates' )
			other = other.y
		me = self.y
		if isinstance( other, list ) and False not in [ isinstance( x, ( bool, int, float ) ) for x in other ]:
			other = numpy.concatenate( [ numpy.asmatrix( x, dtype=numpy.float64 ).A for x in other ], axis=ACROSS_CHANNELS )
			equalize_duration = False
		if IsActuallyNumpyArray( other ):
			if other.ndim == 1: other = numpy.expand_dims( other, ACROSS_CHANNELS )
			if equalize_channels:
				if NumberOfChannels( other ) == 1 and NumberOfChannels( me ) > 1:
					other = other.repeat( NumberOfChannels( me ), axis=ACROSS_CHANNELS )
				if NumberOfChannels( other ) > 1 and NumberOfChannels( me ) == 1:
					me = me.repeat( NumberOfChannels( other ), axis=ACROSS_CHANNELS )
			nchan_me = NumberOfChannels( me )
			nchan_other = NumberOfChannels( other )
			if equalize_channels and nchan_other != nchan_me:
				raise ValueError( 'incompatible numbers of channels' )
			if equalize_duration:
				needed = NumberOfSamples( other ) - NumberOfSamples( me )
				if needed > 0:
					extra = Silence( needed, nchan_me, me )
					me = numpy.concatenate( ( me, extra ), axis=ACROSS_SAMPLES )
				if needed < 0:
					extra = Silence( -needed, nchan_other, other )
					other = numpy.concatenate( ( other, extra ), axis=ACROSS_SAMPLES )
		return ( me, other )
	
	# addition, subtraction
	def __iadd__( self, other ):
		( me, other ) = self._PrepareForArithmetic( other )
		me += other
		self.y = me
		self._BumpRevision()
		return self
	def __add__( self, other ):
		return self.copy().__iadd__( other )
	def __radd__( self, other ):
		return self.__add__( other )
	def __isub__(self, other):
		( me, other ) = self._PrepareForArithmetic( other )
		me -= other
		self.y = me
		self._BumpRevision()
		return self
	def __sub__( self, other ):
		return self.copy().__isub__( other )
	def __rsub__( self, other ):
		s = self.__mul__( -1 )
		s.__iadd__( other )
		return s

	# multiplication, division
	def __imul__( self, other ):
		( me, other ) = self._PrepareForArithmetic( other )
		me *= other
		self.y = me		
		self._BumpRevision()
		return self
	def __mul__( self, other ):
		return self.copy().__imul__( other )
	def __rmul__( self, other ):
		return self.__mul__( other )
	def __idiv__( self, other ):
		( me, other ) = self._PrepareForArithmetic( other )
		me /= other
		self.y = me		
		self._BumpRevision()
		return self
	def __div__( self, other ):
		return self.copy().__idiv__( other )
	__truediv__ = __div__
	__itruediv__ = __idiv__

	# Channel-stacking using the & operator
	def __iand__( self, other ):
		if not ( isinstance( other, Sound ) or IsActuallyNumpyArray( other ) ):
			raise TypeError( 'w1 & w2 only works if w1 and w2 are both wavs, or if w2 is a numpy.array' )
		( me, other ) = self._PrepareForArithmetic( other, equalize_channels=False )
		if me.size == 0: me = other
		elif other.size: me = numpy.concatenate( ( me, other ), axis=ACROSS_CHANNELS )
		self.y = me
		self._BumpRevision()
		return self
	def __and__( self, other ):
		return self.copy().__iand__( other )
	
	# Concatenation using the % operator
	def __imod__( self, other ):
		self.Concatenate( other )
		self._BumpRevision()
		return self
	def __mod__( self, other ):
		return Concatenate( self, other )
	def __rmod__( self, other ):
		return Concatenate( other, self )

	# Unary + and - (both cause data to be deep-copied)
	def __neg__( self ): return -1.0 * self
	def __pos__( self ): return self.copy()

	# Slicing with [] indexing, (first ranges expressed in seconds, second channel index or range):
	def __getitem__(self, range):
		subs = self._TranslateSlice(range)
		s = Sound(fs=self.fs, bits=self.bits, nchan=NumberOfChannels(self))
		s.y = self.y[subs[0],subs[1]]
		return s

	def __setitem__(self, range, val):
		subs = self._TranslateSlice(range)
		if isinstance(val,Sound): val = val.y
		self.y[subs[0],subs[1]] = val
		self._BumpRevision()

	def _TranslateSlice( self, range ):
		chans = slice( None )
		if isinstance( range, ( tuple, list ) ):
			range, chans = range
			if not isinstance( chans, ( int, slice ) ): chans = _ChannelIndices( chans )
		if not isinstance( range, slice ): raise TypeError( 'indices must be ranges, expressed in seconds' )

		start, stop, step = None, None, None
		if range.step is not None:
			raise ValueError( 'custom step sizes are not possible when slicing %s objects in time' % self.__class__.__name__ )
		if range.start is not None:
			start = int( SecondsToSamples( range.start, self ) )
			if range.stop is not None:
				stop = min( range.stop, self.Duration() )
				duration = float( stop ) - float( range.start )
				stop  = int( SecondsToSamples( duration, self ) ) + start
		elif range.stop is not None:
			stop = int( SecondsToSamples( range.stop, self ) )

		return _SubscriptHelper( slice( start, stop, step ), chans )
	
	def SecondsToSamples( self, seconds, rounding='round' ):
		"""
		Convert seconds to samples given the `Sound` instance's
		sampling frequency. `seconds` may be a scalar, or a
		sequence or array. The `rounding` approach may be
		`'floor'`, `'round'`, `'ceil'`, `'none'` or `'int'`.
		The `'int'` option rounds in the same way as `'floor'`
		but returns integers---all other options return
		floating-point numbers.
	
		See also: `.SamplesToSeconds()`
		"""
		return SecondsToSamples( seconds, self, rounding=rounding )
		
	def SamplesToSeconds( self, samples ):
		"""
		Convert samples to seconds given at the sampling
		frequency of the instance. `samples` may be a scalar,
		or a sequence or array. The result is returned in
		floating-point.
	
		See also: `.SecondsToSamples()`
		"""
		return SamplesToSeconds( samples, self )
	
	def MakeHannWindow( self, plateau_duration=0 ):
		"""
		Return a single-channel `Sound` object of the same
		duration and sampling frequency as `self`, containing
		a Hann or Tukey window---i.e. a raised-cosine "fade-in",
		followed by an optional plateau, followed by a raised-
		cosine "fade-out".
		"""
		return MakeHannWindow( duration=self.Duration(), fs=self.fs, plateau_duration=plateau_duration )
		
	def Play( self, *pargs, **kwargs ):
		"""
		This quick-and-dirty method allows you to play a
		`Sound`. It creates a `Player` instance in verbose mode,
		uses it to play the sound, waits for it to finish (or
		for the user to press ctrl-C), then destroys the `Player`
		again.
		
		You will get a better user experience, and better
		performance, if you explicitly create a `Player`
		instance of your own and work with that.
		
		Arguments are passed through to the `Player.Play()`
		method.
		"""
		from . import BackEnd; from .BackEnd import CURRENT_BACK_END as impl
		p = impl.Player( self, verbose=True )
		p.Play( *pargs, **kwargs )
		p.Wait()
	
Sound.ACROSS_SAMPLES  = ACROSS_SAMPLES
Sound.ACROSS_CHANNELS = ACROSS_CHANNELS

def TestSound( *channels ):
	"""
	Return an 8-channel `Sound` object, read from a `.wav`
	file that is bundled with `audiomath`, suitable for
	testing multi-channel sound output devices. Optionally,
	you can select particular channels using the same
	argument conventions as the `.IsolateChannels()` method.
	For example, you could choose to return only the first
	two channels, as follows::
	
		s = TestSound('12')
	"""
	s = Sound( 'test12345678' )
	if channels:
		channels = _ChannelIndices( *channels )
		s.IsolateChannels( channels )
		s.label = 'test' + ''.join( '%d' % ( i + 1 ) for i in channels )
	return s

