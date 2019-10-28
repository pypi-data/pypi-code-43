#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# System
import sys
import os

# Types
import collections
import types
import uuid

# Pattern matching
import glob

# Polycephaly
from polycephaly.comms.messenger import Messenger as PCM
import polycephaly.processes

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

class Application(
	actions.Extend,
	events.Extend,
	info.Extend,
	setup.Extend,
	timing.Extend,
):

	# Application variables
	name		=	None
	ppill		=	None

	# Process skeleton
	_skel		=	types.SimpleNamespace(

						runtime		=	collections.defaultdict(
											lambda			:	None,	# Default return.
											mode			=	'T',	# [A]syncIO, [T]hread, Forked [P]rocess, or [E]xternal Program.
											autostart		=	True,	# Autostart.
											depends			=	[],		# Dependencies - change order based on needs.
											frequency		=	None,	# Frequency - None is a placeholder. See below in __init__() and polycephaly.core.application.setup._setDefaultFreqs()
											boundShutdown	=	True,	# If true, Process exit when Main does.
											forceStop		=	True,	# If true, Process' death() method can be interrupted.
										),

					)

	# Process information
	_procs		=	types.SimpleNamespace(
						objects		=	{},		# Initialized instances.
						threads		=	{},		# Used for Threads and Forked Processes.
					)

	# System paths
	paths		=	types.SimpleNamespace(
						program		=	os.path.abspath( sys.argv[ 0 ] ),
						base		=	os.path.abspath( os.path.dirname( sys.argv[ 0 ] ) ),
						processes	=	types.SimpleNamespace(
											internal	=	os.path.abspath( os.path.dirname( polycephaly.processes.__file__ ) ),
											external	=	os.path.join( os.path.abspath( os.path.dirname( sys.argv[ 0 ] ) ), 'processes' ),
										),
					)

	# Polycephaly Messaging
	pcm			=	None

	def __init__( self, mainProcess=None, *args, **kwargs ):

		# Update application variables
		self.name			=	kwargs.pop( 'name', 'main' ).lower()
		self.ppill			=	kwargs.pop( 'ppill', str( uuid.uuid4() ) )
		self.threadsTimeout	=	kwargs.pop( 'threadsTimeout', 30 )

		# Remove conflicting keywords that we'll set below.
		[ kwargs.pop( k, None ) for k in [ 'mode', 'autostart', ] ]

		# Polycephaly's shared Messaging platform.
		self.pcm	=	PCM(
							nameMain	=	self.name,								# Used for tracking the main process name.
							queueSize	=	kwargs.pop( 'queueSize', 50 ),			# Number of messages to keep in queue.
							queueType	=	kwargs.pop( 'queueType', 'FIFO' )[ 0 ],	# [F]IFO or [P]riority queue.
						)

		# Create an entry for the Main Process if a reference was passed in.
		if mainProcess and ( self.name not in self.listProcessInstances() ):

			self.addProcess(
				mainProcess,
				name		=	self.name,
				mode		=	'Process',
				autostart	=	False,
				*args,
				**kwargs,
			)

			pass # END IF

		self.build()

		# User didn't set a default frequency, so we'll set one for them.
		if not self.globalFrequency():
			self.globalFrequency( 30 )
			pass # END IF

		pass # END CONSTRUCTOR

	pass # END CLASS : Polycephaly Application
