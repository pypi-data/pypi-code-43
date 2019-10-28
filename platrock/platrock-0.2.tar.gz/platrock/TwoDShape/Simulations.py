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

import platrock.Common.Simulations
import platrock.TwoD.Simulations
from   platrock.Common.PyUtils import FriendImporter
import platrock.Common.Math as Math
import platrock.Common.Outputs as Out
from . import Objects
import numpy as np
import copy
from siconos.mechanics.collision.bullet import SiconosBulletCollisionManager, SiconosBulletOptions
from siconos.kernel import DynamicalSystem, NonSmoothDynamicalSystem, MoreauJeanOSI, TimeDiscretisation, RollingFrictionContact, TimeStepping, SICONOS_TS_NONLINEAR, NewtonImpactRollingFrictionNSL
from siconos.mechanics.collision import RigidBody2dDS, SiconosContactorSet, SiconosContactor, SiconosConvexHull2d
from siconos.io.io_base import MechanicsIO

from siconos.io.mechanics_run import MechanicsHdf5Runner
from siconos.mechanics.collision.tools import Contactor

#FIXME: remove these:
from siconos.kernel import FrictionContact, NewtonImpactFrictionNSL

class Simulation(platrock.Common.Simulations.Simulation,FriendImporter):
	webui_typename="PlatRock 2D-Shape"
	valid_rocks_start_params=copy.deepcopy(platrock.TwoD.Simulations.Simulation.valid_rocks_start_params)
	#We imported valid_rocks_start_params from TwoD.Simulations.Simulation, but don't want rocks_volume to be a valid input parameter:
	ID=np.where(valid_rocks_start_params[:,0]=="rocks_volume")[0][0]
	valid_rocks_start_params=np.concatenate((valid_rocks_start_params[:ID],valid_rocks_start_params[ID+1:]))
	#And we want to add these params:
	valid_rocks_start_params=np.concatenate((valid_rocks_start_params,
		np.array([
			["random_rocks_ori",	"Random rocks orientation",				bool,		False,		True	],
			["rocks_ori",			"Rocks orientation (degrees)",			int,		0,			359		]
		])
	))
	
	friendClass=platrock.TwoD.Simulations.Simulation
	friendImportNames=[
		"nb_rocks",
		"rocks_density",
		"rocks_x",
		"rocks_z",
		"rocks_vx",
		"rocks_vz",
		"rocks_angVel",
		"update_checkpoints",
		"checkpoints",
		"save_to_file",
		"after_rock_propagation_tasks",
		"after_successful_run_tasks",
		"results_to_zipfile",
		"get_stops_cdf"
	]

	def __init__(self,*args,rocks_start_params={},checkpoints_x=[],**kwargs):
		super(Simulation,self).__init__(*args,**kwargs) #first parent
		FriendImporter.__init__(self, rocks_start_params=rocks_start_params,checkpoints_x=checkpoints_x)
		
		self.random_rocks_ori=False
		self.rocks_ori=0.
		
		#OVERRIDE THE DEFAULT PARAMS, IF AVAILABLE IN rocks_start_params dict.
		for k in rocks_start_params.keys():
			if(k in self.valid_rocks_start_params[:,0]):
				self.__dict__[k]=rocks_start_params[k]
		
		self.rocks_shape_type=Objects.Ellipse #mainly for webui
		self.rocks_shape_params={}
		self.export_hdf5=False
		self.last_record_pos=Math.Vector2([np.inf,np.inf])
	
	def terrain_to_siconos_hdf5(self):
		with MechanicsHdf5Runner(self.name+".hdf5") as io:
			for seg in self.terrain.segments:
				io.add_convex_shape('Seg'+str(seg.index),seg.siconos_points)
				io.add_object('seg'+str(seg.index), [Contactor('Seg'+str(seg.index))] ,translation=[0,0])
	
	def rock_to_siconos_hdf5(self,r):
		with MechanicsHdf5Runner(self.name+".hdf5",mode="r+") as io:
			io._number_of_dynamic_objects=self.current_rock_number #tweak this as add_object() uses it to index objects in hdf5.
			io.add_convex_shape('Rock'+str(self.current_rock_number),r.vertices)
			io.add_object('rock'+str(self.current_rock_number), [Contactor('Rock'+str(self.current_rock_number))], mass=1., inertia=1., translation=r.pos.tolist())
			
	def setup_siconos(self,dt=0.02):
		self.io = MechanicsIO()
		bulletOptions = SiconosBulletOptions()
		bulletOptions.worldScale = 1.0
		bulletOptions.contactBreakingThreshold = 0.04
		bulletOptions.dimension = 1
		self.interman=SiconosBulletCollisionManager(bulletOptions)
		self.nsds = NonSmoothDynamicalSystem(0,np.inf)
		DynamicalSystem.resetCount(0)
		self.osi = MoreauJeanOSI(0.50001)
		self.osi.setConstraintActivationThreshold(0.0)
		self.timedisc=TimeDiscretisation(0, dt)#FIXME FIXME FIXME : set DT here !
		
		#self.osnspb=RollingFrictionContact(3)
		self.osnspb=FrictionContact(2)
		self.osnspb.setMaxSize(30000)
		self.osnspb.setMStorageType(1)
		
		solverOptions = self.osnspb.numericsSolverOptions()
		solverOptions.iparam[0] = 1000		#iter max tester 100
		solverOptions.dparam[0] = 1e-5		#tolerance tester 1e-3
		self.osnspb.setNumericsVerboseMode(False)
		self.osnspb.setKeepLambdaAndYState(True)
		
		self.sim=TimeStepping(self.nsds,self.timedisc)
		self.sim.insertIntegrator(self.osi)
		self.sim.insertNonSmoothProblem(self.osnspb)
		self.sim.insertInteractionManager(self.interman)
		self.sim.setNewtonOptions(SICONOS_TS_NONLINEAR)
		self.sim.setNewtonMaxIteration(1)
		self.sim.setNewtonTolerance(1e-5) #tester 1e-3
		self.sim.setDisplayNewtonConvergence(False)
		
	def add_terrain(self):
		terrain_points=self.terrain.get_points()
		terrain_min_z=terrain_points[:,1].min()-10
		for seg in self.terrain.segments:
			seg.siconos_points=np.array([	[seg.points[0][0],terrain_min_z],
								[seg.points[1][0],terrain_min_z],
								[seg.points[1][0],seg.points[1][1]],
								[seg.points[0][0],seg.points[0][1]]
							])
			dims = [	seg.siconos_points[:,0].max() - seg.siconos_points[:,0].min(),
						seg.siconos_points[:,1].max() - seg.siconos_points[:,1].min()]
			shp=SiconosConvexHull2d(seg.siconos_points)
			shp.setInsideMargin(min(dims)*0.02)
			shp.setOutsideMargin(0)
			csetpos = [0,0,0,1,0,0,0]
			cset = SiconosContactorSet()
			cset.append(SiconosContactor(shp, csetpos, seg.index+1))
			self.interman.insertStaticContactorSet(cset,csetpos)
			#seg.nsl=NewtonImpactRollingFrictionNSL(seg.e, 0., seg.mu, seg.mu_r, 3) # en, et, mu, mu_r, ndim
			seg.nsl=NewtonImpactFrictionNSL(seg.e, 0., seg.mu, 2) # en, et, mu, ndim
			self.interman.insertNonSmoothLaw(seg.nsl, seg.index+1, 0)
		
	
	def add_rock(self):
		self.reset_rock_kinematics()
		r=self.current_rock
		self.DS=RigidBody2dDS(r.pos.tolist()+[r.ori],r.vel.tolist()+r.angVel.tolist(), r.mass, r.I)
		self.DS.setNumber(self.current_rock_number+1)
		self.DS.setUseContactorInertia(False)
		self.DS.setAllowSelfCollide(False)
		cset = SiconosContactorSet()
		cset.append(SiconosContactor(r.get_siconos_shape(), [0,0,0,1,0,0,0], 0))
		self.DS.setContactors(cset)
		self.nsds.insertDynamicalSystem(self.DS)
		self.nsds.setName(self.DS, 'rock'+str(self.current_rock_number))
		self.DS.setFExtPtr([0, - self.DS.scalarMass() * self.gravity,0])
		if self.export_hdf5 :
			self.rock_to_siconos_hdf5(self.current_rock)
	
	def reset_rock_kinematics(self):
		r=self.current_rock
		r.setup_kinematics(x=self.rocks_x, height=self.rocks_z, vel=Math.Vector2([self.rocks_vx,self.rocks_vz]), angVel=self.rocks_angVel)
		if(self.random_rocks_ori):
			r.ori=self.random_generator.rand()*np.pi*2
		else:
			r.ori=np.radians(self.rocks_ori)
		r.update_current_segment(self.terrain)
		r.pos[1]+=r.current_segment.get_y(r.pos[0])
	
	def remove_rock(self):
		self.nsds.removeDynamicalSystem(self.DS)
		self.interman.removeBody(self.DS)
		

	def before_run_tasks(self):
		super(Simulation, self).before_run_tasks()
		self.setup_siconos()
		self.add_terrain()
		if self.export_hdf5 :
			self.terrain_to_siconos_hdf5()
			#if self.export_hdf5 :
			self.hdf5_io = MechanicsHdf5Runner(self.name+".hdf5",mode='r+')
			self.hdf5_io.__enter__()
			self.hdf5_io._nsds=self.nsds
			self.hdf5_io._simulation=self.sim

	def before_rock_launch_tasks(self):
		import time
		super(Simulation, self).before_rock_launch_tasks()
		self.add_rock()
		self.reset_rock_kinematics()
		self.last_record_pos=Math.Vector2([np.inf,np.inf])
		self.output.add_rock(self.current_rock)
		self.output.add_contact(self.current_rock,Math.Vector2([0.,0.]),Out.START) #store the rock initial position
		

	def rock_propagation_tasks(self):
		self.sim.computeOneStep()
		if self.export_hdf5 :
			self.hdf5_io.output_dynamic_objects()
			self.hdf5_io.output_velocities()
			self.hdf5_io.output_contact_forces()
			self.hdf5_io.output_solver_infos()
			self.hdf5_io._out.flush()
		pos=self.DS.q()
		vel=self.DS.velocity()
		
		#Check out_of_bounds
		if	pos[0]<self.terrain.segments[0].points[0][0] or \
			pos[0]>self.terrain.segments[-1].points[1][0] or \
			pos[1]<self.terrain.get_y_range()[0] :
			self.current_rock.out_of_bounds=True
			self.current_rock.is_stopped=True
		
		#Record trajectory
		if (self.last_record_pos-pos[0:2]).norm() > max(self.current_rock.dims)*5 :
			self.current_rock.pos=Math.Vector2(pos[0:2])
			self.current_rock.ori=pos[2]
			self.current_rock.vel=Math.Vector2(vel[0:2])
			self.current_rock.angVel=Math.Vector1([vel[2]])
			self.output.add_contact(self.current_rock,Math.Vector2([0,0]),Out.MOTION)
			if self.current_rock.vel.norm() < 1e-2:
				self.current_rock.is_stopped=True
				self.remove_rock()
		self.sim.clearNSDSChangeLog()
		self.sim.nextStep()

	def after_all_tasks(self):
		super(Simulation, self).after_all_tasks()
		if self.export_hdf5 :
			self.hdf5_io.__exit__(None, None, None)
















