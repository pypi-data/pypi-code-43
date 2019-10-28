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
This module is used by the TwoD model. It is a kind of master module that handles simulations.
"""
#TODO:
# - find a workaround for rebounds that are too small


from . import Objects, Geoms
import platrock.Common.BounceModels as BounceModels
import platrock.Common.Debug as Debug
import platrock.Common.Math as Math
import platrock.Common.Outputs as Out
import platrock.Common.Simulations
import numpy as np
import time,os,zipfile
import sys,traceback


class Simulation(platrock.Common.Simulations.Simulation):
	"""
	A simulation
	
	Args:
		terrain (:class:`TwoD.Objects.Terrain`): the terrain of the simulation 
		gravity (float): the --- positive --- gravity acceleration value
		rocks (list [:class:`TwoD.Objects.Rock`]): list of rocks, automatically filled
		checkpoints (list [:class:`TwoD.Objects.Checkpoint`, ...]): all the checkpoints. Checkpoints data are post-computed with :meth:`update_checkpoints` from all contacts of all rocks.
		name (String): the name of the simulation, mandatory for the WebGUI
		rocks_start_params (dict): a dictionnary of the rocks start parameters (see Examples/2D.py for more details)
		status (String): available status: ["init"|"running"|"pause"|"finished"|"error"]
		
		nb_rocks (int): number of rocks to launch
		rocks_volume (float): volume of the rocks
		rocks_density (float): density of the rocks
		rocks_x (float): initial x corrdinate of the rocks
		rocks_z (float): initial height of the rocks
		rocks_vx (float): initial horizontal velocity of the rocks
		rocks_vz (float): initial vertical velocity of the rocks
		rocks_angVel (float): initial angular velocity of the rocks
		
		override_rebound_params (bool): if True, the rebound parameters will be overriden by :attr:`override_roughness`, :attr:`override_R_n`, :attr:`override_R_t`, :attr:`override_phi`, :attr:`override_v_half` and :attr:`override_bounce_model_number`
		override_forest_params (bool): if True, the forest parameters will be overriden by :attr:`override_enable_forest` :attr:`override_trees_density` and :attr:`override_trees_dhp_mean` and :attr:`override_trees_dhp_std`
		override_enable_forest (bool)
		override_bounce_model_number=None
		override_roughness=None
		override_R_n=None
		override_R_t=None
		override_phi=None
		override_v_half=None
		override_trees_density=None
		override_trees_dhp_mean=None
		override_trees_dhp_std=None
	"""
	webui_typename="PlatRock 2D"
	valid_rocks_start_params=np.array([
		["nb_rocks",		"Rocks count",						int,		1,		10000	],
		["rocks_volume",	"Rocks volume (m<sup>3</sup>)",		float,		0.1,	100.	],
		["rocks_vx",		"Horizontal velocity (m/s)",		float,		-10,	10,		],
		["rocks_vz",		"Vertical velocity (m/s)",			float,		-10,	10,		],
		["rocks_angVel",	"Angular velocity (rad/s)",			float,		-6.3,	6.3,	],
		["rocks_x",			"Horizontal position (m)",			float,		0 ,		np.inf,	],
		["rocks_z",			"Falling height (m)",				float,		0.1,	50,		],
		["rocks_density",	"Density (kg/m<sup>3</sup>)",		float,		500,	5000,	]
	])
	
	def __init__(self, checkpoints_x=[], rocks_start_params={}, **kwargs):
		super(Simulation, self).__init__(**kwargs)
		#FIXME : DOC
		"""
		Constructor
		
		Args:
			checkpoints_x (list [x0, x1, ...]): all the checkpoints x postions. Checkpoints data are post-computed with :meth:`update_checkpoints` from all contacts of all rocks.
		"""
		self.checkpoints=[Objects.Checkpoint(x) for x in checkpoints_x]
		
		# SET THE ROCKS DEFAULT PARAMS :
		self.nb_rocks=100
		self.rocks_volume=2.
		self.rocks_density=2650.
		self.rocks_x=1.
		self.rocks_z=5.
		self.rocks_vx=1.
		self.rocks_vz=0.
		self.rocks_angVel=0.
		#self.rocks_start_params=rocks_start_params
		#OVERRIDE THE DEFAULT PARAMS, IF AVAILABLE IN rocks_start_params dict.
		for k in rocks_start_params.keys():
			if(k in self.valid_rocks_start_params[:,0]):
				self.__dict__[k]=rocks_start_params[k]
		self.override_mu_r=30
		
	def save_to_file(self):
		"""
		Store (pickle to json) the simulation into a file whose path and name is the return result of :meth:`get_dir`. Note that the file will exclude all data that arises from calculations, this method is meant to save the simulation setup only.
		"""
		#store to local variables all data that shouldn't be saved to the file, then clear the corresponding simulation attributes :
		output=self.output
		self.output=None
		forest_impact_model=self.forest_impact_model
		self.forest_impact_model=None
		checkpoints=self.checkpoints[:]
		self.checkpoints=[Objects.Checkpoint(c.x) for c in checkpoints] #NOTE: keep the checkpoints position, drop the data
		if(self.terrain): #don't save the params zones as it's not necessary and jsonpickle don't deal with this weird types
			params_zones=self.terrain.params_zones
			self.terrain.params_zones=[]
		if hasattr(self,'hdf5_io'):
				hdf5_io = self.hdf5_io
				self.hdf5_io=None
		platrock.Common.Simulations.Simulation.save_to_file(self)	#actual file write is here. Don't use super as save_to_file is imported in TwoDShape.
		#restore the not-saved data:
		self.output=output
		self.forest_impact_model=forest_impact_model
		self.checkpoints=checkpoints
		if(self.terrain):
			self.terrain.params_zones=params_zones
		if hasattr(self,'hdf5_io'):
			self.hdf5_io=hdf5_io
		Debug.Print("... DONE")
	
	def update_checkpoints(self):
		"""
		Update all the simulation :class:`TwoD.Objects.Checkpoint` according to all contacts of all rocks. This is a post-treatement feature, it is supposed to be triggered after the simulation is terminated.
		"""
		#FIXME: there seems to be a bug when checkpoint position == contact pos, or initial rock pos.
		for chkP in self.checkpoints:
			chkP.init_data(self)
		for i in range(self.nb_rocks):
			contacts_pos=self.output.get_contacts_pos(i)
			for chkP in self.checkpoints:
				indices=np.where(contacts_pos[:,0]>=chkP.x)[0]
				if(len(indices)>0):
					chkP.rocks_ids.append(i)
					id_before=indices[0]-1
					pos=contacts_pos[id_before]
					vel=self.output.get_contacts_vels(i)[id_before]
					angVel=self.output.get_contacts_angVels(i)[id_before]
					if(self.output.get_contacts_types(i)[id_before] == Out.ROLL):
						chkP.heights.append(0.0)
						v0_square=Math.Vector2(vel).norm()**2
						vf_square=Math.Vector2(self.output.get_contacts_vels(i)[id_before+1]).norm()**2
						d_tot=Math.Vector2(contacts_pos[id_before+1]-pos).norm()
						dist_ratio = (chkP.x-contacts_pos[id_before][0])/(contacts_pos[id_before+1][0]-contacts_pos[id_before][0])
						d=d_tot*dist_ratio
						vel=np.sqrt( (vf_square-v0_square)/d_tot * d + v0_square )
						chkP.vels.append(vel*Math.Vector2(contacts_pos[id_before+1]-contacts_pos[id_before]).normalized())
						chkP.angVels.append(vel/((3*self.output.volumes[i]/4/np.pi)**(1/3)))
					elif self.output.get_contacts_types(i)[id_before] == Out.MOTION :
						dist_ratio = (chkP.x-contacts_pos[id_before][0])/(contacts_pos[id_before+1][0]-contacts_pos[id_before][0])
						chkP.heights.append(	contacts_pos[id_before]*(1-dist_ratio) + contacts_pos[id_before+1]*dist_ratio)
						chkP.vels.append(		vel*(1-dist_ratio) + self.output.get_contacts_vels(i)[id_before+1]*dist_ratio)
						chkP.angVels.append(	angVel*(1-dist_ratio) + self.output.get_contacts_angVels(i)[id_before+1]*dist_ratio)
					else:
						parabola=Geoms.Parabola(pos=Math.Vector2(pos),vel=Math.Vector2(vel),g=self.gravity)
						chkP.heights.append(parabola.A*chkP.x**2 + parabola.B*chkP.x + parabola.C - chkP.base_height)
						chkP.vels.append(vel.copy()) #make a copy as we modify the value below, and don't want to modify the s.output.contacts arrays
						chkP.vels[-1][1]=-self.gravity*(chkP.x-pos[0])/vel[0] + vel[1]
						chkP.angVels.append(angVel)
		for chkP in self.checkpoints:
			chkP.crossings_ratio=len(chkP.heights)/self.nb_rocks
		self.output.checkpoints=self.checkpoints
	
	def get_stops_cdf(self,nbins=200):
		xmax=np.zeros(self.output._rocks_counter)
		if (self.output is not None) and self.output._rocks_counter>0 :
			for r_id in range(0,self.output._rocks_counter):
				xmax[r_id] = self.output.get_contacts_pos(r_id)[:,0].max()
		xmax.sort()
		rocks_out_of_bounds_count=np.sum(xmax>self.terrain.get_points()[-1,0]) 
		hist,bin_edges=np.histogram(xmax,np.linspace(self.terrain.segments[0].points[0][0],self.terrain.segments[-1].points[1][0],nbins))
		hist=np.cumsum(hist)
		hist=np.append(hist,hist[-1])
		hist=hist/(hist.max()+rocks_out_of_bounds_count)
		out=np.zeros([2,len(hist)])
		out[0,:]=bin_edges
		out[1,:]=hist
		return out
		
	
	def results_to_zipfile(self,filename=None):
		"""
		Create a zip file into the folder returned by :meth:`get_dir` named results.zip containing two text files. "stops.csv" contains info about rocks end position, and "checkpoints.csv" contains the checkpoints infos.
		"""
		if(filename is None):
			filename=self.get_dir()+"results.zip"
		zf = zipfile.ZipFile(filename, "w")
		output_str="volume;x_stop\n"
		for i in range(self.nb_rocks):
			output_str+=str(self.output.volumes[i])+";"+str(self.output.get_contacts_pos(i)[-1,0])+"\n"
		zf.writestr("stops.csv",output_str)
		
		output_str="x_checkpoint;vx;vz;volume;height;angVel;E\n"
		for chckpt in self.checkpoints:
			for i in range(len(chckpt.heights)):
				rock_id=chckpt.rocks_ids[i]
				output_str+=str(chckpt.x)+";"
				output_str+=str(chckpt.vels[i][0])+";"
				output_str+=str(chckpt.vels[i][1])+";"
				output_str+=str(self.output.volumes[rock_id])+";"
				output_str+=str(chckpt.heights[i])+";"
				output_str+=str(chckpt.angVels[i])+";"
				output_str+=str(0.)+"\n"	#FIXME : determine the energy
		zf.writestr("checkpoints.csv",output_str)
		
		if(os.path.isfile(self.get_dir()+"terrain_overview.pdf")):
			zf.write(self.get_dir()+"terrain_overview.pdf",arcname="trajectories_overview.pdf")
		zf.close()
	
	def before_run_tasks(self):
		super(Simulation, self).before_run_tasks()
		if(self.enable_forest and (not self.terrain.forest_available)):
			self.override_forest_params=True
		if(self.override_forest_params and self.override_trees_density==0):
			self.enable_forest=False
		if(self.enable_forest and self.forest_impact_model==None):
			self.forest_impact_model=BounceModels.Toe_Tree()
	
	def before_rock_launch_tasks(self):
		super(Simulation, self).before_rock_launch_tasks()
		self.current_rock=Objects.Rock(x=self.rocks_x, height=self.rocks_z, vel=Math.Vector2([self.rocks_vx,self.rocks_vz]), angVel=self.rocks_angVel, volume=self.rocks_volume, density=self.rocks_density)
		self.current_rock.update_current_segment(self.terrain)
		self.current_rock.pos[1]+=self.current_rock.current_segment.get_y(self.current_rock.pos[0])
		self.output.add_rock(self.current_rock)
		self.output.add_contact(self.current_rock,Math.Vector2([0.,1.]),Out.START) #store the rock initial position
		Debug.Print("New rock:",self.current_rock.pos,self.current_rock.vel)
	
	def after_rock_propagation_tasks(self):
		type(self).__bases__[0].after_rock_propagation_tasks(self)
		if(self.current_rock.out_of_bounds):
			if(not type(self)==platrock.TwoDShape.Simulations.Simulation):
				#Fly into the void...
				parab=Geoms.Parabola(self.current_rock,g=self.gravity)
				terrain_Dx=self.terrain.get_points()[-1][0] - self.terrain.get_points()[0][0]
				if(self.current_rock.vel[0]>0):
					arrival_x=self.terrain.get_points()[-1][0]+0.05*terrain_Dx
				else:
					arrival_x=self.terrain.get_points()[0][0]-0.05*terrain_Dx
				self.current_rock.fly(Math.Vector2([arrival_x,parab.get_value_at(arrival_x)]),self,self.current_rock.current_segment)
			self.output.add_contact(self.current_rock,Math.Vector2([0.,0.]),Out.OUT)
		else:
			#Mark the stop position
			self.output.add_contact(self.current_rock,Math.Vector2([0.,0.]),Out.STOP)
	
	def after_successful_run_tasks(self):
		type(self).__bases__[0].after_successful_run_tasks(self)
		self.update_checkpoints()
		if platrock.web_ui:
			import platrock.GUI.Plot2D as Plot2D
			with open(self.get_dir()+'terrain_overview_plotly.html','w') as f:
				f.write(Plot2D.get_plotly_raw_html(self,100))
			self.results_to_zipfile()

	def rock_propagation_tasks(self):
		r=self.current_rock
		Debug.Print("\nNew rock propagation loop")
		if(abs(r.vel[0])<1e-5):
			r.vel[0]=np.sign(r.vel[0])*1e-5 #the horizontal velocity can't be zero as it would not create a parabolic trajectory
			if(r.vel[0]==0): #if the vel is exactly 0
				r.vel[0]=1e-5
			self.output.get_contacts_vels(-1)[0,0]=1e-5
			Debug.warning("The rock vel along x is too small (<1e-5), set it to",r.vel[0])
		
		#FOREST=======================================================================================================#
		if(self.enable_forest):
			loop_counter=-1
			rolling = False
			# Loop on portions of the trajectory. The loop ends only when the rock rebounds on the SOIL 
			while(True):
				#INIT:
				loop_counter+=1
				Debug.Print("Start tree loop")
				r.update_flying_direction() #if the previous loop changed the rock propagation direction
				
				#PARABOLA COMPUTATION, STOP CONDITION:
				if not rolling:
					try:
						freefall_bounce_point,rebound_segment,parabola=Geoms.find_next_bounce(self,r) #free fall bounce point, previsional bounce point if we don't consider the forest
					except :
						r.out_of_bounds=True
						r.is_stopped=True #just to stop propagation in main loop (Common.Simulations.run())
						Debug.info("No intersection could be found, check rock.out_of_bounds to find out what happened.")
						return
				
				#DO WE ROLL OR DO WE FLY ?
				if loop_counter==0: #this means that the rock is currently in contact with the SOIL (no tree, OR not in flight, OR first portion of roll in this segment). Roll can only be triggered in this case.
					arrow_x=parabola.get_arrow_x_from_gradient(r.current_segment.slope_gradient) #what will be the x coord of the maximal height reached by the rock on this segment ?
					arrow_height=parabola.get_value_at(arrow_x)-r.current_segment.get_y(arrow_x)
					if arrow_height < r.radius/10:
						Debug.info("Set rolling to True with arrow_x=",arrow_x,"and arrow_height=",arrow_height)
						rolling=True
						self.output.del_contact(-1,-1) #remove the last contact, we will add a rolling contact instead.
				
				#HORIZONTAL DISTANCE TRAVELLED ON THE CURRENT SEGMENT WITH THE ROLL
				if rolling :
					mu_r = self.override_mu_r if self.override_rebound_params else r.current_segment.mu_r
					AR=BounceModels.Azzoni_Roll(r.vel,mu_r,-r.current_segment.slope,self.gravity,start_pos=r.pos,tan_slope=-r.current_segment.slope_gradient,A=r.A)
					self.output.add_contact(r,r.current_segment.normal,Out.ROLL)
					arrival_point=AR.stop_pos
					#Limit the arrival point to the segment extremas
					if arrival_point[0] < r.current_segment.points[0][0]:
						arrival_point=r.current_segment.points[0]
					elif arrival_point[0] > r.current_segment.points[1][0]:
						arrival_point=r.current_segment.points[1]
					else:
						AR.until_stop=True
					arrival_point=Math.Vector2(arrival_point)
					xdist_travel_on_segment=arrival_point[0]-r.pos[0]
				
				#HORIZONTAL DISTANCE TRAVELLED ON THE CURRENT SEGMENT WITH THE PARABOLA
				else:
					if(r.flying_direction>0):	# The end of the trajectory on the current segment is determined either by the next rebound or by the segment ends.
						xdist_travel_on_segment=min(freefall_bounce_point[0],r.current_segment.points[1][0])-r.pos[0]
					else:
						xdist_travel_on_segment=max(freefall_bounce_point[0],r.current_segment.points[0][0])-r.pos[0]

				#FOREST PARAMETERS OVERRIDES:
				if(self.override_forest_params):
					trees_density=self.override_trees_density
					dhp_std=self.override_trees_dhp_std
					dhp_mean=self.override_trees_dhp_mean
				else:
					trees_density=r.current_segment.trees_density
					dhp_std=r.current_segment.dhp_std
					dhp_mean=r.current_segment.dhp_mean
				if(trees_density>1e-5 and dhp_mean>1e-5 and dhp_std>1e-5):
					dhp=Math.get_random_value_from_gamma_distribution(dhp_mean,dhp_std,self.random_generator)
				else:
					trees_density=0
					dhp=0
				
				#WHAT DISTANCE CAN WE STATISTICALLY TRAVEL ALONG X BEFORE REACHING A TREE ?
				if(trees_density<=1e-5 or dhp<0.01): # avoid zero division
					next_tree_impact_xdist=np.inf
				else:
					next_tree_impact_xdist=((100./np.sqrt(trees_density))**2)/(dhp_mean/100. + r.radius*2.)
				Debug.Print("Mean next_tree_impact_xdist :",next_tree_impact_xdist)
				#ADD LINEAR RANDOMNESS BETWEEN 0 (=REACH A TREE NOW) AND 2*next_tree_impact_xdist (TRAVEL 2 TIMES THE STATISTICAL MEAN DISTANCE)
				next_tree_impact_xdist*=2.*self.random_generator.rand()
				
				#WILL THERE BE A TREE-CONTACT BEFORE REACHING THE END OF THIS SEGMENT ? ...
				Debug.Print("Comparing abs(xdist_travel_on_segment)=abs(",xdist_travel_on_segment, ") with next_tree_impact_xdist=",next_tree_impact_xdist)
				if(next_tree_impact_xdist<abs(xdist_travel_on_segment)): # then an impact with a tree will hapen before the end of the travel on this segment.
				#... YES! ROLL OR FLY TO THIS POINT IN ANY CASES
					impact_point=Math.Vector2([r.pos[0]+r.flying_direction*next_tree_impact_xdist,0.0]) # set x first
					if rolling:
						AR.until_stop=False #finally the rock will not roll until stop, as there is a tree before.
						impact_point[1]=r.current_segment.get_y(impact_point[0]) # set z
						r.roll(self,AR,impact_point)
					else:
						impact_point[1]=parabola.get_value_at(impact_point[0]) # set z
						impact_height = impact_point[1]-r.current_segment.get_y(impact_point[0])
						r.fly(impact_point,self,r.current_segment)
						#IF THE ROCK FLIES LOW ENOUGH, MODIFY ITS VEL AND STORE THE CONTACT:
						if(impact_height>2): #no rock-tree impact if impact height is too high
							continue #the while(True) loop
					#After roll or fly, do the rock-tree contact:
					vx,vy,vz=self.forest_impact_model.get_output_vel(r.vel.norm(),r.volume,self.random_generator.rand(),dhp,np.sign(r.vel[1])*abs(np.degrees(np.arctan(r.vel[1]/r.vel[0]))))
					vx=vx*np.sign(r.vel[0])
					if rolling: #if the rock was rolling, also roll after contact
						vel_norm=Math.Vector2([vx,vz]).norm()
						r.vel=Math.normalized2(r.current_segment.branch)*vel_norm*np.sign(vx)
						self.output.add_contact(r,(1*r.flying_direction,0.),Out.ROLL_TREE)
					else: #if the rock was flying, also do a fly after contact
						r.vel[0]=vx
						r.vel[1]=vz
						self.output.add_contact(r,(1*r.flying_direction,0.),Out.TREE)
					Debug.Print("Impact with a tree at:",impact_point,", dhp=",dhp,"cm", "output vel is",r.vel)
				#... NO! THERE WILL BE A FREEFLIGHT OR ROLL
				else:
					#ROLL TO THE NEXT SEGMENT OR UNTIL STOP:
					if rolling:
						# as r.current_segment will be modified in r.roll():
						prev_segment_id=r.current_segment.index
						r.roll(self,AR,arrival_point)# note: AR.until_stop have been set earlier
						#if we rolled until out_of_bounds occured. Note that r.is_stopped==True here.
						if r.out_of_bounds :
							self.output.add_contact(r,Math.Vector2([0.,0.]),Out.SOIL)
						#handle junction with next segment
						if not r.is_stopped :
							angle_segs=self.terrain.get_angle_between(prev_segment_id, r.current_segment.index) #the slope discontinuity angle
							if angle_segs>=np.pi:	# angle>180°, just a soil-like contact so that at next loop we will have a flight
								Debug.info("After roll, free fly.")
								self.output.add_contact(r,Math.Vector2([0.,1.]),Out.SOIL)
							elif angle_segs>np.pi/2:	# 90°>angle>180°, we have a real contact with the segment, compute the bounce here.
								Debug.info("After roll, contact on soil.")
								self.output.add_contact(r,r.bounce(self,r.current_segment,disable_roughness=True),Out.SOIL)
								r.update_flying_direction()
								r.update_current_segment(self.terrain) #the previous r.bounce may have changed the rock vel x-direction. Update the current_segment, knowing that the rock is exactly between two segments.
							else:	# angle<90°, we have a frontal impact, stop the rock.
								Debug.info("After roll, stop rock.")
								r.is_stopped=True
						break #end the infinite loop

					#FLY TO THE NEXT SEGMENT OR THE NEXT SOIL CONTACT
					else:
						#i) the rock will fly until a rebound on the current segment :
						if(rebound_segment.index==r.current_segment.index):
							Debug.Print("No tree impact detected until next bounce on soil")
							r.fly(freefall_bounce_point,self,rebound_segment) #fly to the bounce point
							self.output.add_contact(r,r.bounce(self, rebound_segment),Out.SOIL) #bounce here
							break	#end the infinite loop
						#ii) the rock will fly to the next segment
						else:
							#do a PORTION of flight, until reaching the next segment
							Debug.Print("Fly above the current segment to the begining of the next one")
							if(r.flying_direction>0):
								next_x=r.current_segment.points[1][0]
								next_seg=self.terrain.segments[r.current_segment.index+1]
							else:
								next_x=r.current_segment.points[0][0]
								next_seg=self.terrain.segments[r.current_segment.index-1]
							r.fly(Math.Vector2([next_x,parabola.get_value_at(next_x)]),self,next_seg)
		#/FOREST=======================================================================================================#
		
		#NO FOREST=====================================================================================================#
		else: #no forest :
			r.update_flying_direction() #if the previous loop changed the rock propagation direction
			try:
				bounce_point,rebound_segment,parabola=Geoms.find_next_bounce(self,r) #free fall bounce point, previsional bounce point
			except : #no bounce point have been found...
				r.out_of_bounds=True
				r.is_stopped=True
				Debug.warning("No intersection could be found, maybe the rock went out of terrain bounds ?")
				return
			arrow_x=parabola.get_arrow_x_from_gradient(r.current_segment.slope_gradient) #what will be the x coord of the maximal height reached by the rock on this segment ?
			arrow_height=parabola.get_value_at(arrow_x)-r.current_segment.get_y(arrow_x)
			
			# FLIGHT #
			if arrow_height > r.radius/10 : #the arrow is high-enough to do a FLIGHT:
				Debug.info("FLY")
				r.fly(bounce_point,self,rebound_segment)
				if not r.is_stopped :
					#Bounce on the destination segment :
					self.output.add_contact(r,r.bounce(self, rebound_segment),Out.SOIL)

			# ROLL #
			else:
				Debug.info("ROLL")
				mu_r = self.override_mu_r if self.override_rebound_params else r.current_segment.mu_r
				AR=BounceModels.Azzoni_Roll(r.vel,mu_r,-r.current_segment.slope,self.gravity,start_pos=r.pos,tan_slope=-r.current_segment.slope_gradient,A=r.A)
				#As we are rolling, replace the last contact recorded by a roll-contact
				self.output.del_contact(-1,-1) #remove the last contact, we will add a rolling contact instead.
				self.output.add_contact(r,r.current_segment.normal,Out.ROLL)
				arrival_point=AR.stop_pos
				#Limit the arrival point to the segment extremas
				if arrival_point[0] < r.current_segment.points[0][0]:
					arrival_point=r.current_segment.points[0]
				elif arrival_point[0] > r.current_segment.points[1][0]:
					arrival_point=r.current_segment.points[1]
				else:
					AR.until_stop=True
				arrival_point=Math.Vector2(arrival_point)
				# as r.current_segment will be modified in r.roll()
				prev_segment_id=r.current_segment.index 
				r.roll(self,AR,arrival_point)
				#if we rolled until out_of_bounds occured. Note that r.is_stopped==True here.
				if r.out_of_bounds :
					self.output.add_contact(r,Math.Vector2([0.,0.]),Out.SOIL)
				#handle junction with next segment
				if not r.is_stopped :
					angle_segs=self.terrain.get_angle_between(prev_segment_id, r.current_segment.index) #the slope discontinuity angle
					if angle_segs>=np.pi:	# angle>180°, just a soil-like contact so that at next loop we will have a flight
						Debug.info("After roll, free fly.")
						self.output.add_contact(r,Math.Vector2([0.,1.]),Out.SOIL)
					elif angle_segs>np.pi/2:	# 90°>angle>180°, we have a real contact with the segment, compute the bounce here.
						Debug.info("After roll, contact on soil.")
						self.output.add_contact(r,r.bounce(self,r.current_segment,disable_roughness=True),Out.SOIL)
						r.update_flying_direction()
						r.update_current_segment(self.terrain) #the previous r.bounce may have changed the rock vel x-direction. Update the current_segment, knowing that the rock is exactly between two segments.
					else:	# angle<90°, we have a frontal impact, stop the rock.
						Debug.info("After roll, stop rock.")
						r.is_stopped=True
