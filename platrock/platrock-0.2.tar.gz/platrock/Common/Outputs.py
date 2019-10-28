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
This module is used to store output data in a optimized hdf5 file.
"""

import h5py
import numpy as np
import platrock.Common.Debug as Debug

float_type = np.float32

#Contact types :
START=0
SOIL=1
TREE=2
ROLL_TREE=3	#contact with a tree while rolling
ROLL=4		#for rolling-friction algo
STOP=5		#at the end if the rock was stopped
OUT=6		#at the end if the rock went outside the terrain
FLY=7		#used for ThreeD.Postprocessings to describe a fly-over-raster-cell
MOTION=8	#used by TwoDShape to track the motion of the rocks (don't really track contacts)

class Contact_field(object):
	def __init__(self,name,slice):
		self.name=name
		self.slice=slice

class Output(object):
	def __init__(self,s):
		self._s=s
		
		self._rocks_counter=0
		sim_type=self._s.__module__
		if sim_type=="platrock.TwoD.Simulations" or sim_type=="platrock.TwoDShape.Simulations" :
			self._ndim=2
			self.contacts_slices = {
				"types":slice(0,1),
				"rock_pos":slice(1,3),
				"rock_output_vels":slice(3,5),
				"rock_output_angVels":slice(5,6),
				"normals":slice(6,8)
			}
		elif sim_type=="platrock.ThreeD.Simulations" :
			self._ndim=3
			self.contacts_slices = {
				"types":slice(0,1),
				"rock_pos":slice(1,4),
				"rock_output_vels":slice(4,7),
				"rock_output_angVels":slice(7,10),
				"normals":slice(10,13)
			}
		self._contacts_fields_length=0
		for cs in self.contacts_slices.values():
			self._contacts_fields_length+=cs.stop-cs.start
		
		self.checkpoints=None #this is a list directly exported from the "update_checkpoints" function
		self.volumes=np.empty([self._s.nb_rocks],dtype=float_type)
		self.densities=np.empty([self._s.nb_rocks],dtype=float_type)
		if self._ndim==2:
			self.inertias=np.empty([self._s.nb_rocks],dtype=float_type)
		else:
			self.inertias=np.empty([self._s.nb_rocks,3,3],dtype=float_type) #3X3 matrix
		self.contacts=[]

	def add_rock(self,r):
		self.volumes[self._rocks_counter]=float_type(r.volume)
		self.densities[self._rocks_counter]=float_type(r.density)
		if self._ndim==2:
			self.inertias[self._rocks_counter]=float_type(r.I)
		elif r.I.shape==(3,): #diagonal
			self.inertias[self._rocks_counter]=float_type(np.identity(3)*r.I)
		elif r.I.shape==(3,3): #matrix
			self.inertias[self._rocks_counter]=r.I
		else:
			Debug.error("This rock has an invalid inertia shape:",r.I)
		self.contacts.append(np.empty([0,self._contacts_fields_length],dtype=float_type))
		self._rocks_counter+=1
	
	def add_contact(self,r,normal,type_):
		new_contact_data=np.concatenate((
			[type_],
			r.pos,
			r.vel,
			r.angVel,
			normal
		)).astype(float_type)
		self.contacts[-1]=np.append(self.contacts[-1],[new_contact_data],axis=0)
	
	def del_contact(self,rock_id,contact_id):
		if contact_id == -1:
			self.contacts[rock_id]=self.contacts[rock_id][:contact_id]
		else:
			self.contacts[rock_id]=np.append(self.contacts[rock_id][:contact_id] , self.contacts[rock_id][contact_id+1:])
	
	def get_contacts_field(self,rock_id,field):
		return self.contacts[rock_id][:,self.contacts_slices[field]]
	def get_contacts_pos(self,rock_id):
		return self.get_contacts_field(rock_id,"rock_pos")
	def get_contacts_vels(self,rock_id):
		return self.get_contacts_field(rock_id,"rock_output_vels")
	def get_contacts_angVels(self,rock_id):
		if(self._ndim==2):
			return self.get_contacts_field(rock_id,"rock_output_angVels")[:,0]
		else:
			return self.get_contacts_field(rock_id,"rock_output_angVels")
	def get_contacts_types(self,rock_id):
		return self.get_contacts_field(rock_id,"types")[:,0]
	def get_contacts_normals(self,rock_id):
		return self.get_contacts_field(rock_id,"normals")

	def write_to_h5(self,filename):
		with h5py.File(filename, "w") as f:
			
			#GENERAL STRUCTURE:
			# hdf5-file/
			# ├── rocks/
			# |   ├── start_data
			# |   ├── contacts/
			# |   |   ├── 0 (contacts of rock n°0)
			# |   |   ├── ..
			# |   |   └── nb_rocks
			# └── checkpoints/
			#     ├── x_0 (x position of checkpoint 0)
			#     ├── x_1
			#     └── x_N

			f.create_group("rocks")
			f.create_group("rocks/contacts")
			f.create_group("checkpoints")
			
			#ROCKS START DATA:
			#prepare data:
			
			if self._ndim==2:
				inertias = self.inertias.reshape([self._s.nb_rocks,1])
			else :
				inertias = self.inertias.reshape([self._s.nb_rocks,9])
			start_data=np.concatenate((
				self.volumes.reshape([self._s.nb_rocks,1]),
				self.densities.reshape([self._s.nb_rocks,1]),
				inertias
			),axis=1).astype(float_type)
			#write to file:
			f.create_dataset("rocks/start_data",data=start_data)
			#add attributes that embed the links between start_data columns and data types
			f["rocks/start_data"].attrs["volumes"]=0
			f["rocks/start_data"].attrs["densities"]=1
			if(self._ndim==2):
				f["rocks/start_data"].attrs["inertias"]=2
			else:
				f["rocks/start_data"].attrs["inertias"]=[2,10]
			
			#ROCKS CONTACTS DATA:
			#loop on "rocks"
			for i in range(len(self.contacts)):
				#write the contacts of the rock i
				f.create_dataset("rocks/contacts/"+str(i),data=self.contacts[i].astype(float_type))
			#add attributes that embed the links between contacts data columns and data types
			for k in self.contacts_slices.keys():
				f["rocks/contacts"].attrs[k]=[self.contacts_slices[k].start,self.contacts_slices[k].stop-1]
			
			#CHECKPOINTS:
			if(self._s.checkpoints is not None):	#FIXME : ThreeD has currently no checkpoints
				for c in self.checkpoints:
					data_len=len(c.heights)
					if(data_len):
						if self._ndim == 2 :
							angVels=np.asarray(c.angVels).reshape([data_len,1])
						else:
							angVels=np.asarray(c.angVels)
						chckpt_data=np.concatenate((
							np.asarray(c.rocks_ids).reshape([data_len,1]),
							np.asarray(c.heights).reshape([data_len,1]),
							np.asarray(c.vels),
							angVels,
						),axis=1)
					else:
						chckpt_data=np.array([])
					print(chckpt_data)
					f.create_dataset("checkpoints/"+str(c.x),data=chckpt_data.astype(float_type))
					f["checkpoints"].attrs["rocks_ids"]=[0,0]
					f["checkpoints"].attrs["heights"]=[1,1]
					if(self._ndim==2):
						f["checkpoints"].attrs["vels"]=[2,3]
						f["checkpoints"].attrs["angVels"]=[4,4]
					else:
						f["checkpoints"].attrs["vels"]=[2,4]
						f["checkpoints"].attrs["angVels"]=[5,7]
				
