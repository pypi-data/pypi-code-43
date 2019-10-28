#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# System
import time

# Reflection / Debugging
import inspect

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def frequency( self, i=None ):
		"""
		Get/Set skeleton frequency.
		"""

		if i:
			self._runtime.frequency	=	i
			pass # END IF

		return self._runtime.frequency

		pass # END METHOD : Frequency

	def freqSleep( self, multiplier=1 ):
		'''
		Frequency that should sleep
		Optional multiplier can be used to wait for a frequency-based task to complete.
		'''
		time.sleep( ( 1 / self.frequency() ) * multiplier )
		pass # END METHOD : Frequency sleep

	def lightSleeper( self, **kwargs ):
		'''
		'''

		curframe = inspect.currentframe()
		calframe = inspect.getouterframes(curframe, 2)

		sleep		=	kwargs[ 'sleep' ]
		callback	=	kwargs[ 'callback' ]
		conditional	=	kwargs.get( 'conditional', True )

		# for i in range( math.ceil( sleep ) ):
		sleep	=	1 if ( sleep < 1 ) else round( sleep )

		for i in range( sleep ):

			if callback() != conditional:
				logger.info( f'{ self.name }.{ calframe[ 0 ][ 3 ] }() being used in { self.name }.{ calframe[ 1 ][ 3 ] }() : callback condition has changed, waking up early.' )
				return False
				pass # END IF

			time.sleep( 1 )
			pass # END FOR

		return True

		pass # END METHOD : Light sleeper

	def currentFrame( self ):
		return self._currFrame
		pass # END METHOD

	def currentTimeFrame( self ):

		t	=	time.time()
		d	=	( t - math.floor( t ) )

		return math.floor( self.frequency() * d )

		pass # END

	pass # END CLASS : EXTEND
