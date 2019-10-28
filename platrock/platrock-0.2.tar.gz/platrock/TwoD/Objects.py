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
This module is used by the TwoD model. It handles all the Objects types
"""
#FIXME : rewrite the override mechanism and allow to set default segments parameters from the launch script (as in 3D).

import numpy as np
import platrock.Common.Debug as Debug
import copy,sys
from . import Geoms
import platrock.Common.Math as Math
import platrock.Common.ColorPalettes as cp
import platrock.Common.Outputs as Out

class Rock(object):
	"""A falling rock.
	
	Args:
		pos (:class:`Common.Math.Vector2` [float,float]): position along x,z
		vel (:class:`Common.Math.Vector2` [float,float]): velocity along x,z
		angVel (float): angular velocity
		volume (float): volume
		density (float): density
		I (float): inertia
		radius (float): radius
		mass (float): mass
		is_stopped (boolean): flag triggered when the stopping condition is reached
		current_segment (:class:`Segment`): the current segment that is vertically under the rock
		flying_direction (int): -1 if the rock is moving towards -x, +1 if the rock is moving towards +x
		color (list [float,float,float]): the rock RGB color, each compound being between 0. and 1.
		contacts (list [:class:`Contact` , ...]): list of all contacts that the rock has had with soil or trees.
			A first contact is added at the initial position of the rock, even though it's not a real contact
		out_of_bounds (bool): set to true during the simulation if the rock went out of the terrain
	"""
	def __init__(self,x=0.,height=1.,vel=[1.,0.],angVel=0.,volume=1.,density=2800.,I=None):
		"""
		Constructor
		
		Args:
			x (float): initial position along the x axis. Note that the coordinates system used is the one after the terrain is eventually cleaned, shifted and reversed.
			height (float): initial height, relative to 0
		"""
		
		self.setup_kinematics(x,height,vel,angVel)
		self.volume=volume
		self.density=density
		
		self.radius = (3.*self.volume/np.pi/4.)**(1./3.)
		self.mass = self.volume*self.density
		self.I = I or 2./5.*self.mass*self.radius**2
		self.A = self.mass/(self.mass+self.I/self.radius**2) # see Azzoni et al. 1995
		self.v_square=0 #needed by the rolling aglorithm
	
	def setup_kinematics(self,x=None,height=None,vel=None,angVel=None):
		self.pos=Math.Vector2([x,height])
		self.vel=Math.Vector2(vel)
		self.angVel=Math.Vector1(angVel)
		self.is_stopped=False
		self.current_segment=None
		self.flying_direction=0
		self.color=[np.random.rand(),np.random.rand(),np.random.rand()]
		self.out_of_bounds=False
	
	def update_current_segment(self,input):
		"""
		Update the :attr:`current_segment` of this rock.
		
		Args:
			input (:class:`Segment` | :class:`Terrain`): the new segment or the terrain from which to compute.
		"""
		if(isinstance(input,Segment)):
			self.current_segment=input
			Debug.Print("CURRENT SEGMENT IS SET TO N",self.current_segment.index)
		elif(isinstance(input,Terrain)):
			terrain_points=input.get_points()
			seg=input.segments[np.where(terrain_points[:,0]<=self.pos[0])[0][-1]]
			if abs(self.pos[0]-seg.points[0][0]) < 1e-10: #we are exactly at a point, use velocity to choose between segment before or after.
				self.current_segment = seg if self.flying_direction>0 else input.segments[seg.index-1]
			else :
				self.current_segment=seg
			Debug.Print("CURRENT SEGMENT IS SET TO N",self.current_segment.index)
		else:
			Debug.Print("ERROR, update_current_segment_number called with a wrong input parameter.")
	def update_flying_direction(self):
		"""
		Update the :attr:`flying_direction` from the velocity.
		"""
		self.flying_direction=int(np.sign(self.vel[0]))
		Debug.Print("Rock direction is set to",self.flying_direction)
	
	def move(self,arrival_point,s,segment):
		#update position :
		self.pos=arrival_point
		self.update_current_segment(segment)
		if(self.vel.norm()<0.5 and s.output.contacts[-1].shape[0]>1):
			Debug.Print("ROCK STOPPED")
			self.is_stopped=True
	
	def fly(self,arrival_point,s,segment):
		"""
		Update the position and the velocity of the rock. Also contains the rock stop condition, so sets the :attr:`is_stopped` flag if necessary.
		
		Args:
			arrival_point (:class:`Common.Math.Vector2` [float,float]): point to reach after fly
			gravity (float): gravity to apply during flight #FIXME: DOC
			segment (:class:`Segment`): arrival segment
		"""
		#update velocity regarding the  arrival point :
		self.vel[1]=-s.gravity*(arrival_point[0]-self.pos[0])/self.vel[0] + self.vel[1]
		Debug.Print("Fly to",arrival_point,",new vel is",self.vel)
		self.move(arrival_point,s,segment)
	
	def roll(self,s,azzoni_roll,arrival_point):
		Debug.info("Roll to ",arrival_point)
		if(azzoni_roll.until_stop):
			self.vel*=0
			self.angVel*=0
			self.move(arrival_point,s,self.current_segment)
		else:
			self.vel=azzoni_roll.get_vel(arrival_point)
			self.angVel = Math.Vector1(- self.flying_direction * self.vel.norm()/self.radius)
			if self.flying_direction>0 and arrival_point[0]>=self.current_segment.points[1][0] :
				next_seg_id=self.current_segment.index+1
			elif self.flying_direction<0 and arrival_point[0]<=self.current_segment.points[0][0] :
				next_seg_id=self.current_segment.index-1
			else: next_seg_id=self.current_segment.index
			if next_seg_id<0 or next_seg_id>len(s.terrain.segments)-1 :
				self.out_of_bounds=True
				self.is_stopped=True
				next_segment = self.current_segment
			else:
				next_segment = s.terrain.segments[next_seg_id] 
				
			self.move(arrival_point,s,next_segment)
	
	def bounce(self,s,segment,disable_roughness=False):
		if(s.override_rebound_params):
			bounce_model_number=s.override_bounce_model_number
		else:
			bounce_model_number=segment.bounce_model_number
		bounce_model=s.number_to_model_correspondance[bounce_model_number]
		bounce_model.run(self,segment,disable_roughness)
		return bounce_model.updated_normal

class Contact(object):
	"""
	A contact, used to keep history and store data of a single contact.
	
	Args:
		pos (:class:`Common.Math.Vector2` [float,float]): position along x,z
		vel (:class:`Common.Math.Vector2` [float,float]): velocity along x,z
		normal (:class:`Common.Math.Vector2` [float,float]): normal of the segment facing upwards seen by the rock after the roughness was applied
	"""
	def __init__(self,r,normal,type=None):
		self.rock_pos=r.pos.copy()
		self.rock_output_vel=r.vel.copy()
		self.normal=normal.copy()
		self.rock_output_angVel=r.angVel.copy()
		self.type=type

class Segment(object):
	"""
	A segment of the terrain.
		
	Args:
		points (:class:list [[x0, z0], [x1, z1]]): start and end points	
		bounce_model_number (int): integer representing the bounce model	
		R_t (float): tangential restitution coefficient [0.-1.]
		R_n (float): normal restitution coefficient [0.-1.]
		roughness (float): roughness #FIXME: definition?
		v_half (float): v_half #FIXME: definition?
		phi (float): phi #FIXME: definition?
		trees_density (float): the 3D density of the trees, in trees/hectare #FIXME : check this
		dhp_mean (float): mean dhp, diameter at breast height
		dhp_std (float): dhp standard deviation, diameter at breast height
		slope_gradient (float): the slope gradient, equals to the :math:`a` coefficient of the line
		index (int): index of the segment (they are continuously indexed through the terrain)
	"""
	def __init__(self, start_point, end_point, bounce_model_number=None, R_t=None, R_n=None, roughness=None,mu_r=None, v_half=None, phi=None, trees_density=None, dhp_mean=None, dhp_std=None):
		"""
		Constructor
		
		Args:
			start_point (:class:`Common.Math.Vector2` [x,z]): start point of the segment
			end_point (:class:`Common.Math.Vector2` [x,z]): end point of the segment
		"""
		self.points=np.array([start_point,end_point])
		self.bounce_model_number=bounce_model_number
		self.R_t=R_t
		self.R_n=R_n
		self.roughness=roughness
		self.mu_r=mu_r
		self.v_half=v_half
		self.phi=phi
		self.trees_density=trees_density
		self.dhp_mean=dhp_mean
		self.dhp_std=dhp_std
		self.index=-1
		self.set_geometrical_quantities()
	
	def set_geometrical_quantities(self):
		self.branch=Math.Vector2(self.points[1]-self.points[0])
		if(abs(self.branch[0])<1e-5):
			self.slope_gradient=0.
		else:
			self.slope_gradient=self.branch[1]/self.branch[0]
		self.normal=self.branch.rotated(np.pi/2.).normalized()
		self.slope=np.arctan(self.slope_gradient)
	
	def get_y(self,x):
		"""
		Get the y value from a x value. Warning, x must be between segment start and end.
		
		"""
		return self.points[0][1]+self.slope_gradient*(x-self.points[0][0])
			

class Terrain(object):
	"""
	A 2D terrain made of segments
	
	Args:
		segments (list [:class:`Segment`, ...]): the successive segments forming the terrain
		rebound_models_available (list [int,int,int]): A list of available rebound models regarding the per-segment input parameters given. Modified by check_segments_parameters_consistency() method.
		forest_available (bool): whether the forest is available in the terrain. Modified by check_segments_parameters_consistency() method.
	"""
	valid_input_attrs=np.array([	["R_n",					"R<sub>n</sub>",				float,	0,		0.95	],
									["R_t",					"R<sub>t</sub>",				float,	0,		0.95	],
									["roughness",			"Roughness",					float,	0,		1.		],
									["bounce_model_number",	"Rebound model",				int,	0,		2		],
									["mu_r",				"μ<sub>r</sub>",				float,	0,		45		],
									["phi",					"φ",							float,	0,		40		],
									["v_half",				"V<sub>1/2</sub>",				float,	0,		50		],
									["trees_density",		"Trees density  (trees/ha)",	float,	0,		5000	],
									["dhp_mean",			"Mean trees ⌀ (cm)",			float,	5,		200		],
									["dhp_std",				"σ(trees ⌀)  (cm)",				float,	0.01,	1000	]])
	def __init__(self,file=None,segments_type=Segment):
		self.segments=[]
		self.params_zones=[]
		self.rebound_models_available=[]#A list of available rebound models regarding the per-segment input parameters given. Modified by check_segments_parameters_consistency() method.
		self.forest_available=False
		if(isinstance(file,str)):
			self.import_from_csv(file,segments_type)
			self.check_segments_continuity()
			self.check_segments_parameters_consistency()
			self.index_segments()
			self.set_params_zones()
	
	def import_from_csv(self,file,segments_type):
		"""
		Constructor
		
		Args:
			file (string): path to the terrain file. This file is a basic csv text file, which contains points (X,Z) and per-segment parameters. It is formed as follows:
			
				+-+-+-------------------+---+---+---------+------+---+-------------+--------+-------+
				|X|Z|bounce_model_number|R_t|R_n|roughness|v_half|phi|trees_density|dhp_mean|dhp_std|
				+-+-+-------------------+---+---+---------+------+---+-------------+--------+-------+

				The first line of the file MUST be the columns names, which are CASE-SENSITIVE but the sequence can be swapped. The data must be rectangular, meaning that the table must be fullfilled without "no-data" possibility. You can import a terrain with only X and Z columns, but in this case you will have to complete the segments parameters in your script before launching the simulation.
		
		"""
		### all these code lines are needed to clean the terrain.
		input_array=np.genfromtxt(file,names=True, dtype=float)
		if(input_array['Z'][0]-input_array['Z'][-1]<0): # mirror terrain through X if the terrain is ascendent
			input_array['X']=-input_array['X']
			input_array['X']-=input_array['X'].min()
		if(input_array['X'][-1]-input_array['X'][0]<0):	# reverse the values through X if they are inversed
			input_array=np.flip(input_array,axis=0)
		# add horizontal segments at the right and left
		#input_array=np.append(input_array,[input_array[-1]]) ; input_array[-1]["X"]+=0.1*(input_array[-1]["X"]-input_array[0]["X"])
		#input_array=np.insert(input_array,0,[input_array[0]]) ; input_array[0]["X"]-=0.1*(input_array[-1]["X"]-input_array[0]["X"])
		
		### BEGIN REMOVE CAVITIES
		# 1:sort indices by X position in a new list and delete indices that creates cavities
		cleaned_indices=[]
		sorted_indices=np.argsort(input_array['X'])
		unsorted_indices=list(range(len(sorted_indices)))
		counter=0
		while counter < len(sorted_indices):
			i=sorted_indices[counter]
			if(i==unsorted_indices[0]):		# no cavity
				cleaned_indices.append(i)
				unsorted_indices.pop(0)
			else:							# there is a cavity here. Compute V1 and V2 to know whether its a cavity towards left or right of the terrain
				V1=Math.Vector2([input_array[i]['X'],input_array[i]['Z']])-Math.Vector2([input_array[unsorted_indices[0]]['X'],input_array[unsorted_indices[0]]['Z']])
				V2=Math.Vector2([input_array[cleaned_indices[-1]]['X'],input_array[cleaned_indices[-1]]['Z']])-Math.Vector2([input_array[unsorted_indices[0]]['X'],input_array[unsorted_indices[0]]['Z']])
				if(V1.cross(V2)[0]<0):	# so the cavity is on the LEFT
					unsorted_indices.remove(i)
				else:						# so the cavity is on the RIGHT
					for j in range(counter,i):
						counter+=1
						unsorted_indices.remove(j)
					cleaned_indices.append(i)
					unsorted_indices.remove(i)
			counter+=1
		
		# 2: at each discontinuity (one per cavity), add a point that makes the terrain locally vertical (fill the cavity)
		new_cleaned_indices=cleaned_indices[:]
		for cleaned_indice in range(len(cleaned_indices)-1):
			i=cleaned_indices[cleaned_indice]	#the indice of the point before the discontinuity
			j=cleaned_indices[cleaned_indice+1]	#the indice of the point after the discontinuity
			if(j>i+1):	# so there is a discontinuity
				if(input_array[i]['Z']>input_array[j]['Z']): #LEFT side cavity
					line=Geoms.Line(segments_type([input_array[j-1]['X'],input_array[j-1]['Z']],[input_array[j]['X'],input_array[j]['Z']]))
					x=input_array[i]['X']
					z=line.a*x+line.b
					new_cleaned_indices.insert(cleaned_indice+1+(len(new_cleaned_indices)-len(cleaned_indices)),j-1)
					input_array[j-1]["X"]=x
					input_array[j-1]["Z"]=z
				else:	#RIGHT side cavity
					line=Geoms.Line(segments_type([input_array[i]['X'],input_array[i]['Z']],[input_array[i+1]['X'],input_array[i+1]['Z']]))
					x=input_array[j]['X']
					z=line.a*x+line.b
					new_cleaned_indices.insert(cleaned_indice+1+(len(new_cleaned_indices)-len(cleaned_indices)),i+1)
					input_array[i+1]["X"]=x
					input_array[i+1]["Z"]=z
		
		### BEGIN ADD SLOPE TO VERTICAL SEGMENTS
		for indice in range(len(new_cleaned_indices)):
			i=new_cleaned_indices[indice]
			xa=input_array[i]["X"] ; za=input_array[i]["Z"]
			for j in new_cleaned_indices[indice+1:-1]:
				xb=input_array[j]["X"] ; zb=input_array[j]["Z"]
				if(abs(zb-za)<1e-8):	#HORIZONTAL
					break
				neg_slope=(zb-za)<0.
				theta1=np.arctan(abs((xb-xa)/(zb-za)))
				if(neg_slope and theta1<np.radians(1.)):
					input_array[j]["X"]=input_array[i]["X"]+np.tan(np.radians(1.))*(input_array[i]["Z"]-input_array[j]["Z"])
				elif((not neg_slope) and theta1<np.radians(1.) ):
					input_array[j]["X"]=input_array[i]["X"]-np.tan(np.radians(1.))*(input_array[i]["Z"]-input_array[j]["Z"])
				else:
					break
					
		### FINALLY REPLACE THE INPUT_ARRAY
		input_array=input_array[new_cleaned_indices]
		
		### Create segments with X,Z and columns names
		for i in range(0,len(input_array)-1):
			# in all cases, import the terrain coordinates:
			if( abs(input_array['X'][i] - input_array['X'][i+1])<1e-3 and abs(input_array['Z'][i] - input_array['Z'][i+1])<1e-3 ): # consecutive points at the same place
				continue
			s=segments_type([input_array['X'][i],input_array['Z'][i]],[input_array['X'][i+1],input_array['Z'][i+1]])
			for column_name in input_array.dtype.fields:
				name_id = np.where(self.valid_input_attrs[:,0]==column_name)[0]
				if(len(name_id)):
					s.__dict__[column_name]=self.valid_input_attrs[name_id[0],2](input_array[column_name][i])
			self.segments.append(s)
	
	def get_csv_string(self):
		s='X	Z'
		for p in self.valid_input_attrs[:,0]:
			s+="\t"+p
		s=s+"\n"
		for segt in self.segments:
			s+=str(segt.points[0][0])+"\t"+str(segt.points[0][1])+"\t"
			for p in self.valid_input_attrs[:,0]:
				s+=str(segt.__dict__[p])+"\t"
			s=s[:-1]+"\n"
		segt=self.segments[-1]
		s+=str(self.segments[-1].points[1][0])+"\t"+str(self.segments[-1].points[1][1])
		for p in self.valid_input_attrs[:,0]:
			s+=str(segt.__dict__[p])+"\t"
		s=s[:-1]
		return s
	
	def check_segments_continuity(self):
		"""
		Checks the continuity of the terrain. This method checks that each segment starts at the previous segment end. Is the terrain is not valid, the program exits.
		"""
		valid=True
		for i in range(1,len(self.segments)-1):
			if(abs(self.segments[i].points[1,0]-self.segments[i+1].points[0,0])>1e-10):valid=False
			if(abs(self.segments[i].points[1,1]-self.segments[i+1].points[0,1])>1e-10):valid=False
		if(not valid):
			Debug.Print("ERROR, the terrain is not valid")
			sys.exit(1)
	
	def check_segments_parameters_consistency(self):
		"""
			Analyze the segments parameters and checks their consistency/availability. :attr:`forest_available` and :attr:`rebound_models_available` are here.
		"""
		s=self.segments[0] #all the segments has the same data, use the first one to list them below
		HAS_bounce_model_number=s.bounce_model_number is not None
		HAS_roughness=s.roughness is not None
		HAS_R_t=s.R_t is not None
		HAS_trees_density=s.trees_density is not None
		HAS_dhp=(s.dhp_mean is not None) and (s.dhp_std is not None)
		HAS_R_n=s.R_n is not None
		HAS_v_half=s.v_half is not None
		HAS_phi=s.phi is not None
		if(HAS_dhp and HAS_trees_density):
			self.forest_available=True
		if(HAS_bounce_model_number):
			if(HAS_roughness and HAS_R_t and HAS_R_n):
				self.rebound_models_available+=[0,1]
			if(HAS_v_half and HAS_phi):
				self.rebound_models_available+=[2]
				
			bounce_model_numbers=[s.bounce_model_number for s in self.segments]
			USE_classical = 0 in bounce_model_numbers
			USE_pfeiffer = 1 in bounce_model_numbers
			USE_bourrier = 2 in bounce_model_numbers
			if( USE_classical and (0 not in self.rebound_models_available)):
				raise ValueError('At least one segment "rebound_model" parameter has been set to 0(=Classical) but the corresponding parameters were not specified (roughness, R_n, R_t)')
			if( USE_pfeiffer and (1 not in self.rebound_models_available)):
				raise ValueError('At least one segment "rebound_model" parameter has been set to 1(=Pfeiffer) but the corresponding parameters were not specified (roughness, R_n, R_t)')
			if( USE_bourrier and (2 not in self.rebound_models_available)):
				raise ValueError('At least one segment "rebound_model" parameter has been set to 2(=Bourrier) but the corresponding parameters were not specified (roughness, R_t, v_half, phi)')
	
	def compare_params(self,id1,id2):
		s1=self.segments[id1]
		s2=self.segments[id2]
		for param_name in self.valid_input_attrs[:,0]:
			if(s1.__dict__[param_name]!=s2.__dict__[param_name]):
				return False
		return True
		
	def set_params_zones(self):
		if len(self.segments) < 1 :
			self.params_zones=[]
			return
		self.params_zones=[ParamsZone(self,0,0)] #init with first segment = first zone
		for id1 in range(1,len(self.segments)):
			id2 = self.params_zones[-1].end_id
			if(self.compare_params(id1,id2)):	#so we are still on the same param zone, increase its size
				self.params_zones[-1].end_id=id1
			else:	#so we enter a new zone
				self.params_zones.append(ParamsZone(self,id1,id1))
		i=0
		for pz in self.params_zones:
			pz["color"]=cp.qualitative10[i]
			i+=1
	
	def point_is_a_zone_border(self,x):
		id1, id2 = self.get_segments_ids_around_point(x)
		if(id1==-1 or id2==-1): return True
		for pz in self.params_zones:
			if(id1>=pz.start_id and id1<=pz.end_id and id2>=pz.start_id and id2<=pz.end_id):
				return False
		return True

	def get_y(self,x):
		for s in self.segments:
			if(s.points[0,0]<=x and s.points[1][0]>=x):
				return s.get_y(x)
		#x is outside the terrain
		if x>=self.get_points()[-1,0] :
			return self.get_points()[-1,1]
		elif x<=self.get_points()[0,0]:
			return self.get_points()[0,1]
		else:
			Debug.error("Error in terrain.get_y, should never happen.")
	
	def get_segment_zone_ids(self,index):
		for pz in self.params_zones:
			if(index>=pz.start_id and index<=pz.end_id):
				return [pz.start_id,pz.end_id]
				
	def get_points(self):
		"""
		From the list of segments, returns an array of points representing the terrain.
		#FIXME: this method should be used once, but it seems to be used very often during simulation
		
		Returns:
			:class:`numpy.ndarray` [[x0, z0], [x1, z1], ...]
		"""
		output=np.asarray([seg.points[0,:] for seg in self.segments],dtype=float)
		output=np.append(output,[self.segments[-1].points[-1,:]],axis=0)
		return output
	
	def index_segments(self):
		"""
		Index all segments of the terrain, :math:`i=0..N`, applying :class:`Segment` . :attr:`index` :math:`=i`
		As the index are continuously distributed along the terrain, it allows to easily access the next or the previous segment from a given segment.
		"""
		for i in range(0,len(self.segments)):
			self.segments[i].index=i
	
	def get_angle_between(self,id1,id2):
		if(id1>id2):
			id1,id2=id2,id1
		seg1=self.segments[id1]
		seg2=self.segments[id2]
		ret = Math.atan2_signed(seg1.points[0][1]-seg1.points[1][1],seg1.points[0][0]-seg1.points[1][0])- Math.atan2_signed(seg2.points[1][1]-seg2.points[0][1],seg2.points[1][0]-seg2.points[0][0])
		if(ret<0):
			ret+=np.pi*2
		return ret
	
	def get_y_range(self):
		pts=self.get_points()[:,1]
		return [pts.min(), pts.max()]
		
	
	def get_segments_ids_around_point(self,x):
		nearest=np.inf
		for s in self.segments:
			if abs(s.points[0][0]-x)<nearest:
				best_segts = [s.index-1, s.index]
				nearest=abs(s.points[0][0]-x)
		if abs(self.segments[-1].points[1][0]-x)<nearest:
			best_segts = [ len(self.segments)-1, -1]
		return best_segts

	def remove_point(self,x):
		id1, id2 = self.get_segments_ids_around_point(x)
		if(id2==-1): #remove the last point, so remove segment n°id1
			self.remove_segment(id1)
			return
		if id2==len(self.segments)-1 : #remove the penultimate point, so remove the last segment but connect end of id1 to end of id2 before.
			self.segments[id1].points[1][:]=self.segments[id2].points[1][:]
		#general case: remove the segment after the point at x
		self.remove_segment(id2)
	
	def add_point_after(self,x):
		id1, id2 = self.get_segments_ids_around_point(x)
		if(id2!=-1): #if there is a segment after the point
			self.split_segment(id2)
	
	def move_point(self,x,newx,newy):
		id1, id2 = self.get_segments_ids_around_point(x)
		if(id1==-1):
			self.move_segment_point(0,"start",newx,newy)
		elif(id2==-1):
			self.move_segment_point(len(self.segments)-1,"end",newx,newy)
		else:
			self.move_segment_point(id1,"end",newx,newy)
	
	def new_zone_at(self,x):
		id1, id2 = self.get_segments_ids_around_point(x)
		if not self.point_is_a_zone_border(x) :
			zone_start, zone_end = self.get_segment_zone_ids(id2)
			for index in range(id2,zone_end+1):
				for p in self.valid_input_attrs:
					self.segments[index].__dict__[p[0]]=p[3]
		self.set_params_zones()

	def remove_segment(self,id):
		if(id!=0 and id!=len(self.segments)-1): #if the segment is not at an extremity, update the end point of the previous segment.
			self.segments[id-1].points[1][:]=self.segments[id].points[1][:]
			self.segments[id-1].set_geometrical_quantities()
		self.segments.pop(id)
		self.index_segments()
		self.set_params_zones()
		self.check_segments_continuity()
		self.check_segments_parameters_consistency()
	
	def split_segment(self,id):
		middle_point = (self.segments[id].points[0] + self.segments[id].points[1])/2
		new_segt=copy.deepcopy(self.segments[id])
		self.segments[id].points[1]=middle_point[:]
		self.segments[id].set_geometrical_quantities()
		new_segt.points[0]=middle_point[:]
		new_segt.set_geometrical_quantities()
		self.segments.insert(id+1,new_segt)
		self.index_segments()
		self.set_params_zones()
		self.check_segments_continuity()
		self.check_segments_parameters_consistency()
	
	def move_segment_point(self,index,which_end,x,y):
		eps=1e-4
		if(which_end=="start"):
			x=min(x,self.segments[index].points[1][0]-eps)
			if(index!=0):
				x=max(x,self.segments[index-1].points[0][0]+eps)
			self.segments[index].points[0][0]=x
			self.segments[index].points[0][1]=y
			self.segments[index].set_geometrical_quantities()
			if(index!=0):
				self.segments[index-1].points[1][0]=x
				self.segments[index-1].points[1][1]=y
				self.segments[index-1].set_geometrical_quantities()
		elif(which_end=="end"):
			x=max(x,self.segments[index].points[0][0]+eps)
			if(index!=len(self.segments)-1):
				x=min(x,self.segments[index+1].points[1][0]-eps)
			self.segments[index].points[1][0]=x
			self.segments[index].points[1][1]=y
			self.segments[index].set_geometrical_quantities()
			if(index!=len(self.segments)-1):
				self.segments[index+1].points[0][0]=x
				self.segments[index+1].points[0][1]=y
				self.segments[index+1].set_geometrical_quantities()
		self.index_segments()
		self.set_params_zones()
		self.check_segments_continuity()
		self.check_segments_parameters_consistency()

class ParamsDict(dict): #subclass dict to be able to i)put attributes (with ".") on a dict ; and ii) propagate params to segments on key assignation (with "[]").
	def __init__(self,zone,terrain):
		super(ParamsDict,self).__init__()
		self.zone=zone
		for attr in terrain.valid_input_attrs[:,0]: #import parameters from start_id
			super(ParamsDict,self).__setitem__(attr, self.zone.segments[self.zone.start_id].__dict__[attr]) #use "super" to avoid the usage of __setitem__ below.

	def __setitem__(self,item,value):
		super(ParamsDict,self).__setitem__(item,value)
		for i in range(self.zone.start_id, self.zone.end_id+1):
			self.zone.segments[i].__dict__[item]=value

class ParamsZone(dict):
	def __init__(self,terrain,start,end):
		self.start_id=start
		self.end_id=end
		self.segments=terrain.segments
		self["color"]=[0,0,0]
		self["params"]=ParamsDict(self,terrain)
		
class Checkpoint(object):
	"""
	A checkpoint along the terrain. Checkpoints data are post-computed from all contacts of all rocks.
	
	Args:
		x (float): the x-position of the checkpoint
		base_height (float): the height of the terrain at the checkpoint x
		rocks (list [:class:`Rock`, ...]): all rocks that passed through the checkpoint
		heights (list [float, ...]): all heights at which the rocks passed through the checkpoint
		vels (list [[vx1,vz1], [vx2,vz2], ...]): all velocities at which the rocks passed through the checkpoint
		angVels (list [float, ...]): all angVels at which the rocks passed through the checkpoint
	"""
	def __init__(self,x):
		self.x=x
		#self.rocks=[]	#this will avoid error when looping on empty checkpoints
	def init_data(self,simulation):
		"""
		Initialize data lists: :attr:`rocks`, :attr:`heights`, :attr:`vels`, :attr:`angVels`
		"""
		self.base_height=simulation.terrain.get_y(self.x)
		#self.rocks=[]
		self.heights=[]
		self.vels=[]
		self.angVels=[]
		self.rocks_ids=[]










