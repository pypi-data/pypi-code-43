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
This module handles all the engines (the core) of the ThreeD code.
TODO : add rock-terrain and rock-tree Cython functions.
"""

from . import ThreeDEnginesToolbox
import platrock.Common.Debug as Debug
import platrock.Common.Math as Math
import platrock.Common.Outputs as Out
import numpy as np
from . import Objects
import quaternion, shapely
import copy
import types

class Engine(object):
	"""
	"Abstract" class for all engines. Each engine has a run() method which is run at each "iter_every" iteration. Engines instances must be stored in :attr:`ThreeD.Simulations.Simulation.Engines`.
	
	Args:
		dead (bool): if True, the engine will not be ran
		iter_every (int): run the engine each iter_every timesteps
	"""
	def __init__(self,iter_every=1,use_cython=False):
		self.dead=False
		self.iter_every=iter_every
		self.use_cython=use_cython


class Verlet_update(Engine):
	"""
	Update the rocks faces (:attr:`ThreeD.Objects.Rock.verlet_faces_list`) and trees (:attr:`ThreeD.Objects.Rock.verlet_trees_list`) neighbours lists.
	
	Args:
		dist_factor (float): the verlet distance factor (dist_factor * rock_radius = verlet distance). Values must be >1, but values >5 are highly recommanded.If dist_factor==1, the verlet algorithm will be unefficient.
		
	"""
	def __init__(self,dist_factor=5,**kwargs):
		super(Verlet_update,self).__init__(**kwargs)
		self.dist_factor=dist_factor
		if(self.use_cython):
			self.run=types.MethodType(ThreeDEnginesToolbox.verlet_run,self)
		else:
			def run(self,s):
				r=s.current_rock
				if(not((r.pos-r.radius*1.1<r.bounding_box.pos-r.bounding_box.half_length).any() or (r.pos+r.radius*1.1>r.bounding_box.pos+r.bounding_box.half_length).any())): #if the rock stays inside the box
					return
				r.bounding_box.half_length=self.dist_factor*r.radius
				r.bounding_box.pos[:]=r.pos[:]
				
				# ROCK - TERRAIN verlet list :
				r.verlet_faces_list=[]	#initialize the list
				mins_check_outside = (r.bounding_box.pos+r.bounding_box.half_length<s.terrain.faces_xyz_bb[:,0::2]).any(axis=1)
				maxs_check_outside = (r.bounding_box.pos-r.bounding_box.half_length>s.terrain.faces_xyz_bb[:,1::2]).any(axis=1)
				inside_mask = np.logical_not(np.logical_or(mins_check_outside, maxs_check_outside))
				r.verlet_faces_list=s.terrain.faces[inside_mask].tolist()
				
				if(s.enable_forest):
					r.verlet_trees_list=[]
					# ROCK - TREES verlet list :
					dists=((s.terrain.trees_as_array[:,0:2] - r.pos[0:2])**2).sum(axis=1)-(s.terrain.trees_as_array[:,2]/2)**2# all (rock centroid) - (trees) squared distances. NOTE: trees_as_array[:,2] are the dhp per trees
					active_indices=np.where(dists<(r.bounding_box.half_length)**2)[0]	#indices of trees composing the verlet list
					r.verlet_trees_list=np.asarray(s.terrain.trees)[active_indices]
					#Debug.info("len(verlet_trees_list) =",len(r.verlet_trees_list))
				
			self.run=types.MethodType(run,self)

class Contacts_detector(Engine):
	"""
	FIXME:DOC
	Append (real, geometrical) contacts into :attr:`ThreeD.Objects.Rock.terrain_active_contacts` dict. Rock-Face goes into :attr:`terrain_active_contacts["terrain"]<ThreeD.Objects.Rock.>`  and Rock-Tree contacts goes into :attr:`terrain_active_contacts["tree"]<ThreeD.Objects.Rock.terrain_active_contacts>` .
	"""
	def __init__(self,**kwargs):
		super(Contacts_detector,self).__init__(**kwargs)
		if(self.use_cython):
			self.run=types.MethodType(ThreeDEnginesToolbox.contacts_detector_run,self)
		else:
			def run(self,s):
				
				# ROCK-TERRAIN :
				r=s.current_rock
				r.terrain_active_contact=None
				face_candidate=None
				face_candidate_dist=np.inf
				#for rp in r.points:
				rp=r.points[0] #for a Object.Sphere there is a unique point
				for tf in r.verlet_faces_list:
					dist=tf.normal.dot(rp.pos-tf.points[0].pos)-r.radius	# first pass : point-plane distance. Negative dist <=> interpenetration.
					if(dist>0.): # no penetration with the plan : no contact possible
						continue
					if(r.vel.dot(tf.normal)>0): #if the rock goes appart from the face. This check was added with the edge and wedge contact detection: edge and wedge detection algorithms could lead to select a face the rock is going appart from.
						continue
					# We now search the nearest distance between the sphere and the triangle. 3 possibilities: surface contact, edge contact, vertex contact
					if(tf.is_point_inside_3D(rp)):
						#we are sure that the contact is on the face surface
						if(dist<face_candidate_dist):
							#this is currently the best candidate
							face_candidate=tf
							face_candidate_dist=dist
						continue 	#as the contact is on the face surface, it is not on an edge or on a vertex. So continue to the next face
					# We now search an edge contact
					found_edge_contact=False
					for i in range(-1,2):
						branch=rp.pos-tf.points[i].pos
						edge=tf.points[i+1].pos-tf.points[i].pos
						proj_coef=branch.dot(edge)/(branch.norm()**2)
						if(proj_coef>1 or proj_coef<0):continue #the projection of the sphere center on the edge is outside the edge
						proj=edge*proj_coef
						dist=(branch-proj).norm()-r.radius
						if(dist<face_candidate_dist and dist<0):
							#this is currently the best candidate
							face_candidate=tf
							face_candidate_dist=dist
							found_edge_contact=True
					if(found_edge_contact):continue	#as the contact is on an edge, it is not on a vertex. So continue to the next face
					# We now search a vertex contact
					for i in range(0,3):
						dist=(tf.points[i].pos-rp.pos).norm()-r.radius
						if(dist<face_candidate_dist and dist<0):
							#this is currently the best candidate
							face_candidate=tf
							face_candidate_dist=dist
				if(face_candidate_dist<0):	#the default value for face_candidate_dist is +infinity, see above.
					r.terrain_active_contact=Objects.Rock_terrain_contact(rp,face_candidate)
					r.terrain_active_contact.dist=face_candidate_dist
				
				# ROCK - TREES :
				if(s.enable_forest):
					r.tree_active_contact=None
					for t in r.verlet_trees_list:
						if(t.active):
							dist=Math.norm2(r.pos[0:2]-t.pos)-r.radius-t.dhp/2./100	#negative dist <=> interpenetration
							if(dist<0.):
								r.tree_active_contact=Objects.Rock_tree_contact(t)
								r.tree_active_contact.dist=dist
			self.run=types.MethodType(run,self)
		
		

class Nscd_integrator(Engine):
	"""
	FIXME : doc
	"""
	def __init__(self,**kwargs):
		super(Nscd_integrator,self).__init__(**kwargs)
		if(self.use_cython):
			self.run=types.MethodType(ThreeDEnginesToolbox.nscd_integrator_run,self)
		else:
			def run(self,s):
				r=s.current_rock
				r.vel[2]-=s.gravity*s.dt
				r.pos+=r.vel*s.dt
				if(s.GUI_enabled):
					#/!\ NOTE this rotational integration scheme is only valid for spheres
					r.ori=quaternion.from_rotation_vector(r.angVel*s.dt)*r.ori
					r.ori=r.ori.normalized()
				r.update_members_pos()
				if(r.pos[2]<s.terrain.min_height):
						Debug.warning("The rock went outside the terrain !")
						r.out_of_bounds=True
						r.is_stopped=True
			self.run=types.MethodType(run,self)

class Rock_terrain_nscd_basic_contact(Engine):
	"""
	FIXME : doc
	"""
	def __init__(self,**kwargs):
		super(Rock_terrain_nscd_basic_contact,self).__init__(**kwargs)
	def run(self,s):
		r=s.current_rock
		if(r.terrain_active_contact):
			f=r.terrain_active_contact.face
			if(s.override_rebound_params):
				bounce_model_number=s.override_bounce_model_number
			else:
				bounce_model_number=f.bounce_model_number
			BM=s.number_to_model_correspondance[bounce_model_number]
			BM.run(r,f)
			cp=r.pos-r.radius*f.normal
			#Push the sphere outside the face along the z axis. Use the z axis and not face.normal as the latter would cause bugs in Posprocessings.
			r.pos[2]+=-(f.normal[0]*(cp[0]-f.points[0].pos[0]) + f.normal[1]*(cp[1]-f.points[0].pos[1]))/f.normal[2]+f.points[0].pos[2]-cp[2]+0.01*r.radius
			s.output.add_contact(r,BM.updated_normal,Out.SOIL)

class Rock_tree_nscd_basic_contact(Engine):
	"""
	FIXME : doc
	"""
	def __init__(self,**kwargs):
		super(Rock_tree_nscd_basic_contact,self).__init__(**kwargs)
	def run(self,s):
		r=s.current_rock
		if(not r.terrain_active_contact and r.tree_active_contact):
			t=r.tree_active_contact.tree
			Debug.info("Rock-tree contact !")
			vel=r.vel.norm()
			vol=r.volume
			
			vxy_rock=Math.Vector2(r.vel[0:2])
			xy_contact_point=t.pos+t.dhp/2/100*Math.normalized2(r.pos[0:2]-t.pos)
			ecc_axis=Math.Vector2([-vxy_rock[1],vxy_rock[0]]).normalized() #the normed axis, orthogonal to vxy, on which the eccentricity is measured from the contact point and vxy
			ecc=(xy_contact_point-t.pos).dot(ecc_axis)/(t.dhp/2./100)	#eccentricity, from -1 to 1
			ang=np.sign(r.vel[2])*abs(np.degrees(np.arctan(r.vel[2]/vxy_rock.norm()))) # the vertical incident angle.
			angle=np.arctan2(vxy_rock[1],vxy_rock[0])	#the signed angle between the rock xy velocity and the +x axis. NOTE: arctan2=arctan2(y,x)
			r.vel[:]=s.forest_impact_model.get_output_vel(vel,vol,abs(ecc),t.dhp,ang) #we use abs(ecc) as the DEM model is symetric, see the line below for ecc<0. The vel here is expressed in Toe's C.S.
			if(ecc<0):r.vel[1]*=-1
			r.vel[0:2]=Math.rotated2(r.vel[0:2],angle) #rotate the vel to translate from Toe's C.S to our global C.S.
			normal=r.pos.copy()
			normal[0:2]-=t.pos
			normal=normal.normalized()
			s.output.add_contact(r,normal,Out.TREE)
			t.active=False
			if(s.GUI_enabled):
				t.color=[0.8,0,0]
				s.GUI.updateTreeColor(t)
			
			
class Snapshooter(Engine):
	def __init__(self,filename="snap_",**kwargs):
		super(Snapshooter,self).__init__(**kwargs)
		self.filename=filename
		self.ndone=0
	def run(self,s):
		s.GUI.take_snapshot(self.filename+str(self.ndone).rjust(6,"0")+".png")
		self.ndone+=1
		
class Time_stepper(Engine):
	def __init__(self,safety_coefficient=0.1,**kwargs):
		super(Time_stepper,self).__init__(**kwargs)
		self.safety_coefficient=safety_coefficient
	def run(self,s):
		s.dt=self.safety_coefficient*s.current_rock.radius/(s.current_rock.vel.norm())
		s.dt=min(s.dt,0.1)
		#Debug.warning("New time step:",s.dt)
		


class Siconos(Engine):
	def __init__(self,terrain=None,dt=0.02,**kwargs):
		super(Siconos,self).__init__(**kwargs)
		from siconos.kernel import NonSmoothDynamicalSystem, MoreauJeanDirectProjectionOSI, TimeDiscretisation, TimeSteppingDirectProjection, FrictionContact, SICONOS_TS_NONLINEAR, NewtonImpactFrictionNSL,MLCPProjectOnConstraints
		from siconos.numerics import SICONOS_FRICTION_3D_NSGS, SICONOS_FRICTION_3D_NSGS_ERROR_EVALUATION_LIGHT, SICONOS_FRICTION_3D_NSGS_FILTER_LOCAL_SOLUTION_TRUE, SICONOS_FRICTION_3D_ONECONTACT_NSN_GP_HYBRID,SICONOS_MLCP_ENUM
		from siconos.mechanics.collision.bullet import SiconosBulletCollisionManager, SiconosBulletOptions
		from siconos.io.io_base import MechanicsIO
		
		self.io = MechanicsIO()
		self.nsds = NonSmoothDynamicalSystem(0,np.inf)
		self.timedisc=TimeDiscretisation(0, dt)#FIXME FIXME FIXME : set DT here !
		
		self.osi=MoreauJeanDirectProjectionOSI(0.50001)
		
		self.osnspb=FrictionContact(3,SICONOS_FRICTION_3D_NSGS)
		self.osnspb.setMaxSize(30000)	#NOTE: what is that ?
		self.osnspb.setMStorageType(1)
		self.osnspb.setNumericsVerboseMode(False)
		self.osnspb.setKeepLambdaAndYState(True)
		solverOptions = self.osnspb.numericsSolverOptions()
		solverOptions.iparam[0] = 1000		#iter max
		solverOptions.dparam[0] = 1e-5			#tolerance
		solverOptions.iparam[1] = SICONOS_FRICTION_3D_NSGS_ERROR_EVALUATION_LIGHT
		solverOptions.iparam[14] = SICONOS_FRICTION_3D_NSGS_FILTER_LOCAL_SOLUTION_TRUE
		fcOptions = solverOptions.internalSolvers[0]
		fcOptions.iparam[0] = 20
		fcOptions.solverId = SICONOS_FRICTION_3D_ONECONTACT_NSN_GP_HYBRID
		
		self.osnspb_pos=MLCPProjectOnConstraints(SICONOS_MLCP_ENUM, 1.0)
		self.osnspb_pos.setMaxSize(30000)
		self.osnspb_pos.setMStorageType(0) # "not yet implemented for sparse storage"
		self.osnspb_pos.setNumericsVerboseMode(False)
		self.osnspb_pos.setKeepLambdaAndYState(True)
		
		self.sim=TimeSteppingDirectProjection(self.nsds,self.timedisc,self.osi,self.osnspb,self.osnspb_pos)
		self.sim.setProjectionMaxIteration(20)
		self.sim.setConstraintTolUnilateral(1e-5);
		self.sim.setConstraintTol(1e-5);
		#self.sim.insertIntegrator(self.osi)
		#self.sim.insertNonSmoothProblem(self.osnspb)
		
		self.interman=SiconosBulletCollisionManager(SiconosBulletOptions())
		self.sim.insertInteractionManager(self.interman)
		
		self.sim.setNewtonOptions(SICONOS_TS_NONLINEAR)
		self.sim.setNewtonMaxIteration(1)
		self.sim.setNewtonTolerance(1e-5)
		self.add_terrain(terrain)
		self.nsl=NewtonImpactFrictionNSL(0.,0.,0.6,3) #NOTE: en, et, mu, ?
		self.interman.insertNonSmoothLaw(self.nsl, 1, 2)
		
	def add_terrain(self,terrain):
		from siconos.mechanics.collision import SiconosContactor, SiconosContactorSet
		cset = SiconosContactorSet()
		csetpos = [0,0,0,1,0,0,0]
		hm,offsets=terrain.get_siconos_heightmap()
		cset.append(SiconosContactor(hm, [offsets[0],offsets[1],0,1,0,0,0], 1))
		#if(terrain.enable_forest):	#FIXME: enable the forest flag
		from siconos.mechanics.collision import SiconosCylinder
		for t in terrain.trees:
			lowest_terrain_point_z=terrain.points_as_array[:,2].min()
			highest_terrain_point_z=terrain.points_as_array[:,2].max()+50.
			cylinders_height=highest_terrain_point_z-lowest_terrain_point_z
			cyl=SiconosCylinder(t.dhp/2/100,cylinders_height)
			q=quaternion.from_rotation_vector([np.pi/2,0,0])
			cset.append(SiconosContactor(cyl, [t.pos[0],t.pos[1],lowest_terrain_point_z+cylinders_height/2.,q.w,q.x,q.y,q.z], 1))
		self.interman.insertStaticContactorSet(cset, csetpos)
	
	def add_rock(self,r):
		from siconos.mechanics.collision import RigidBodyDS, SiconosContactorSet, SiconosContactor
		self.DS = RigidBodyDS(r.pos.tolist() + [r.ori.w,r.ori.x,r.ori.y,r.ori.z], r.vel.tolist(), r.mass, 0.0*np.eye(3))#NOTE:  0.0*np.eye(3) is the inertia
		cset = SiconosContactorSet()
		csetpos = [0,0,0,1,0,0,0]
		cset.append(SiconosContactor(r.get_siconos_convex_hull(), csetpos, 2))
		self.DS.setContactors(cset)
		#self.DS.setNumber(np.random.randint(1e10)) #NOTE : set something else maybe
		self.nsds.insertDynamicalSystem(self.DS)
		#self.nsds.setName(self.DS, str(name))	#NOTE: set a name maybe
		self.DS.setFExtPtr([0, 0, - self.DS.scalarMass() * 9.8])#FIXME: set s.g intead of hardcoding

	def remove_rock(self):
		self.interman.removeBody(self.DS)
		self.nsds.removeDynamicalSystem(self.DS)
	
		
	
	def run(self,s):
		ds_nb=self.nsds.getNumberOfDS()-1
		shapely_point=shapely.geometry.Point(s.current_rock.pos[0:2])
		for i in range(len(s.terrain.soil_params)):	
			if(s.terrain.soil_params[i]["shapely_polygon"].contains(shapely_point)): #NOTE: this could be optimized by avoiding updating mu and e when the rock doesn't change from polygon (when i==0)
				mu=s.terrain.soil_params[i]["params"].get("mu",s.terrain.default_faces_params["mu"])
				e=s.terrain.soil_params[i]["params"].get("e",s.terrain.default_faces_params["e"])
				self.nsl.setEn(e)
				self.nsl.setMu(mu)
				s.terrain.soil_params.insert(0,s.terrain.soil_params.pop(i))	#swap poly_params sequence: put the current one at the first position to increase speed
				break
			#if no polygon found:
			mu=s.terrain.default_faces_params["mu"]
			e=s.terrain.default_faces_params["e"]
		self.sim.computeOneStep()
		s.current_rock.pos[:]=self.DS.q()[0:3]
		s.current_rock.vel[:]=self.DS.velocity()[0:3]
		s.current_rock.angVel[:]=self.DS.velocity()[3:]
		s.current_rock.ori.w=self.DS.q()[3]
		s.current_rock.ori.x=self.DS.q()[4]
		s.current_rock.ori.y=self.DS.q()[5]
		s.current_rock.ori.z=self.DS.q()[6]
		if(self.nsds.getNumberOfInteractions()>0 and (self.io.contactPoints(self.nsds) is not None)):
			normal=Math.normalized3(self.io.contactPoints(self.nsds)[:,7:10].mean(axis=0))
			s.output.add_contact(s.current_rock,normal,Out.SOIL)
		if(s.GUI_enabled):
			s.current_rock.update_members_pos()
		if(s.current_rock.pos[2]<s.terrain.min_height):
			Debug.warning("The rock went outside the terrain !")
			s.current_rock.out_of_bounds=True
			s.current_rock.is_stopped=True
		self.sim.clearNSDSChangeLog()
		self.sim.nextStep()





#...........::::::::::::: DEPRECATED/UNDER DEVELOPMENT :::::::::::............



class Newton_integrator(Engine):
	"""
	Convert the force and torque applied to the rock into translation and rotation. Acutally move/rotate the rock. This engine also stores copies of the contacts into :attr:`ThreeD.Objects.Rock.contacts` list.
	"""
	def run(self,s):
		r=s.current_rock
		
		# TRANSLATION :
		linAccel=r.force/r.mass + np.array([0.,0.,-s.gravity])
		r.vel+=s.dt*linAccel
		r.pos+=r.vel*s.dt
		
		# ROTATION :
		A				=	quaternion.as_rotation_matrix(r.ori.conjugate())			# rotation matrix from global to local r.f.
		l_n				=	r.angMom + s.dt/2. * r.torque								# global angular momentum at time n
		l_b_n			=	np.dot(A,l_n)												# local angular momentum at time n
		angVel_b_n		=	l_b_n/r.I													# local angular velocity at time n
		dotQ_n			=	Math.DotQ(angVel_b_n,r.ori)									# dQ/dt at time n
		Q_half			=	r.ori + s.dt/2. * dotQ_n									# Q at time n+1/2
		r.angMom		+=	s.dt*r.torque												# global angular momentum at time n+1/2
		l_b_half		=	np.dot(A,r.angMom)											# local angular momentum at time n+1/2
		angVel_b_half	=	l_b_half/r.I												# local angular velocity at time n+1/2
		dotQ_half		=	Math.DotQ(angVel_b_half,Q_half)								# dQ/dt at time n+1/2
		r.ori			=	r.ori + s.dt*dotQ_half										# Q at time n+1
		r.angVel		=	quaternion.rotate_vector(r.ori,angVel_b_half)				# global angular velocity at time n+1/2
		r.ori			=	r.ori.normalized()
		
		
		# MOVE THE POINTS ACCORDINGLY
		r.update_members_pos()
		
		# EVENTUALLY STORE THE CONTACT PROPERTIES FOR POST-PROCESSING
		if(len(r.terrain_active_contacts["terrain"])>0): #NOTE : r.terrain_active_contacts["terrain"] normally contains only one element. NOTE 2 : make hard copy of all variables
			r.contacts.append(r.terrain_active_contacts["terrain"][0].get_storage_copy(r))
		#FIXME : uncomment below to store rock-tree contacts when postprocessing will allow it
		#if(len(r.terrain_active_contacts["tree"])>0):
			#r.contacts.append(r.terrain_active_contacts["tree"][0].get_storage_copy(r))
			
		
class Rock_terrain_nscd_contact(Engine):
	"""
	Choose the contact for which the interpenetration is maximal and append the corresponding force/torque on the rock. NSCD stands for non-smooth contact-dynamics, meaning that the contact is instantaneous: from the input velocity and the contact properties, we compute the output velocity. Then the force/torque corresponding to the (input-output) velocity difference are computed.
	"""
	def run(self,s):
		maxDist=np.inf
		contact=None
		r=s.current_rock
		for c in r.terrain_active_contacts["terrain"]:	#only keep the most interpenetrated contact
			if(c.status==1 and maxDist>c.dist):
				contact=c
				maxDist=c.dist
		if(contact):
			r.terrain_active_contacts["terrain"]=[contact] #remove multiple contacts here
			p=contact.point
			f=contact.face
			
			#Compute point velocity and decompose
			p.vel=r.vel+(r.pos-p.pos).cross(r.angVel)
			p_vel_n=p.vel.dot(f.normal)*f.normal
			p_vel_t=p.vel-p_vel_n
			
			#Apply rebound
			p_vel_n *= -r.R_n
			p_vel_t *= r.R_t
			
			#Compute velocity difference
			delta_p_vel = (p_vel_n+p_vel_t) - p.vel
			
			#Compute the force/torque needed to get the velocity difference

			r.force  +=  r.mass/s.dt*delta_p_vel
			r.torque +=  (p.pos-r.pos).cross(r.force)
			
			#Position correction to avoid real penetration of the rock into the face
			r.pos-=f.normal*contact.dist*1.001
			
			#The contact is computed, set the status accordingly
			contact.status=2
			
class Rock_tree_basic_contact(Engine):
	"""
	Choose the contact for which the interpenetration is maximal and append the corresponding force/torque on the rock. The contact is instantaneous: from the input velocity and the contact properties, we compute the output velocity. Then the force/torque corresponding to the (input-output) velocity difference are computed.
	"""
	def run(self,s):
		maxDist=np.inf
		contact=None
		r=s.current_rock
		for c in r.terrain_active_contacts["tree"]:	#only keep the most interpenetrated contact
			if(c.status==1 and maxDist>c.dist):
				contact=c
				maxDist=c.dist
		if(contact):
			r.terrain_active_contacts["tree"]=[contact] #remove multiple contacts here
			normal=(r.pos[0:2]-contact.tree.pos).normalized()
			contact.pos=Math.Vector3([0.,0.,r.pos[2]])
			contact.pos[0:2]=contact.tree.pos+(contact.tree.dhp/2./100)*normal
			
			normalized_rock_vel=r.vel[0:2].normalized()
			contact.eccentricity=( contact.pos[0:2] + (contact.tree.pos - contact.pos[0:2]).dot(normalized_rock_vel)*normalized_rock_vel - contact.tree.pos ).norm() / (contact.tree.dhp/2./100)
			
			#Compute the force needed to get the velocity difference
			v_factor=0.8+0.2*contact.eccentricity
			vel_n=r.vel[0:2].dot(normal)*normal
			vel_t=r.vel[0:2]-vel_n
			new_vel_2D = -vel_n + vel_t
			delta_v = Math.Vector3([new_vel_2D[0]*v_factor,new_vel_2D[1]*v_factor,r.vel[2]]) - r.vel
			r.force+=r.mass/s.dt*delta_v
			
			#Position correction to avoid real penetration of the rock into the tree
			r.pos[0:2] -= normal*contact.dist*1.001
			
			contact.tree.active=False
			contact.tree.color=[0.8,0,0]
			if(s.GUI_enabled):
				s.GUI.updateTreeColor(contact.tree)
			contact.status=2
		
		
		
		
		
		
		
		
