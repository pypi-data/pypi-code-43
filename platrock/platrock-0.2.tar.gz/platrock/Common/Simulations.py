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
This module gather all simulations common things for ThreeD and TwoD models.
"""
import time,traceback,yappi
import numpy as np
import subprocess,os,sys
from . import BounceModels
import platrock.Common.Outputs
import platrock.Common.Debug as Debug
import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
jsonpickle_numpy.register_handlers()
jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=1)

class Simulation(object):
	"""
	"""
	def __init__(self, terrain=None, gravity=9.8, name=None, project=None, enable_forest=False, random_seed=None):
		#FIXME : DOC
		"""
		"""
		t=time.localtime()
		if(name==None):self.name="New simulation ("+str(t.tm_mday).rjust(2,'0')+"-"+str(t.tm_mon).rjust(2,'0')+"-"+str(t.tm_year)+", "+str(t.tm_hour).rjust(2,'0')+":"+str(t.tm_min).rjust(2,'0')+":"+str(t.tm_sec).rjust(2,'0')+")"
		else:self.name=str(name)
		self.terrain=terrain
		self.gravity=gravity
		self.project=project
		self.enable_forest=enable_forest
		self.status="init"
		self.forest_impact_model=None
		self.nb_rocks=0
		self.current_rock=None
		self.benchmark=False
		self.checkpoints=None
		self.output=None
		self.current_rock_number=-1
		
		#OVERRIDE FOREST PARAMETERS :
		self.override_forest_params=False
		self.override_trees_density=0
		self.override_trees_dhp_mean=30
		self.override_trees_dhp_std=10
		#OVERRIDE SEGMENTS PARAMETERS :
		self.override_rebound_params=False
		self.override_bounce_model_number=0
		self.override_roughness=0.1
		self.override_R_n=0.8
		self.override_R_t=0.7
		self.override_phi=30
		self.override_v_half=5
		
		self.number_to_model_correspondance = {}
		
		if(random_seed==None):
			self.random_generator=np.random.RandomState()
		else:
			self.random_generator=np.random.RandomState(random_seed)
	
	def get_full_path(self):
		"""
		Get the full path of the simulation pickle file, composed of: "/the_project_path/simulation_name/setup.pickle"
		
		Returns:
			String: "/the_project_path/simulation_name/setup.pickle"
		"""
		if(self.project):
			return self.project.path+"/"+self.name+"/setup.json"
		else:
			Debug.info("This simulation has no project.")
			return "./"+self.name+"/setup.json"
	
	def get_dir(self):
		"""
		Get the path corresponding to the simulation
		
		Returns:
			String: "/the_project_path/simulation_name/"
		"""
		return self.get_full_path().rsplit("/",1)[0]+"/"
	
	def save_to_file(self):
		"""
		FIXME: DOC. Hint: this method will write any simulation into a json file with jsonpickle. However it is not intented to be used as it, rather call it from the simulation subclass after having removed the unwanted heavy attributes.
		"""
		Debug.Print("Save simulation...")
		prefix=self.get_dir()
		if(not os.path.isdir(prefix)):
			subprocess.call(["mkdir",prefix])
		with open(self.get_full_path(), "w", encoding="utf8") as f:
			project=self.project
			self.project=None
			f.write(jsonpickle.encode(self))
		self.project=project
	
	def before_run_tasks(self):
		Debug.add_logger(self.get_dir()+"log.txt")
		self.current_rock_number=-1
		#initialize the bounce models:
		for number in BounceModels.number_to_model_correspondance.keys():
			self.number_to_model_correspondance[number]=BounceModels.number_to_model_correspondance[number](self) # instanciation of each model
		self.output=platrock.Common.Outputs.Output(self)
		if(self.benchmark):
			yappi.start(builtins=True)
		self.status="running"
	
	def before_rock_launch_tasks(self):
		Debug.info("\n-----------------------------------\n.....::::: NEW ROCK N"+str(self.current_rock_number)+":::::.....\n-----------------------------------\n")
	
	def rock_propagation_tasks(self):
		return
	
	def after_rock_propagation_tasks(self):
		return
	
	def after_successful_run_tasks(self):
		self.status="finished"
	
	def after_failed_run_tasks(self):
		self.status="error"
		Debug.error(traceback.format_exc())
		
	def after_all_tasks(self):
		if(self.benchmark):
			yappi.stop()
			fs=yappi.get_func_stats()
			fs.sort('ttot')
			fs.print_all( columns={0: ('name', 36), 1: ('ncall', 8), 2: ('ttot', 8), 3: ('tsub', 8), 4: ('tavg', 8)} )
		if platrock.web_ui:
			self.save_to_file()
			Debug.Print("Simulation located in "+self.get_full_path()+" finished with status "+self.status+".")
		else:
			Debug.Print("Simulation finished with status "+self.status+".")
	
	def run(self,GUI=False):
		try:
			self.before_run_tasks()
		except:
			self.after_failed_run_tasks()
			self.after_all_tasks()
			return
		if(GUI):	#ThreeD GUI only
			self.GUI_enabled=True
			import platrock.GUI.View3D as View3D
			self.GUI=View3D
			if(self.terrain):self.GUI.draw_rock(self.terrain)
			if(self.enable_forest):self.GUI.draw_trees(self)
			self.GUI.V.ren.ResetCamera()
		try:
			while self.current_rock_number<self.nb_rocks-1 :
				self.current_rock_number+=1
				self.before_rock_launch_tasks()
				while( not self.current_rock.is_stopped):
					self.rock_propagation_tasks()
				self.after_rock_propagation_tasks()
			self.after_successful_run_tasks()
		except KeyboardInterrupt:
			pass
		except Exception:
			self.after_failed_run_tasks()
		finally:
			self.after_all_tasks()
