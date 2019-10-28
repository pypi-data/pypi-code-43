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
This module is used by the ThreeD model. It handles all the bounce model types
"""
import numpy as np
from . import Debug,Math
import os

#FIXME: DOC in the whole file
class BounceModel(object):
	"""
	
	.. _bounce_params:
	
	Parent class of every bounce models. The table below represents the bounce-models dependency to the parameters. The soil parameters of the terrain elements (segments or faces) MUST be set regarding to this table. Similarly, the input files (csv or shapefile) must be consistent with this table. Note that the parameters are case-sensitive.
	
	+------------------+---------------------------+-----------------+------------+------------+--------------+------------+
	|                  |:attr:`bounce_model_number`|:attr:`roughness`|:attr:`R_n` | :attr:`R_t`|:attr:`v_half`|:attr:`phi` |
	+------------------+---------------------------+-----------------+------------+------------+--------------+------------+
	|Classical         |            *              |        *        |     *      |     *      |              |            |
	+------------------+---------------------------+-----------------+------------+------------+--------------+------------+
	|Pfeiffer          |            *              |        *        |     *      |     *      |              |            |
	+------------------+---------------------------+-----------------+------------+------------+--------------+------------+
	|Bourrier          |            *              |        *        |            |     *      |      *       |     *      |
	+------------------+---------------------------+-----------------+------------+------------+--------------+------------+
	
	"""
	def __init__(self,simulation):
		self.updated_normal=None
		self.simulation=simulation
		if("TwoD" in self.simulation.__module__):
			self.set_updated_normal=self.set_updated_normal2D
			self.check_output_vel=self.check_output_vel_2D
		else:
			self.set_updated_normal=self.set_updated_normal3D
			self.check_output_vel=self.check_output_vel_3D
		
	def set_updated_normal2D(self,rock,normal,roughness):
		roughness_angle=self.simulation.random_generator.rand()*np.arctan(roughness/rock.radius)
		roughness_angle*=np.sign(rock.vel.cross(normal))
		self.updated_normal=normal.rotated(roughness_angle)
		if(self.updated_normal[1]<0.01):	#AVOID THE ROUGHNESS TO CAUSE SLOPE HIGHER THAN 90° OR LESS THAN -90°.
			Debug.info("Roughness caused slope higher than 90 or lower than -90 with normal =",self.updated_normal)
			self.updated_normal[1]=0.01		#Set the z component of the normal=0.01
			self.updated_normal[0]=np.sqrt(1-0.01**2)*np.sign(self.updated_normal[0])	#ajust the x component according to the normalization condition
		Debug.info("updated_normal =",self.updated_normal)
		
	def set_updated_normal3D(self,rock,normal,roughness):
		nd=(rock.vel-rock.vel.dot(normal)*normal).normalized()
		nt=(nd.cross(normal)).normalized()
		roughness_angle=self.simulation.random_generator.rand()*np.arctan(roughness/rock.radius)
		braking_ratio=self.simulation.random_generator.rand()
		deviation_ratio=np.sign(self.simulation.random_generator.rand()-0.5)*(1-braking_ratio)
		self.updated_normal=normal.rotated(roughness_angle*braking_ratio,nt)
		self.updated_normal=self.updated_normal.rotated(roughness_angle*deviation_ratio,nd)
		#FIXME: can the output vel be "inside" the terrain with that ?
	
	def get_velocity_decomposed(self,v):
		vn = v.dot(self.updated_normal)*self.updated_normal
		return [vn,v-vn]
	
	def check_output_vel_2D(self,r,f):
		if(r.vel.cross(f.branch)>-1e-10):
			direction=np.sign(r.vel[0])
			v_norm=r.vel.norm()
			angle = np.pi/180 if direction>0 else np.pi*(1-1/180)
			r.vel=f.branch.rotated(angle).normalized()*v_norm
			self.updated_normal=Math.Vector2([0,0]) #updated_normal is no longer meaningful and difficult to compute for complex rebound models -> disable it.
			Debug.info("Output vel is not valid (inside terrain), modify it to",r.vel)
	
	def check_output_vel_3D(self,r,f):
		pass

class Classical(BounceModel):
	"""
	Classical bounce model type.
	"""
	def __init__(self,*args):
		super(Classical, self).__init__(*args)
	def run(self,r,f,disable_roughness=False):
		"""
		FIXME:  DOC
		"""
		if(self.simulation.override_rebound_params):
			roughness=self.simulation.override_roughness
			R_n=self.simulation.override_R_n
			R_t=self.simulation.override_R_t
		else:
			roughness=f.roughness
			R_n=f.R_n
			R_t=f.R_t
		if(disable_roughness):
			roughness=0
		
		#APPLY REBOUND :
		Debug.Print("CLASSICAL REBOUND on",f)
		self.set_updated_normal(r,f.normal,roughness)
		Vn, Vt = self.get_velocity_decomposed(r.vel)
		Debug.Print("Old vel:",r.vel, "Vn,Vt=",Vn,Vt)
		r.vel=-Vn*R_n+Vt*R_t
		Debug.Print("New vel:",r.vel)
		self.check_output_vel(r,f)

class Pfeiffer(BounceModel):
	"""
	Pfeiffer bounce model type.
	"""
	def __init__(self,*args):
		super(Pfeiffer, self).__init__(*args)
	def run(self,r,f,disable_roughness=False):
		"""
		Runs the bounce model:
		
		#. randomly compute the LSA
		#. compute the rock velocity in the local slope coordinate system
		#. compute the friction function and the scaling factor
		#. modify the velocity
		#. finally rotate back the velocity into the global coordinates and apply it to the rock.
		
		Args:
			r (:class:`TwoD.Objects.Rock`): the rock that bounces
			s (:class:`TwoD.Objects.Segment`): the segment on which the rock bounces
		"""
		
		#SET PARAMS :
		if(self.simulation.override_rebound_params):
			roughness=self.simulation.override_roughness
			R_n=self.simulation.override_R_n
			R_t=self.simulation.override_R_t
		else:
			roughness=f.roughness
			R_n=f.R_n
			R_t=f.R_t
		if(disable_roughness):
			roughness=0
		
		#APPLY REBOUND :
		Debug.Print("PFEIFFER REBOUND on",f)
		self.set_updated_normal(r,f.normal,roughness)
		Vn, Vt = self.get_velocity_decomposed(r.vel)
		
		Ff=R_t+(1.-R_t)/ ((((Vt.norm()-r.angVel.norm()*r.radius)/6.096)**2) +1.2)	#Friction function 6.096=const (vitesse)
		SF=R_t/ ((Vn.norm()/(76.2*R_n))**2+1.)	#Scaling factor
		
		Vn=-Vn.normalized()*Vn.norm()*R_n/(1.+(Vn.norm()/9.144)**2)
		Vt=Vt.normalized()*np.sqrt( ( r.radius**2*(r.I*r.angVel.norm()**2+r.mass*Vt.norm()**2)*Ff*SF ) / ( r.I+r.mass*r.radius**2 ) )
		
		r.vel=Vn+Vt
		r.angVel=self.updated_normal.cross(Vt)   /   r.radius
		Debug.Print("New vel:",r.vel)
		Debug.Print("New angVel:",r.angVel)
		self.check_output_vel(r,f)

class Bourrier(BounceModel):
	"""
	Bourrier bounce model type.
	"""
	def __init__(self,*args):
		super(Bourrier, self).__init__(*args)
	def run(self,r,f,disable_roughness=False):
		"""
		
		"""
		
		#SET PARAMS :
		if(self.simulation.override_rebound_params):
			roughness=self.simulation.override_roughness
			R_t=self.simulation.override_R_t
			v_half=self.simulation.override_v_half
			phi=self.simulation.override_phi
		else:
			roughness=f.roughness
			R_t=f.R_t
			v_half=f.v_half
			phi=f.phi
		if(disable_roughness):
			roughness=0
		
		#APPLY REBOUND :
		Debug.Print("BOURRIER REBOUND on",f)
		self.set_updated_normal(r,f.normal,roughness)
		Vn, Vt = self.get_velocity_decomposed(r.vel)
		
		#FIXME: compute Vn.norm() and Vt.norm() once for perfomance improvement.
		R_n = v_half/(abs(Vn.norm())+v_half)
		psi = np.degrees(np.arctan((2.*(R_t*Vt.norm()+r.radius*R_t*r.angVel.norm()))/(7.*Vn.norm()*(1.+R_n))))
		if (abs(psi)<phi):
			Debug.Print("Adhesion bounce")
			a,b=(5./7.)*R_t*Vt.norm(), (2./7.)*R_t*r.radius*r.angVel.norm() #intermediate computation
			angVel = (b-a)/r.radius
			r.angVel = angVel * Vt.cross(self.updated_normal)/Vt.norm()
			Vt = Vt/Vt.norm()*(a-b)
			Vn = -R_n*Vn
		else:
			Debug.Print("Sliding bounce")
			angVel = -(5./2.)*(1.+R_n)*Vn.norm()/r.radius + R_t*r.angVel.norm()
			r.angVel = angVel * Vt.cross(self.updated_normal)/Vt.norm()
			Vt = Vt/Vt.norm() * ( R_t*Vt.norm() + np.tan(np.radians(phi))*(1.+R_n)*Vn.norm() )
			Vn = -R_n*Vn
		r.vel=Vn+Vt
		Debug.Print("New vel:",r.vel)
		self.check_output_vel(r,f)


number_to_model_correspondance={0:Classical, 1:Pfeiffer, 2:Bourrier}
"""
Dictionnary that allows to link between the rebound model numbers and the corresponding class.

