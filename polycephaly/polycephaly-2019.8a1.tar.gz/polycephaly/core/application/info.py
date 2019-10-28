#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def activeSubProcesses( self ):
		'''
		Returns list of Processes (both threaded and forked) that are still running.
		'''
		return [ threadName for threadName, threadAttr in self._procs.threads.items() if threadAttr.is_alive() ]

		pass # END METHOD : Active Sub-processes

	def listProcessInstances( self ):
		return list( self._procs.objects.keys() )
		pass # END METHOD : List process instances

	def listRecipients( self ):
		return self.pcm.listQueues()
		pass # END METHOD : List recipients

	def getProcess( self, name ):
		'''
		Used to retrieve the object instance of a process.
		'''
		return self._procs.objects[ name ] if ( name in self._procs.objects ) else None
		pass # END METHOD : Get process instance

	pass # END CLASS : EXTEND
