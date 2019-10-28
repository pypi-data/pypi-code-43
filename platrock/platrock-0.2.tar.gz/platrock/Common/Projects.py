"""
Copyright (c) 2017, 2018, 2019 Irstea
Copyright (c) 2017, 2018, 2019 François Kneib
Copyright (c) 2017, 2018, 2019 Franck Bourrier
Copyright (c) 2017, 2018, 2019 David Toe
Copyright (c) 2017, 2018, 2019 Frédéric Berger
Copyright (c) 2017, 2018, 2019 Stéphane Lambert

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

"""
Definition of the project class
TODO-LIST:
- change the serialization method from pickle to XML or JSON which are more universal and not sensible to the program version upgrades.
"""

from . import Debug
import os,re,glob,fnmatch
import numpy as np
import jsonpickle
import platrock.ThreeD.Simulations
projects_root=""
projects_list=[]

class Project(object):
	def __init__(self):
		self.name=""
		self.date=""
		self.author=""
		self.location=""
		self.context=""
		self.aims=""
		self.path=""
		self.simulations=[]
	
	def write_to_file(self):
		path=self.path+"/PlatRockProject"
		f=open(path,'w',encoding="utf8")
		for k in self.__dict__:
			if k in ["path","simulations_names"]:continue
			f.write('###'+k+'\n')
			f.write(str(self.__dict__[k])+"\n")
		f.close()
	
	def get_loaded_simulation(self,path):
		f=open( path, "r",encoding="utf8")
		r=f.read()
		try:
			s=jsonpickle.decode(r)
			if isinstance(s.terrain,platrock.TwoD.Objects.Terrain) : #we didn't save the param_zones as jsonpickle don't handle weird types, reconstruct here.
				s.terrain.set_params_zones()
		except ValueError:
			Debug.info("Jsonpickle was unable to load the simulation",path)
			Debug.info('The content of the file was:',r)
			s=None
		f.close()
		return s
	
	def update_simulations_list(self):
		simulations=[]
		sim_dirs=next(os.walk(self.path))[1]
		sim_dirs.sort()
		for sim_dir in sim_dirs:
			sim_dir=self.path+"/"+sim_dir
			sim_file=glob.glob(sim_dir+'/setup.json')
			if(len(sim_file)>0):
				s=self.get_loaded_simulation(sim_file[0])
				if(s==None): #the file was not readable for some reason
					for s2 in self.simulations: #search in the existing simulations list in memory
						if(s2.get_full_path()==sim_file[0]):
							s=s2	#if found, keep the one in memory instead of loading
							break
				s.project=self
				simulations.append(s)
		self.simulations=simulations
		
	def reload_simulation(self,simulation):
		s=self.get_loaded_simulation(simulation.get_full_path())
		if(s):
			s.project=self
			for i in range(len(self.simulations)):
				if(self.simulations[i].get_full_path()==s.get_full_path()):
					self.simulations[i]=s
					break
			return s
		else:
			return simulation
	
	def has_simulation_name(self,name):
		if name in [s.name for s in self.simulations]:
			return True
		else:
			return False

def find_by_name(name):
	for p in projects_list:
		if(p.name==name):
			return p

def exists(name):
	if name in [p.name for p in projects_list]:
		return True
	else:
		return False

def update_projects_list():
	global projects_list
	projects_list=[]
	w=os.walk(projects_root)
	for path, dirs, files in w:
		for filename in files:
			if(filename=="PlatRockProject"):
				f=open(path+"/"+filename,'r',encoding="utf8")
				filestring=f.read()
				f.close()
				filestring=re.sub(' *\\n','\\n',filestring)
				p=Project()
				p.path=path
				for argname in ["name","date","author","location","context","aims"]:
					if("###"+argname) in filestring:
						value=filestring.split("###"+argname+"\n")[1].split("\n###")[0]
						value=value.strip()
						p.__dict__[argname]=value
				projects_list.append(p)