0: :class:`Classical`
1: :class:`Pfeiffer`
2: :class:`Bourrier`

"""


class Toe_Tree():
	def __init__(self,*args):
		from scipy.spatial import cKDTree
		script_dir = os.path.realpath(__file__).rsplit("/",1)[0]
		vels=[5., 10., 15., 20., 25., 30.]
		self.input_sequence=["vel","vol","ecc","dbh","ang","vx","vy","vz"]
		self.weight_sequence=["vel","vol","ang","ecc","dbh","vx","vy","vz"]	#FIXME: check this sequence
		self.toe_array=np.empty([0,8])	#cols 0->4 are parameters given by input_sequence, cols 5->7 are outputs [vx,vy,vz]
		for vi in range(len(vels)):
			input=np.genfromtxt(script_dir+"/Toe_2018/result"+str(vels[vi])+".txt",skip_header=1)
			input=np.delete(input,[5,6],axis=1) #remove the useless columns (input vels)
			self.toe_array=np.append(self.toe_array,input,axis=0)
		#to sort the array lines we need a "structured view" of it, see https://stackoverflow.com/questions/2828059/sorting-arrays-in-numpy-by-column and https://docs.scipy.org/doc/numpy/user/basics.rec.html
		toe_structured_view=self.toe_array.view({"names":self.input_sequence,'formats':['float']*len(self.input_sequence)})
		toe_structured_view.sort(order=self.weight_sequence, axis=0)
		
	def get_output_vel(self,vel=None,vol=None,ecc=None,dbh=None,ang=None):
		#start with the whole array
		sliced_toe_array=self.toe_array.copy()
		dbh*=0.01 #platrock dbh is in cm, while Toe_2018 is in m.
		for key in self.weight_sequence[:-3]:
			col=self.input_sequence.index(key)	#get the current column index
			real_value=locals()[key]			#get the input value
			id_min=np.argmin(abs(sliced_toe_array[:,col]-real_value))
			id_max=len(sliced_toe_array)-np.argmin(abs(sliced_toe_array[::-1,col]-real_value)) -1
			sliced_toe_array=sliced_toe_array[id_min:id_max+1,:] #narrow the slice at each loop
		Debug.info("Toe model with parameters:",sliced_toe_array[0,0:5])
		return sliced_toe_array[0,-3:]


class Azzoni_Roll():
	#1 - init Azzoni roll, this will compute the stop distance and optionally the stop pos ON AN INFINITE SLOPE
	#2 - Use get_vel(arrival_point) from simulation, regarding the rock environment which this class doesn't know about (if segments ends are reached for example)
	def __init__(self,vel,phi,slope,gravity,start_pos=None,tan_slope=None,A=None,mass=None,radius=None,I=None):
		#INPUTS:
			#Mandatory:
		self.vel=vel
		self.phi=phi
		self.slope=slope
		self.gravity=gravity
			#Optional:
		self.start_pos=start_pos
		if tan_slope is None:
			self.tan_slope=np.tan(slope)
		else:
			self.tan_slope=tan_slope
		if A is None: #give either A or {mass,I,radius}
			self.A = mass/(mass+I/radius**2)
		else: self.A=A
		
		#OUTPUTS:
		self.tan_roll_phi=None
		self.delta_tan_angles=None
		self.dist_stop=None
		self.stop_pos=None #only if start_pos is given
		self.direction=None
		self.v_square=None
		
		#Depending on the rock environment, the variables below can be set by the simulation.
		#OTHER:
		self.until_stop=False
		
		self.compute_dist()
	
	def compute_dist(self):
		self.tan_roll_phi=np.tan(np.radians(self.phi))
		self.direction = -1 if self.vel[0]<0 else 1
		self.tan_slope*=self.direction #if going to -x direction, slope sign convention inverted
		self.delta_tan_angles = self.tan_slope - self.tan_roll_phi
		self.v_square=self.vel.norm()**2
		if(self.delta_tan_angles<0):#slow down rolling
			self.dist_stop=-self.v_square/(2*self.A*self.gravity*np.cos(self.slope)*self.delta_tan_angles)
			if(self.start_pos is not None):
				Dx=np.cos(self.slope)*self.dist_stop*self.direction
				Dy=-self.tan_slope*abs(Dx)
				self.stop_pos=self.start_pos+[Dx,Dy]
		else:
			self.dist_stop=np.inf
			self.stop_pos=Math.Vector2([self.direction*np.inf,self.direction*np.inf])
		
	def get_vel(self,arrival_point):
		roll_dist=(arrival_point-self.start_pos).norm()
		scalar_vel = np.sqrt(2*self.A*self.gravity*np.cos(self.slope)*self.delta_tan_angles*roll_dist+self.v_square)
		return (arrival_point-self.start_pos).normalized()*scalar_vel
		


















