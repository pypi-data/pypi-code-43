#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# System
import os

# Types
import collections

# Pattern matching
import glob

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

class Messenger(
	actions.Extend,
	filters.Extend,
	info.Extend,
	setup.Extend,
):

	# Defaults
	_defSize		=	None	# Default size for message queues
	_defCaller		=	None	# Default caller
	_defRoute		=	None	# Default route

	# Message filters
	_filters		=	collections.defaultdict(
							lambda	:	collections.defaultdict(
											lambda	:	list()
										)
						)

	# Message Queues - e.g. a dictionary with keys, 'main', 'ocm', 'ros', and 'uds'
	_queues			=	{}

	def __init__( self, *args, **kwargs ):

		self.nameMain	=	kwargs.pop( 'nameMain' ).lower()

		# Set defaults
		self._defSize	=	kwargs.get( 'queueSize', 0 )			# 0 for unlimited
		self._defCaller	=	kwargs.get( 'defaultCaller' )			#
		self._defRoute	=	kwargs.get( 'defaultRoute' )			#
		self._defType	=	kwargs.get( 'queueType', 'F' )			# FIFO or Priority

		logger.debug( f"Default message size : { self._defSize }" )
		logger.debug( f"Default message type : { self._defType }" )
		logger.debug( f"Default caller : { self._defCaller }" )
		logger.debug( f"Default route : { self._defRoute }" )

		pass # END METHOD : Constructor

	pass # END CLASS : Polycephaly Messenger
