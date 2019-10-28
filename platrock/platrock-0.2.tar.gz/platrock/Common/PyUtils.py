"""
Copyright (c) 2019 François Kneib
Copyright (c) 2019 Franck Bourrier
Copyright (c) 2019 David Toe
Copyright (c) 2019 Frédéric Berger
Copyright (c) 2019 Stéphane Lambert

This file is part of PlatRock.

PlatRock is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

PlatRock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar. If not, see <http://www.gnu.org/licenses/>.
"""

class FriendImporter(object):
	friendClass=None
	friendImportNames=[]
	
	#Import normal ATTRIBUTES, i.e. the ones handeled by the objects.
	def __init__(self,*args,**kwargs):
		friendObject=self.friendClass(*args,**kwargs)
		for name in self.friendImportNames:
			if name in friendObject.__dict__.keys(): # so "name" is handeled by the object (like attributes)
				self.__dict__[name]=friendObject.__dict__[name]
	
	#Import METHOD and CLASS ATTRIBUTES that are handeled by the class, not the objects.
	#This is called at PlatRock launch early state, when FriendImporter class is subclassed (not sub-instanciated).
	def __init_subclass__(child_class):
		for name in child_class.friendImportNames:
			if name in child_class.friendClass.__dict__.keys(): #so "name" is handeled by the class (like methods and class attributes)
				exec('child_class.'+name+'=child_class.friendClass.'+name)
