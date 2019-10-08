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
Wrap the PortAudio library using high-level functions and classes
to make it easy to use from Python (at a higher level than the
enclosed `_dll_wrapper` submodule, which aims to provide Python
wrappers/replicas of the functions and constants in portaudio.h).
"""
__all__ = [
	'SetDefaultVerbosity',
	'GetHostApiInfo', 'GetDeviceInfo', 'FindDevice', 'FindDevices', 'Tabulate',
	'Stream', 'PORTAUDIO',
]

####### portaudio-specific implementation

import sys
import ctypes
import pstats
import weakref
import cProfile

if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )
def IfStringThenRawString( x ):
	from . import _dll_wrapper
	if isinstance( x, _dll_wrapper.String ): x = x.data
	if isinstance( x, unicode ): x = x.encode( 'utf-8' )
	return x
def IfStringThenNormalString( x ):
	from . import _dll_wrapper
	if isinstance( x, _dll_wrapper.String ): x = x.data
	if str is not bytes and isinstance( x, bytes ): x = x.decode( 'utf-8' )
	return x

class ErrorCheckingDllWrapper( object ):
	def __init__( self, dll, raiseExceptions=False, printWarnings=False ):
		self.__dll = dll
		self.raiseExceptions = raiseExceptions
		self.printWarnings = printWarnings
	def __getattr__( self, name ):
		func = getattr( self.__dll, name )
		def wrapped( *pargs ):
			error = func( *pargs )
			if error == self.__dll.paUnanticipatedHostError:
				info = self.__dll.Pa_GetLastHostErrorInfo()
				error = info.contents.errorCode
				errorName = 'paUnanticipatedHostError: ' + IfStringThenNormalString( info.contents.errorText )
			elif error:
				lookup = [ x for x in dir( self.__dll ) if getattr( self.__dll, x ) == error ]
				errorName = lookup[ 0 ] if lookup else '???'
			if error:
				msg = '%s() call failed with error code %r (%s)' % ( name, error, errorName )
				if self.raiseExceptions: raise RuntimeError( msg )
				elif self.printWarnings: print( 'WARNING: %s' % msg )
			return error
		wrapped.__name__ = name
		setattr( self, name, wrapped )
		return wrapped

class Library( object ):
	"""
	A representation of the PortAudio library itself.
	This will be automatically initialized and
	terminated as appropriate.
	"""
	DEFAULT_INPUT_API_PREFERENCE_ORDER  = 'DirectSound, MME, WASAPI, *'
	DEFAULT_OUTPUT_API_PREFERENCE_ORDER = 'DirectSound, WASAPI, ASIO, *'
	# ASIO has been demoted in this ordering, because (at least with
	# 'Realtek ASIO' under Windows 10 on Dell Optiplex 7760 AIO) it would
	# take over the entire driver and sounds from other applications
	# could not be heard (NB: in some situations that may be desirable...)
	
	def __init__( self, verbose=False ):
		self.verbose = verbose
		self.__initialized = False
		self.__dll = None
		self.__dll_errorcheck = None
		
	def __Open( self ):
		if not self.__dll: from . import _dll_wrapper; self.__dll = _dll_wrapper
		if not self.__dll_errorcheck: self.__dll_errorcheck = ErrorCheckingDllWrapper( self.__dll, printWarnings=self.verbose )
		if not self.__initialized:
			self.__initialized = ( self.__dll_errorcheck.Pa_Initialize() == 0 )
			if self.verbose: print( repr( self ) + ( ' has been initialized' if self.__initialized else ' failed to initialize' ) )
			self.__Pa_Terminate = self.__dll_errorcheck.Pa_Terminate # this may seem stupid...
		return self
	
	def __Close( self ):
		if self.__initialized:
			if self.verbose > 1: print( '%r is terminating (stage 0)' % self )
			elif self.verbose: print( '%r is terminating' % self )
			self.__Pa_Terminate() # ...but it works around an exception that would otherwise happen (and be verbosely ignored) during garbage collection in Python 2
			if self.verbose > 1: print( '%r is terminating (stage 1)' % self )
		self.__initialized = False
		
	def __del__( self ):
		self.__Close()
	
	@property
	def initialized( self ):
		return self.__initialized
	@property
	def dll( self ):
		return self.__Open().__dll
	@property
	def dll_errorcheck( self ):
		return self.__Open().__dll_errorcheck
				
PORTAUDIO = Library()

class Bunch( dict ):
	def __getattr__( self, name ):
		b = self
		for name in name.split( '.' ): b = b[ name ] if name in b else getattr( super( b.__class__, b ), name ) if isinstance( b, Bunch ) else getattr( b, name )
		return b
	def __setattr__( self, name, value ): dict.__setattr__( self, name, value ) if name.startswith( '_' ) else self.__setitem__( name, value )
	def __dir__( self ): return self.keys()
	_getAttributeNames = __dir__
	def __repr__( self ): return self._report()
	def _report( self, indent=0, minColonPosition=0 ):
		s = ' ' * indent + '{\n'
		keys = list( self.keys() )
		order = getattr( self, '_fieldOrder', '' )
		known = order.replace( '/', '' ).split()
		order = order.split()
		keys = [ key for key in order if key.strip( '/' ) in keys ] + sorted( [ key for key in keys if key not in known ] )
		maxLen = max( len( repr( key ) ) for key in keys ) if keys else 0
		indentIncrement = 4
		minColonPosition = max( minColonPosition - indentIncrement, maxLen + indent + indentIncrement + 1 )
		#minColonPosition = max( minColonPosition, maxLen + indent + indentIncrement + 1 )
		#minColonPosition = maxLen + indent + indentIncrement + 1
		for key in keys:
			if key.startswith( '//' ): s += '\n'
			key = key.strip( '/' )
			krepr = repr( key )
			spaces = minColonPosition - len( krepr ) - 1
			spacesBefore = indent + indentIncrement
			#spacesBefore = spaces
			spacesAfter = spaces - spacesBefore
			s += ' ' * spacesBefore + krepr + ' ' * spacesAfter + ' : '
			value = self[ key ]
			if hasattr( value, '_report' ): s += '\n' + value._report( indent=indent + indentIncrement, minColonPosition=minColonPosition + indentIncrement ).rstrip()
			else: s += repr( value ).strip()
			s += ',\n'
		s += ' ' * ( indent ) + '}'
		return s		

def struct2dict( s, fieldOrder='' ):
	b = Bunch( { k : IfStringThenNormalString( getattr( s.contents, k ) ) for k in s.contents.__slots__ } )
	b._fieldOrder = fieldOrder
	return b

def GetHostApiInfo():
	"""
	Returns a list of records corresponding to PortAudio's
	`Pa_GetHostApiInfo()` output for every available host
	API.  You can `print()` the result, or otherwise convert
	it to `str()`, to see a pretty tabulated summary.
	"""
	fieldOrder = "index name isDefault type deviceCount defaultInputDevice defaultOutputDevice structVersion"
	hostApis = [ struct2dict( PORTAUDIO.dll.Pa_GetHostApiInfo( i ), fieldOrder ) for i in range( PORTAUDIO.dll.Pa_GetHostApiCount() ) ]
	default = PORTAUDIO.dll.Pa_GetDefaultHostApi()
	for index, hostApi in enumerate( hostApis ):
		hostApi[ 'index' ] = index
		hostApi[ 'isDefault' ] = ( index == default )
	return ListOfHostApiRecords( hostApis )
	
def GetDeviceInfo():
	"""
	Returns a list of records corresponding to PortAudio's
	`Pa_GetDeviceInfo()` output for every available
	combination of host API and device.   You can `print()`
	the result, or otherwise convert it to `str()`, to see
	a pretty tabulated summary.
	"""
	hostApis = GetHostApiInfo()
	fieldOrder = "index name defaultSampleRate //maxInputChannels defaultLowInputLatency defaultHighInputLatency isDefaultInput //maxOutputChannels defaultLowOutputLatency defaultHighOutputLatency isDefaultOutput //structVersion hostApi"
	devices = [ struct2dict( PORTAUDIO.dll.Pa_GetDeviceInfo( i ), fieldOrder ) for i in range( PORTAUDIO.dll.Pa_GetDeviceCount() ) ]
	for index, device in enumerate( devices ):
		device[ 'index' ] = index
		device[ 'hostApi' ] = api = hostApis[ device[ 'hostApi' ] ]
		device[ 'isDefaultInput'  ] = ( index == api[ 'defaultInputDevice'  ] )
		device[ 'isDefaultOutput' ] = ( index == api[ 'defaultOutputDevice' ] )
	return ListOfDeviceRecords( devices )
	
def FindDevices( id=None, mode=None, apiPreferences=None ):
	"""
	Calls `GetDeviceInfo()`, filtering and reordering the
	outputs according to the specified criteria. You can
	`print()` the result, or otherwise convert it to `str()`,
	to see a pretty tabulated summary.
	
	You can use `FindDevice()` (singular) to return just the
	top-ranking result (and to assert that at least one
	result can be found).
	
	Args:
		id (int, dict, str, None):
			- `None`: matches all devices;
			- `str`: matches any device with the specified
			  word or phrase in its `name` field;
			- `int`: matches only the device whose `index`
			  field matches `id`;
			- `dict` (including the objects returned by
			  this function, which are `dict` subclassses):
			  matches only the device whose `index` field
			  matches `id['index']`
			
		mode (str, tuple, None):
			May be either a two-element tuple such as
			`mode=(minInputChannels,minOutputChannels)`,
			or a string containing a number of `'o'`
			and/or `'i'` characters.  In either case,
			devices are only matched if they provide
			at least the specified number of input
			and output channels. For example,
			`FindDevices(mode='oo')` matches all devices
			that provide two or more output channels. 
			
		apiPreferences (str, None):
			If this is left at `None`, it defaults to the
			current value of
			`PORTAUDIO.DEFAULT_INPUT_API_PREFERENCE_ORDER`
			(if the `mode` argument requests any inputs) or
			`PORTAUDIO.DEFAULT_OUTPUT_API_PREFERENCE_ORDER`
			otherwise.  The string `'*'` matches all
			host APIs.  Host APIs may be comma-delimited.
			For example, `apiPreferences='DirectSound,*'`
			means "give first priority to devices hosted 
			by the DirectSound API, and then, failing that,
			match all other APIs".  If `'*'` is not included
			in the specification, this argument may limit
			the number of records returned. In any case it
			will affect the ordering of the returned records.
	"""
	if isinstance( id, ( tuple, list ) ):
		return ListOfDeviceRecords( FindDevice( each_id ) for each_id in id )
	devices = GetDeviceInfo()
	
	if isinstance( id, str ): id = id.lower().strip()
	elif isinstance( id, dict ): id = id[ 'index' ]
	elif isinstance( id, int ) or id is None: pass
	else: raise TypeError( 'invalid `id` argument (use name, index or dict)' )
	
	if not mode: mode = '' #if id else 'o'
	if isinstance( mode, ( tuple, list ) ) and len( mode ) == 2:
		minInputChannels, minOutputChannels = mode
	else:
		minInputChannels  = mode.lower().count( 'i' )
		minOutputChannels = mode.lower().count( 'o' )
	
	reordered = []
	if not apiPreferences:
		apiPreferences = PORTAUDIO.DEFAULT_INPUT_API_PREFERENCE_ORDER if minInputChannels else PORTAUDIO.DEFAULT_OUTPUT_API_PREFERENCE_ORDER			
	if isinstance( apiPreferences, str ): apiPreferences = [ preferred.strip() for preferred in apiPreferences.split( ',' ) ]
	# if there's a '*' in the apiPreferences sequence, insert the default host API just before it to ensure that the default is considered first
	apiPreferences = [ preferred.lower() for item in apiPreferences for preferred in ( [ GetHostApiInfo()[ PORTAUDIO.dll.Pa_GetDefaultHostApi() ][ 'name' ], item ] if item == '*' else [ item ] ) ]
	is_subphrase = lambda phrase, sentence: ( ' ' + phrase + ' ' ) in ( ' ' + sentence + ' ' )
	rank = {}
	for preferenceIndex, preferred in enumerate( apiPreferences ):
		if not preferred: continue
		for device in devices:
			if device in reordered: continue
			if preferred != '*' and not is_subphrase( preferred, device[ 'hostApi' ][ 'name' ].lower() ): continue
			rank[ device[ 'index' ] ] = preferenceIndex
			if isinstance( id, str  ) and not is_subphrase( id, device[ 'name' ].lower() ): continue
			if isinstance( id, int  ) and id != device[ 'index' ]: continue
			if device[ 'maxInputChannels'  ] < minInputChannels:  continue
			if device[ 'maxOutputChannels' ] < minOutputChannels: continue
			reordered.append( device )
	reordered.sort( key=lambda device: (
		rank[ device[ 'index' ] ],
		1 if device[ 'isDefaultInput' ] or device[ 'isDefaultOutput' ] else 2,
	) )
	return ListOfDeviceRecords( reordered )
	
def FindDevice( id=None, mode=None, apiPreferences=None ):
	"""
	Returns the first device matched by `FindDevices()`
	(plural) according to the specified criteria. Raises
	an exception if there are no matches.
	"""
	devices = FindDevices( id=id, mode=mode, apiPreferences=apiPreferences )
	if not devices: raise ValueError( 'could not find a device that matched the criteria' )
	return devices[ 0 ]

class Stream( object ):
	# TODO: make this more efficient if the device index is already known (no fussing with repeated FindDevice() calls)
	def __init__( self, device=None, mode=None, apiPreferences=None, outputCallbacks=None, sampleRate=None, sampleFormat=None, verbose=None ):
		"""
		The `device`, `mode` and `apiPreferences` arguments are the
		same as `id`, `mode` and `apiPreferences` in `FindDevice()`.
		"""
		self._library = PORTAUDIO
		self.__verbose = verbose
		if self.verbose: print( '%r is being initialized' % self )
		self.opened = False
		self.started = False
		possibleSampleFormats = [
			dict( ctypes=ctypes.c_float, portaudio=self._library.dll.paFloat32, numpy='float32', bytes=4 ),
		]
		if not apiPreferences:
			wantInput = ( isinstance( mode, str ) and 'i' in mode ) or ( isinstance( mode, ( tuple, list ) ) and mode and mode[ 0 ] )
			apiPreferences = PORTAUDIO.DEFAULT_INPUT_API_PREFERENCE_ORDER if wantInput else PORTAUDIO.DEFAULT_OUTPUT_API_PREFERENCE_ORDER
			if self.verbose: print( '%r prefers APIs %r' % ( self, apiPreferences ) )
		if device is not None:
			device = FindDevice( id=device, apiPreferences=apiPreferences )
			nInputChannels  = device[ 'maxInputChannels'  ]
			nOutputChannels = device[ 'maxOutputChannels' ]
			if not mode:
				if nOutputChannels: mode = 'o' * nOutputChannels
				else: mode = 'i' * nInputChannels
		if hasattr( mode, 'NumberOfChannels' ):
			mode = 'o' * mode.NumberOfChannels()
		if not mode: mode = 'oo'
		if isinstance( mode, ( tuple, list ) ) and len( mode ) == 2:
			nInputChannels, nOutputChannels = mode
		else:
			nInputChannels  = mode.lower().count( 'i' )
			nOutputChannels = mode.lower().count( 'o' )
		
		dual = FindDevices( id=device, mode=( nInputChannels, nOutputChannels ), apiPreferences=apiPreferences )
		if dual:
			self.inputDevice = self.outputDevice = dual[ 0 ]
		else:
			self.inputDevice  = FindDevice( id=device, mode=( nInputChannels,  0 ), apiPreferences=apiPreferences ) if ( nInputChannels  or not mode ) else None
			self.outputDevice = FindDevice( id=device, mode=( 0, nOutputChannels ), apiPreferences=apiPreferences ) if ( nOutputChannels or not mode ) else None
		if nInputChannels <= 1 and nOutputChannels <= 1:
			if nInputChannels  or not mode: nInputChannels  = self.inputDevice[  'maxInputChannels'  ]
			if nOutputChannels or not mode: nOutputChannels = self.outputDevice[ 'maxOutputChannels' ]
		if not nInputChannels  or not self.inputDevice[  'maxInputChannels'  ]: self.inputDevice  = None
		if not nOutputChannels or not self.outputDevice[ 'maxOutputChannels' ]: self.outputDevice = None
		
		defaultSampleFormat = self._library.dll.paFloat32
		defaultSampleRate = min( [ device[ 'defaultSampleRate' ] for device in [ self.inputDevice, self.outputDevice ] if device is not None ] )
		if not sampleFormat: sampleFormat = defaultSampleFormat
		if not sampleRate: sampleRate = defaultSampleRate
		inParams = outParams = ctypes.POINTER( self._library.dll.struct_PaStreamParameters )()
		sampleFormat = [ d for d in possibleSampleFormats if sampleFormat in d.values() ][ 0 ]
		if nInputChannels:
			inParams  = self._library.dll.PaStreamParameters( channelCount=nInputChannels,  device=self.inputDevice[  'index' ], sampleFormat=sampleFormat[ 'portaudio' ], suggestedLatency=self.inputDevice[  'defaultLowInputLatency'  ], hostApiSpecificStreamInfo=self._library.dll.NULL ) # NB: None used as NULL
		if nOutputChannels:
			outParams = self._library.dll.PaStreamParameters( channelCount=nOutputChannels, device=self.outputDevice[ 'index' ], sampleFormat=sampleFormat[ 'portaudio' ], suggestedLatency=self.outputDevice[ 'defaultLowOutputLatency' ], hostApiSpecificStreamInfo=self._library.dll.NULL )
		
		self.__nInputChannels  = nInputChannels
		self.__nOutputChannels = nOutputChannels
		self.__sampleFormat    = sampleFormat
		self.__sampleRate      = sampleRate
		
		dtype = sampleFormat[ 'numpy' ]
		
		self._streamPtr = ctypes.c_void_p()
		
		paContinue = self._library.dll.paContinue  # paContinue, paComplete and paAbort are the possible return values from a stream callback
		paComplete = self._library.dll.paComplete
		paAbort    = self._library.dll.paAbort
		
		self._inputCallbacks = {}
		self._outputCallbacks = {}
		self._AddOutputCallback( outputCallbacks )
		
		profile = self.profile = {}
		class ProfileCM( object ):
			__enter__ = lambda self:     [ p.enable()  for p in profile.values() ]
			__exit__  = lambda self, *p: [ p.disable() for p in profile.values() ]
		profileCM = ProfileCM()
		
		inputBytesPerFrame  = nInputChannels  * sampleFormat[ 'bytes' ]
		outputBytesPerFrame = nOutputChannels * sampleFormat[ 'bytes' ]
		wrself = weakref.ref( self )
		def CallbackWrapper( inputData, outputData, frameCount, timeInfo, statusFlags, userData ):
			with profileCM:
				self = wrself()
				if not self: return paAbort
				t = timeInfo.contents.outputBufferDacTime   # fields are currentTime, inputBufferAdcTime, outputBufferDacTime
				if not t: t = timeInfo.contents.currentTime         # workaround for bug under ALSA-on-Linux
				if not t: t = timeInfo.contents.inputBufferAdcTime  # workaround for bug under ALSA-on-Linux
				# statusFlags may be a bitwise-OR combination of: paInputUnderflow, paInputOverflow, paOutputUnderflow, paOutputOverflow, paPrimingOutput
				if inputData:
					for inputCallback in list( self._inputCallbacks.values() ):
						result = inputCallback( t, inputData, frameCount, nInputChannels )
						if result is not None: inputData = result # currently, `GenericInterface.GenericRecorder._InputCallback` always returns `None`, but it could be streamlined by adding a cacheing mechanism similar to `GenericInterface.GenericPlayer._OutputCallback`
				if outputData:
					ctypes.memset( outputData, 0, frameCount * outputBytesPerFrame )
					for outputCallback in list( self._outputCallbacks.values() ):
						result = outputCallback( t, outputData, frameCount, nOutputChannels, dtype )
						if result is not None: outputData = result # the callback itself should never return `None`, but `result` can end up being `None` anyway due to `weakmethod` wrapping, below
			
				return paContinue # possible values are paContinue, paComplete, paAbort
		self._wrappedCallback = self._library.dll.PaStreamCallback( CallbackWrapper )
		
		handle = ctypes.cast( ctypes.addressof( self._streamPtr ), ctypes.POINTER( ctypes.c_void_p ) )
		
		error = self._library.dll_errorcheck.Pa_IsFormatSupported( inParams, outParams, self.__sampleRate )
		if error == self._library.dll.paInvalidSampleRate:
			self.__sampleRate = defaultSampleRate
			if self.verbose: print( '%r is changing the sample rate to %r' % ( self, self.__sampleRate ) )
			error = self._library.dll_errorcheck.Pa_IsFormatSupported( inParams, outParams, self.__sampleRate )
			
		if self.verbose:
			if self.inputDevice:  print( '%r will use device %d for input  (%r via %s)' % ( self, self.inputDevice[  'index' ], self.inputDevice[  'name' ], self.inputDevice[  'hostApi' ][ 'name' ] ) )
			if self.outputDevice: print( '%r will use device %d for output (%r via %s)' % ( self, self.outputDevice[ 'index' ], self.outputDevice[ 'name' ], self.outputDevice[ 'hostApi' ][ 'name' ] ) )

		for attempt in range( 2 ): # TODO: this fails on Mac (hostApi = 'Core Audio') with error -9996 (paInvalidDevice) for some reason...
			error = self._library.dll_errorcheck.Pa_OpenStream( handle, inParams, outParams, self.__sampleRate, self._library.dll.paFramesPerBufferUnspecified, self._library.dll.paNoFlag, self._wrappedCallback, self._library.dll.NULL )
			if self.verbose and ( error or attempt ): print( 'error on Pa_OpenStream attempt #%d: %r' % ( attempt + 1, error ) )
			if not error: break
			if error != -997: break
		if error: # TODO: ...so we have to fall back on this, which ideally we would prefer not to use
			error = self._library.dll_errorcheck.Pa_OpenDefaultStream( handle, nInputChannels, nOutputChannels, sampleFormat[ 'portaudio' ], self.__sampleRate, self._library.dll.paFramesPerBufferUnspecified, self._wrappedCallback, self._library.dll.NULL )
			if not error:
				if self.verbose: print( 'Pa_OpenStream failed, but Pa_OpenDefaultStream succeeded.' )
				defaultApi = GetHostApiInfo()[ self._library.dll.Pa_GetDefaultHostApi() ]
				devices = GetDeviceInfo()
				if nInputChannels:  self.inputDevice  = devices[ defaultApi[ 'defaultInputDevice'  ] ]
				if nOutputChannels: self.outputDevice = devices[ defaultApi[ 'defaultOutputDevice' ] ]
				# TODO: check whether these represent a change relative to what was requested, and issue a warning if so
		
		self.opened = not error
		self.started = self.opened and self._library.dll_errorcheck.Pa_StartStream( self._streamPtr ) == 0
		
	def StartProfiling( self, **types ):
		self.profile.clear()
		if not types: types = { 'cProfile' : True }
		for type, value in types.items():
			if not value: continue
			if type in [ 'profile', 'cProfile' ]:
				self.profile[ type ] =cProfile.Profile()
			elif type == 'line_profiler':
				import line_profiler
				if not callable( value ): raise ValueError( 'line_profiler option expects a callable, e.g. line_profiler=playerInstance._OutputCallback' )
				self.profile[ type ] = line_profiler.LineProfiler( value )
			else:
				raise TypeError( 'unknown profiler module %r' % type )
		
	def StopProfiling( self ):
		for key, profiler in self.profile.items():
			if key == 'cProfile': pstats.Stats( profiler ).sort_stats( 'cumtime' ).print_stats( 25 )
			if key == 'line_profiler': profiler.print_stats()
			print( '' )
		self.profile.clear()
	
	@property
	def verbose( self ):
		if self.__verbose is not None: return self.__verbose
		return self._library.verbose if self._library else False
	@verbose.setter
	def verbose( self, value ):
		self.__verbose = value
			
	def _AddOutputCallback( self, *callbacks ):
		AddCallbacks( self._outputCallbacks, *callbacks )
		return self
		
	def _RemoveOutputCallback( self, *keyObjects ):
		return RemoveCallbacks( self._outputCallbacks, *keyObjects )
		
	def _AddInputCallback( self, *callbacks ):
		AddCallbacks( self._inputCallbacks, *callbacks )
		return self
		
	def _RemoveInputCallback( self, *keyObjects ):
		return RemoveCallbacks( self._inputCallbacks, *keyObjects )

	def __del__( self ):
		verbose = self.verbose
		if verbose > 1: print( '%r is being deleted (stage 0)' % self )
		elif verbose: print( '%r is being deleted' % self )
		if self.started: self._library.dll.Pa_StopStream( self._streamPtr )
		self.started = False
		if verbose > 1: print( '%r is being deleted (stage 1)' % self )
		if self.opened: self._library.dll.Pa_CloseStream( self._streamPtr )
		self.opened = False
		if verbose > 1: print( '%r is being deleted (stage 2)' % self )
		self._library = None
	
	@property
	def sampleRate( self ): return self.__sampleRate
	fs = sampleRate
	
	@property
	def sampleFormat( self ): return self.__sampleFormat
	
	@property
	def nInputChannels( self ): return self.__nInputChannels
	
	@property
	def nOutputChannels( self ): return self.__nOutputChannels
	
def AddCallbacks( container, *callbacks ):
	callbacks = [ callback for item in callbacks for callback in ( item if isinstance( item, ( tuple, list ) ) else [ item ] if item else [] ) ]
	for callback in callbacks:
		if hasattr( callback, '__self__' ):
			key = id( callback.__self__ )
			wrself = weakref.ref( callback.__self__ )
			func = callback.__func__
			# NB: do not decorate with functools.wraps( callback ) because that will increment the reference count
			def weakmethod( *pargs, **kwargs ):
				self = wrself()
				if self is not None:
					return func( self, *pargs, **kwargs )
			callback = weakmethod
		else:
			key = id( callback )
		container[ key ] = callback
		
def RemoveCallbacks( container, *keyObjects ):
	keyObjects = [ keyObject for item in keyObjects for keyObject in ( item if isinstance( item, ( tuple, list ) ) else [ item ] if item else [] ) ]
	for keyObject in keyObjects: container.pop( id( keyObject ), None )
	return len( container )

def SetDefaultVerbosity( value ):
	"""
	Useful for debugging when the PortAudio library is
	initialized or terminated, when streams are opened,
	started, stopped or closed, and when other objects
	such as players or recorders are initialized or
	garbage-collected.   Objects may be individually
	marked as `.verbose=True` or `.verbose=False`, but
	by default they inherit their verbosity from the
	setting you specify here.
	"""
	PORTAUDIO.verbose = value

def Tabulate( records, *fields ):
	"""
	Returns a pretty-printed table of the specified `fields`
	(i.e. dictionary entries or attributes) of a list of
	records.  This is called automatically, with certain
	default combinations of field names, when you `print()`
	the results of `GetHostApiInfo()`, `GetDeviceInfo()`
	or `FindDevices()`.
	"""
	fields = [ field for item in fields for field in ( item if isinstance( item, ( tuple, list ) ) else item.split() if isinstance( item, str ) else [] if item is None else [ item ] ) ]
	if not fields:
		if not records: return '(no entries)'
		fields = getattr( records, '_fieldsToTabulate', None )
		if isinstance( fields, str ): fields = fields.split()
		if not fields: raise ValueError( 'no fields specified' )
	sep = '  '
	if not records: return sep.join( fields )
	render = lambda x: '%g' % x if isinstance( x, float ) else str( x )
	def getfield( record, field ):
		try: return record[ field ]
		except: return getattr( record, field )
	table = [ fields ] + [ [ render( getfield( record, field ) ) for field in fields ] for record in records ]
	lengths = [ [ len( cell ) for cell in row ] for row in table ]
	lengths = [ max( column ) for column in zip( *lengths ) ]
	return '\n'.join( sep.join( '%-*s' % pair for pair in zip( lengths, row ) ) for row in table )
	
class ListOfHostApiRecords( list ):
	_fieldsToTabulate = 'index name isDefault defaultInputDevice defaultOutputDevice'.split()
	__str__ = Tabulate
class ListOfDeviceRecords( list ):
	_fieldsToTabulate = 'hostApi.name index name maxInputChannels maxOutputChannels defaultSampleRate'.split()
	__str__ = Tabulate
