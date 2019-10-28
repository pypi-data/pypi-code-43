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
This module is used by the ThreeD model. It is a kind of master module that handles simulations.
"""

from . import Objects, Postprocessings, Engines
import platrock.Common.Debug as Debug
import platrock.Common.BounceModels as BounceModels
import platrock.Common.Math as Math
import platrock.Common.Simulations
import platrock.Common.ColorPalettes as cp
import platrock.Common.Outputs as Out
import numpy as np
import quaternion, time, sys
import osgeo.gdal as gdal
if(int(gdal.__version__.split('.')[0])<2):
	Debug.error("python3-gdal version is ",gdal.__version__,"but must be >=2. If you are using ubuntu 16.04 or earlier, you may consider using 'sudo add-apt-repository -y ppa:ubuntugis/ppa'.")
	sys.exit()
import shapely.geometry
import shapely.affinity
from matplotlib import cm
import copy,os,zipfile

#:The current simulation.
current_simulation=None

class Simulation(platrock.Common.Simulations.Simulation):
	"""
	A simulation
	
	.. _input_threeD_params:
	
	The table below displays the attributes that have to be set to the polygons of the input shapefile rocks_start_params_shapefile depending on the sub-model choosen.
	
	+------------------+--------------+---------+--------------+-----------+--------------+-------------+--------------+
	|                  |:attr:`number`|:attr:`z`|:attr:`volume`| :attr:`vz`|:attr:`length`|:attr:`width`|:attr:`height`|
	+------------------+--------------+---------+--------------+-----------+--------------+-------------+--------------+
	|PlatRock (builtin)|            * |       * |     *        |     *     |              |             |              |
	+------------------+--------------+---------+--------------+-----------+--------------+-------------+--------------+
	|Siconos           |            * |   *     |              |     *     |       *      |       *     |       *      |
	+------------------+--------------+---------+--------------+-----------+--------------+-------------+--------------+

	
	Args:
		rocks (list [:class:`ThreeD.Objects.Rock`]): list of all rocks, created in the launching script (see Examples/3D.py)
		current_rock (:class:`ThreeD.Objects.Rock`): the rock currently falling
		terrain (:class:`ThreeD.Objects.Terrain`): the terrain of the simulation
		gravity (float): the --- positive --- gravity acceleration value
		enable_forest (bool): whether to take trees into account or not
		engines (list [:class:`ThreeD.Engines.Engine`]): list of engines to run at each timestep
		dt (int): the time-step
		iter (int): the current iteration (reseted at each new rock)
		running (bool): whether the simulation is running
		enable_GUI (bool): enables the 3D view (experimental)
	"""
	webui_typename="PlatRock 3D"
	valid_input_shapefile_attrs=np.array([	["number",	"Rocks count",					int,	1,		1000],
											["z",		"Drop height (m)",				float,	2,		50	],
											["volume",	"Rocks volume (m<sup>3</sup>)",float,	0.1,	10	],
											["vz",		"Vertical velocity (m/s)",		float,	-10,	0	],
											["length",	"Length (m)",					float,	0.1,	3	],
											["width",	"Width (m)",					float,	0.1,	3	],
											["height",	"Height (m)",					float,	0.1,	3	]])
	def __init__(self, dt=0.02, engines=None,rocks_start_params_shapefile=None,**kwargs):
		super(Simulation, self).__init__(**kwargs)
		global current_simulation
		current_simulation=self
		self.forest_impact_model=None
		self.engines=engines or []
		self.use_siconos=False
		self.dt=dt
		self.iter=0
		self.rocks_start_params=[]
		self.current_start_params_id=0
		self.current_start_params_rock_id=0
		self.GUI_enabled=False
		if(rocks_start_params_shapefile is not None):
			self.set_rocks_start_params_from_shapefile(rocks_start_params_shapefile)
		self.automatic_engines_fill=None
		self.automatic_generate_forest={"enable":False, "density":0, "dhp_mean":30, "dhp_std":10}
		self.limit_fps=30 #used only with 3D view

	def set_rocks_start_params_from_shapefile(self,rocks_start_params_shapefile):
		try:
			self.rocks_start_params=[]
			shp_file=gdal.OpenEx(rocks_start_params_shapefile)
			layer0=shp_file.GetLayer(0)
			feature_nb=layer0.GetFeatureCount()
			for i in range(feature_nb): #loop on rocks start polygons
				self.rocks_start_params.append({}) #self.rocks_start_params is a list of dict
				feat=layer0.GetFeature(i).ExportToJson(as_object=True)
				shapely_poly = shapely.geometry.shape(feat['geometry'])
				shapely_poly = shapely.affinity.translate(shapely_poly,xoff=-self.terrain.Z_raster.xllcorner,yoff=-self.terrain.Z_raster.yllcorner)
				self.rocks_start_params[i]["shapely_polygon"]=shapely_poly
				self.rocks_start_params[i]["color"]=cp.dark2[i]
				rocks_properties = feat['properties']
				for k in list(rocks_properties.keys()):
					if(k not in Simulation.valid_input_shapefile_attrs[:,0]):
						rocks_properties.pop(k)
				self.rocks_start_params[i]["params"]=rocks_properties
		except Exception as e:
			Debug.error("The importation of rocks start params from shapefile failed:",str(e))
	
	def is_siconos_engine_capable(self):
		if not self.rocks_start_params:
			return False
		if not self.terrain:
			return False
		if not self.terrain.soil_params:
			return False
		for params in [rsp["params"] for rsp in self.rocks_start_params]:
			for p in ["height","length","width","z","vz","number"]:
				if not (p in params):
					return False
		for params in [sp["params"] for sp in self.terrain.soil_params]:
			for p in ["e","mu"]:
				if not p in params:
					return False
		return True
			
	def is_sphere_engine_capable(self):
		if not self.rocks_start_params:
			return False
		if not self.terrain:
			return False
		if not self.terrain.soil_params:
			return False
		for params in [rsp["params"] for rsp in self.rocks_start_params]:
			for p in ["volume","z","vz","number"]:
				if not (p in params):
					return False
		for params in [sp["params"] for sp in self.terrain.soil_params]:
			for p in ["roughness","bounce_model_number","R_t"]:
				if not p in params:
					return False
			if params["bounce_model_number"]==0 or params["bounce_model_number"]==1: #Classical and Pfeiffer
				if not "R_n" in params:
					return False
			elif(params["bounce_model_number"]==2):#Bourrier
				if not ("phi" in params and "v_half" in params):
					return False
		return True
	
	def stop_condition(self):
		return (len(self.output.contacts[-1])>1 and self.current_rock.vel.norm()<0.5)
	
	def save_to_file(self):
		"""
		Store (pickle to json) the simulation into a file whose path and name is the return result of :meth:`get_dir`. Note that the file will exclude all data that arises from calculations, this method is meant to save the simulation setup only.
		"""
		#store to local variables all data that shouldn't be saved to the file, then clear the corresponding simulation attributes :
		output=self.output
		self.output=None
		forest_impact_model=self.forest_impact_model
		self.forest_impact_model=None
		current_rock=self.current_rock
		self.current_rock=None
		if(self.terrain):
			terrain=copy.copy(self.terrain)
			self.terrain.faces=[]
			self.terrain.points=[]
			self.terrain.trees=[]
			self.terrain.faces_xyz_bb=None
			self.terrain.Z_raster.data={"Z":self.terrain.Z_raster.data["Z"]}	#only keep the Z data
		super(Simulation,self).save_to_file()	#actual file write is here
		#restore the not-saved data:
		self.output=output
		self.forest_impact_model=forest_impact_model
		if(self.terrain):
			self.terrain=terrain
		self.current_rock=current_rock
		#self.checkpoints=checkpoints
		Debug.Print("... DONE")
	
	def results_to_zipfile(self,filename=None):
		"""
		Create a zip file into the folder returned by :meth:`get_dir` named results.zip containing two text files. "stops.csv" contains info about rocks end position, and "checkpoints.csv" contains the checkpoints infos.
		"""
		if(filename is None):
			filename=self.get_dir()+"results.zip"
		zf = zipfile.ZipFile(filename, "w")
		pp=Postprocessings.Postprocessing(self)
		pp.run()
		outputs=pp.raster.output_to_asc(output_to_string=True)
		for field,output in outputs.items():
			zf.writestr(field+".asc",output)

		if(os.path.isfile(self.get_dir()+"terrain_overview.pdf")):
			zf.write(self.get_dir()+"terrain_overview.pdf",arcname="trajectories_overview.pdf")
		zf.close()
	
	def before_run_tasks(self):
		#set the simulation total number of rocks:
		self.nb_rocks=0
		for rsp in self.rocks_start_params:
			self.nb_rocks+=rsp['params']["number"]
		#call the parent function, which needs nb_rocks to be initialized:
		super(Simulation, self).before_run_tasks()
		
		self.current_start_params_rock_id=0
		self.current_start_params_id=0
		self.current_rock_id=0
		
		if(platrock.web_ui):
			self.terrain.populate_from_Z_raster()
			self.terrain.precompute_datas()
			self.automatic_generate_forest["enable"]=True
		self.terrain.set_faces_params_from_shapefile()
		if(self.automatic_engines_fill=="builtin"):
			self.engines=[	Engines.Verlet_update(use_cython=1,dist_factor=5),
							Engines.Contacts_detector(use_cython=1),
							Engines.Rock_terrain_nscd_basic_contact(),
							Engines.Rock_tree_nscd_basic_contact(),
							Engines.Nscd_integrator(use_cython=1)]
		elif(self.automatic_engines_fill=="siconos"):
			self.engines=[	Engines.Siconos(terrain=self.terrain, dt=0.001)]
		
		if(self.automatic_generate_forest["enable"]):
			self.terrain.generate_random_forest(self.automatic_generate_forest["density"],self.automatic_generate_forest["dhp_mean"],self.automatic_generate_forest["dhp_std"])
			self.enable_forest=len(self.terrain.trees)>0
		if self.enable_forest:
			self.terrain.trees_as_array=np.asarray([np.append(t.pos,t.dhp) for t in self.terrain.trees])
		#if forest, setup the impact model for 3D:
		if(self.enable_forest and self.forest_impact_model==None):
			self.forest_impact_model=BounceModels.Toe_Tree()

		#Define whether we use Siconos or not:
		if("Siconos" == self.engines[0].__class__.__name__):
			self.use_siconos=True
		else:
			self.use_siconos=False
		
		
		
	def before_rock_launch_tasks(self):
		super(Simulation, self).before_rock_launch_tasks()
		self.iter=0
		#select the right parameter set from self.rocks_start_params by using the sub-counter self.current_start_params_rock_id
		self.current_start_params_rock_id+=1
		if(self.current_start_params_rock_id>self.rocks_start_params[self.current_start_params_id]['params']["number"]):
			self.current_start_params_id+=1
			self.current_start_params_rock_id=1
		params=self.rocks_start_params[self.current_start_params_id]['params']
		polygon=self.rocks_start_params[self.current_start_params_id]['shapely_polygon']
		if(isinstance(polygon,shapely.geometry.MultiPolygon)):
			rand=self.random_generator.rand()
			ID=np.where(self.rocks_start_params[self.current_start_params_id]["multipoly_normalized_area_cumsum"]>rand)[0][0]
			polygon=polygon[ID]

		#find a rock start x,y pos in the polygon:
		min_x, min_y, max_x, max_y = polygon.bounds
		for i in range(1001):
			random_point = shapely.geometry.Point([self.random_generator.uniform(min_x, max_x), self.random_generator.uniform(min_y, max_y)])
			if(polygon.contains(random_point)):
				pos=Math.Vector3([random_point.x,random_point.y,0.])
				break
			if(i==1000):Debug.error("Unable to generate a point in the given polygon after 1000 tries.")
		#create the rock at [x,y,0]
		if(self.use_siconos):
			l=params.get("length",1)
			h=params.get("height",1)
			w=params.get("width",1)
			self.current_rock=Objects.Parallelepiped(lengths=[l,h,w],pos=pos)
			self.current_rock.ori=quaternion.from_euler_angles(self.random_generator.rand(3)*2*np.pi)
		else:
			self.current_rock=Objects.Sphere(volume=params["volume"],pos=pos)
		#find the face below the rock then set the rock altitude:
			#1- use the faces bounding boxes in the (x,y) plane to get a rough list
		mins_check_outside = (pos[0:2]<self.terrain.faces_xyz_bb[:,0:3:2]).any(axis=1)
		maxs_check_outside = (pos[0:2]>self.terrain.faces_xyz_bb[:,1:5:2]).any(axis=1)
		inside_mask = np.logical_not(np.logical_or(mins_check_outside, maxs_check_outside))
			#2- loop on the faces list to get the face right below the rock
		for f in self.terrain.faces[inside_mask]:
			#find the corresponding face:
			if(f.is_point_inside_2D(self.current_rock)):	#find the Z position of the rock right above the corresponding face
				self.current_rock.pos[2] = -(f.normal[0]*(random_point.x-f.points[0].pos[0]) + f.normal[1]*(random_point.y-f.points[0].pos[1]))/f.normal[2]+f.points[0].pos[2]+params["z"]+self.current_rock.radius
				break
		if(self.current_rock.pos[2]==0): Debug.error("Couldn't find a suitable height for the current rock.")
		
		self.current_rock.vel=Math.Vector3([self.random_generator.rand()*0.01,self.random_generator.rand()*0.01,params["vz"]])
		if(self.use_siconos):
			self.engines[0].add_rock(self.current_rock)
		self.output.add_rock(self.current_rock)
		self.output.add_contact(self.current_rock,Math.Vector3([0.,1.,0.]),Out.START) #store the rock initial position
		if(self.GUI_enabled):
			self.GUI.draw_rock(self.current_rock)
		# Reset forest:
		if(self.terrain):
			for tree in self.terrain.trees:
				tree.active=True
				tree.color=[0,0.8,0]
	
	def after_rock_propagation_tasks(self):
		type(self).__bases__[0].after_rock_propagation_tasks(self)
		if(self.current_rock.out_of_bounds):
			self.output.add_contact(self.current_rock,Math.Vector3([0.,0.,0.]),Out.OUT)
		else:
			self.output.add_contact(self.current_rock,Math.Vector3([0.,0.,0.]),Out.STOP)
	
	def after_successful_run_tasks(self):
		super(Simulation, self).after_successful_run_tasks()
		if platrock.web_ui:
			import platrock.GUI.Plot3D as Plot3D
			Plot3D.clear()
			Plot3D.draw_terrain(self,with_polygons=True)
			Plot3D.draw_sample_trajectories(self,50)
			Plot3D.fig.savefig(self.get_dir()+'terrain_overview.svg',bbox_inches='tight')
			Plot3D.fig.savefig(self.get_dir()+'terrain_overview.pdf',bbox_inches='tight')
			Plot3D.plt.close()
			self.results_to_zipfile()
	
	def after_all_tasks(self):
		super(Simulation, self).after_all_tasks()

	def rock_propagation_tasks(self):
		#Don't call the parent function here as it would slow down a bit. It would be useless as there is nothing in the parent class (nothing common between TwoD and ThreeD)
		if(not self.status=="running"):
			if(self.GUI_enabled):
				self.GUI.V.window.start_stop_button.setText("RESUME")
			time.sleep(0.1)
			return
		if(self.GUI_enabled):
			for f in self.current_rock.verlet_faces_list:
				f.color=[0.68235294, 0.5372549 , 0.39215686]
		for E in self.engines:
			if( (not E.dead) and self.iter%E.iter_every==0):E.run(self)
		if(self.GUI_enabled):
			for f in self.current_rock.verlet_faces_list:
				f.color=[0.82352941, 0.41176471, 0.11764706]
			if(self.current_rock.terrain_active_contact):
				self.current_rock.terrain_active_contact.face.color=np.random.rand(3)
			if(time.time()-self.GUI.V.time_last_updated>1/self.GUI.V.fps):
				self.GUI.V.time_last_updated=time.time()
				self.GUI.updateTO(self.current_rock)
				self.GUI.updateTerrainColors(self.terrain)
				self.GUI.V.camera.SetFocalPoint(self.current_rock.pos)
				self.GUI.V.window.start_stop_button.setText("PAUSE")
				self.GUI.V.iren.Render()
				time.sleep(0.01)
		if(self.stop_condition()):
			self.current_rock.is_stopped=True
			if(self.use_siconos):
				self.engines[0].remove_rock()
			Debug.info("Rock stopped")
			if(self.GUI_enabled and (not self.use_siconos)):
				self.GUI.V.ren.RemoveActor(self.current_rock.bounding_box.VTK_actor)
				for f in self.current_rock.verlet_faces_list:
					f.color=[0.68235294, 0.5372549 , 0.39215686]
		self.iter+=1
















