#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Processes
import threading
import multiprocessing

def isMainThreadInAPythonProcess():
	'''
	Sourced from https://stackoverflow.com/questions/23206787/check-if-current-thread-is-main-thread-in-python

	The older way of accomplishing this was:
	assert threading.current_thread() is threading.main_thread()

	This value returns True if this method is called from the:

	* Application's Main thread.
	* Sub-process running as a Multiprocess instead of a Thread.
	'''

	return True if ( threading.current_thread() is threading.main_thread() ) else False

	pass # END FUNCTION : Is Main Thread?

def isApplicationMainThread( cls=None ):
	'''
	For most of the time, this is a nearly identical result as isMainThreadInAPythonProcess(), but the difference is
	that it can be used when setting up a process (e.g. polycephaly.core.process._setupFilters() which would otherwise register a "false" positive.)
	'''

	if cls:
		return True if ( cls.name == cls.nameMain ) else False
		pass # END IF

	elif (
		isMainThreadInAPythonProcess()
		and
		not isProcessForked()
		and
		not isProcessThreaded()
	):
		return True
		pass # END ELIF

	else:
		return False
		pass # END ELSE

	pass # END FUNCTION : Is this the application thread?

def isProcessForked():
	'''
	https://stackoverflow.com/questions/42283265/how-to-determine-if-running-current-process-is-parent

	The only way that this will return True is if the process' mode is set to Multiprocessing.
	'''

	return False if ( multiprocessing.current_process().name == 'MainProcess' ) else True

	pass # END FUNCTION

def isProcessThreaded():
	'''
	'''

	return True if ( not isMainThreadInAPythonProcess() and not isProcessForked() ) else False

	pass # END FUNCTION
