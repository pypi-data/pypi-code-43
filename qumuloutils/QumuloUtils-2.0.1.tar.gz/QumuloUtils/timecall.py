# Copyright (c) 2015 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
# -----------------------------------------------------------------------------
# TimeCall.py
#
# Class that handles timing of operations. You can frame any operation
# with a "timing" and then report on it anytime during the execution
# of your routine.

'''
== Import

from QumuloUtils import TimeCall

== Invocation

@TimeCall
def SomeRoutineThatYouHaveWritten:

Put the @TimeCall just before the definition of the routine that you wish to time.
That is all that you have to do to capture how long each routine takes to execute.

== Reporting

When you wish to output the counts and timing, you only have to issue a print or some other
statement where you pass in one of the TimeCall routines.

print ("Counts %s" % TimeCall.counts())
print ("Minimums %s" % TimeCall.minimums())
print ("Maximums %s" % TimeCall.maximums())
print ("Averages %s" % TimeCall.averages())

'''

# Import python libraries

import sys
import os
import time
import json
import functools

# TimeCall Class

class TimeCall (object):

   __instances = {}

   def __init__(self, f):
      self.__f = f
      self.__numcalls = 0
      self.__min = 0
      self.__max = 0
      self.__total = 0
      TimeCall.__instances[f] = self

   def __call__(self, *args):
      self.__numcalls += 1
      ts = time.time ()
      result = self.__f (*args)
      te = time.time ()

      # Compute time elapsed and then return

      telapsed = te - ts
      self.__total += telapsed
      self.__min = telapsed if self.__min == 0 else self.__min
      self.__min = telapsed if telapsed < self.__min else self.__min
      self.__max = telapsed if telapsed > self.__max else self.__max

      return result

   def __get__ (self, instance, instancetype):
       return functools.partial (self.__call__, instance)

   def count (self):
      # Return the number of times the function f was called.
      return TimeCall.__instances[self.__f].__numcalls

   def min (self):
       # Return the minimum amount of time a call took
       return "%.5gms" % (TimeCall.__instances[self.__f].__min * 1000)

   def max (self):
       # Return the maximum amount of time a call took
       return "%.5gms" % (TimeCall.__instances[self.__f].__max * 1000)

   def avg (self):
       # Return the average amount of time a call took
       # It is possible that it was never called, so take that into account.

       if TimeCall.__instances[self.__f].__numcalls == 0:
           result = 0
       else:
           result = ((TimeCall.__instances[self.__f].__total / \
                          TimeCall.__instances[self.__f].__numcalls) * 1000)

       return "%.5gms" % result

   # Return a dict of counts for all registered functions."

   @staticmethod
   def counts ():
      return json.dumps (dict ([(f.__name__, \
                                     TimeCall.__instances[f].__numcalls) \
                                   for f in TimeCall.__instances]))

   # Return a dict of minimums for all registered functions."

   @staticmethod
   def minimums ():
       return json.dumps (dict ([(f.__name__, \
                                      TimeCall.__instances[f].min ()) \
                                     for f in TimeCall.__instances]))

   # Return a dict of maximums for all registered functions."

   @staticmethod
   def maximums ():
       return json.dumps (dict ([(f.__name__, \
                                      TimeCall.__instances[f].max ()) \
                                     for f in TimeCall.__instances]))

   # Return a dict of averages for all registered functions."

   @staticmethod
   def averages ():
       return json.dumps (dict ([(f.__name__, \
                                      TimeCall.__instances[f].avg ()) \
                                     for f in TimeCall.__instances]))

