#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# System
import sys
import os

# Reflection / Debugging
import functools

# Pattern matching
import glob

# Polycephaly
import polycephaly.functions.threading

# Formatting
from pprint import pformat as pf

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

#------------------------------------------------------------ IMPORT ALL MODULES
currDir	=	os.path.dirname( __file__ )

# https://stackoverflow.com/questions/1057431/how-to-load-all-modules-in-a-folder
modules	=	glob.glob( f"{currDir}/*.py" )
__all__	=	[ os.path.basename(f)[:-3] for f in modules if os.path.isfile( f ) and not f.endswith('__init__.py') ]

# Add sub-modules
__all__	+=	[ d for d in os.listdir( currDir ) if (
				os.path.isdir( os.path.join( currDir, d ) )
				and
				os.path.isfile( os.path.join( currDir, d, '__init__.py' ) )
			) ]

from . import *
#------------------------------------------------------------/IMPORT ALL MODULES

class Process(
	actions.Extend,
	events.Extend,
	info.Extend,
	locking.Extend,
	messaging.Extend,
	setup.Extend,
	signals.Extend,
	threading.Extend,
	timing.Extend,
):

	# Core
	nameMain		=	None	# Primary process for entire application.
	name			=	None	# Name referred to by internal messaging.
	paths			=	None	# Varying paths used by the entire application.
	_runtime		=	None	# Run-time variables, such as frequency.
	_ppill			=	None	# Used for shutting down the process.
	messenger		=	None	# Instance of Polycephaly Messenger.
	_application	=	None	# Application instance, where each process can have direct access to its calls.

	# Local variables
	args			=	None	# Arguments
	kwargs			=	None	# Keyword Arguments

	# Messaging
	_callbacks		=	None	# Methods called from filters.

	# Process state
	_locks			=	None	# Used for atomic locking of actions.
	_active			=	False	# Determines if process is supposed to be active or not.
	_runLevel		=	None	# Current run level (and a poor copy of how Linux does it. 😉)
	_threads		=	None	# Sub-threads that this local process may spin up (e.g. LED patterns).
	_currFrame		=	None	# Used for tracking progress of frames in a second.
	_ranMailman		=	False	# Used for tracking if mailman was run in life() or not, and will run it if forgotten.

	# Signals
	_signalsBak		=	None	# Used for backing up signals if defaults are set in process setup.
	_signalsUsed	=	False	# Used for tracking if any signals are being used or not.
	signalEnd		=	None	# Signal number indicating why process was shutdown (e.g. 2 for SIGINT, 15 for SIGTERM, etc.)

	def _setupVariables( self, args, kwargs ):

		# e.g. main
		self.nameMain		=	kwargs.pop( 'nameMain' )

		# e.g. helloworld
		self.name			=	kwargs.pop( 'name' )

		# e.g. self.paths.base=/opt/helloWorld, self.paths.program=/opt/helloWorld/launch.py
		self.paths			=	kwargs.pop( 'paths' )

		# Prevent incompatibility with names
		if self.name in self.paths.__dict__.keys():
			raise KeyError( f"Process named '{ self.name }' conflicts with a stored path value." )
			pass # END IF

		# Add path to current process *after* inheritance.
		setattr(
			self.paths,
			self.name,
			os.path.abspath( sys.modules[ self.__class__.__module__ ].__file__ )
		)

		# e.g. {'autostart': True, 'daemon': True, 'depends': [], 'frequency': 30, 'forceStop': True, 'mode': 'T'}
		self._runtime		=	kwargs.pop( 'runtime' )

		# e.g. 038ad5eb-5aee-4f70-9c93-1a522991c5a0
		self._ppill			=	kwargs.pop( 'ppill' )

		# e.g. Polycephaly Messenger object.
		self.messenger		=	kwargs.pop( 'messenger' )

		# Store local variables for this process' other methods to use.
		self.args			=	args
		logger.debug( f"{ self.name }.args = { pf( self.args ) }" )
		self.kwargs			=	kwargs
		logger.debug( f"{ self.name }.kwargs = { pf( self.kwargs ) }" )

		# Dictionary of callbacks for message filters used by a specific process.
		self._callbacks		=	{}

		# Dictionary of threads used by a specific process.
		self._threads		=	{}

		# Dictionary of locks used by a specific process.
		self._locks			=	{}

		# Primarily used by the Main process for backing up signals, but can also be used by sub-processes loaded as multiprocessing.
		self._signalsBak	=	{}

		pass # END METHOD : Setup variables

	def _setupEvents( self ):

		self.isActive( True )

		self.addLocks(
			'queue'		# Used by self.getQueue() to lock access to the message queue in case we want threads to also deal with this queue.
		)

		pass # END METHOD : Setup events

	def _setupFilters( self ):

		# Shutdown the entire application.
		if polycephaly.functions.threading.isApplicationMainThread( self ):

			self.addFilter(
				id			=	'e-brake',
				description	=	'Emergency brake : shut the entire application down.',
				recipient	=	fr'(?i)^{ self.name }$',
				subject		=	r'(?i)^EBRAKE$',
				callback	=	self.die,
			)

			# Monkey-patching : add `__subProcInfo` callback for filter to use.
			monkeyMethodSubProcInfo				=	functools.partial( main.Extend._Extend__subProcInfo, self )
			monkeyMethodSubProcInfo.__name__	=	'_Process__subProcInfo'
			monkeyMethodSubProcInfo.__doc__		=	"Queries methods in the application's side and returns them back across the wire to a process that's asking for the information."
			setattr(
				self,
				'_Process__subProcInfo',
				monkeyMethodSubProcInfo
			)
			del monkeyMethodSubProcInfo

			self.addFilter(
				id			=	'proc-info',
				description	=	'Returns results to sub-processes asking the main process for information.',
				recipient	=	fr'(?i)^{ self.name }$',
				subject		=	r'(?i)^PROCINFO$',
				callback	=	self.__subProcInfo,
			)

			pass # END IF

		# Shutdown process.
		self.addFilter(
			id			=	'ppill',
			description	=	'Poison pill.',
			recipient	=	fr'(?i)^{ self.name }$',
			subject		=	fr'(?i)^{ self._ppill }$',
			callback	=	self.die,
		)

		pass # END METHOD : Setup events

	def __init__( self, *args, **kwargs ):
		'''
		'''

		# Setup environments variables.
		self._setupVariables( args, kwargs )

		# Active and initialization of locks.
		self._setupEvents()

		# Adds basic filters, such as shutdown.
		self._setupFilters()

		pass # END METHOD : Constructor

	pass # END CLASS : Polycephaly Process
