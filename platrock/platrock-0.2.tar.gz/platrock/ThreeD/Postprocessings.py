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

# TODO: forest integration 
import numpy as np
#from . import Objects
import platrock.Common.Math as Math
from . import RasterTools
import platrock.Common.Outputs as Out


class Postprocessing(object):
	def __init__(self,simulation,raster_cell_length=None):
		self.simulation=simulation
		if(raster_cell_length is None):
			self.raster=self.simulation.terrain.Z_raster
		else:
			self.raster=RasterTools.from_raster(simulation.terrain.Z_raster,cell_length=float(raster_cell_length))
	
	def get_indices_cleaned(self,arr):
		arr_shift1=np.roll(arr,1,axis=0) ; arr_shift1[0]=np.NaN
		arr_shift2=np.roll(arr,-1,axis=0); arr_shift2[-1]=np.NaN
		XCompare=np.where(arr_shift1[:,0]!=arr_shift2[:,0])[0]
		YCompare=np.where(arr_shift1[:,1]!=arr_shift2[:,1])[0]
		return np.unique( np.concatenate((XCompare,YCompare)) )
	
	def get_raster_indices_from_contacts(self,c_pos,c_types):
		Len=np.sum(c_types!=Out.OUT) # exclude out of bounds contacts as it will likely give cells indices outside raster.
		raster_indices=np.empty([Len,2],dtype=int)
		for i in range(Len):
			raster_indices[i]=self.raster.get_indices_from_coords(c_pos[i,0:2])
		return raster_indices
	
	def insert_fly(self,arrays_dict,where):
		for k in arrays_dict.keys():
			arrays_dict[k]=np.insert(arrays_dict[k],where,np.zeros(arrays_dict[k][0].shape),axis=0)
		arrays_dict["pos"][where]=arrays_dict["pos"][where-1]	#in the case of a flight, pos and vel are copied from the last known contact
		arrays_dict["vels"][where]=arrays_dict["vels"][where-1]
		arrays_dict["types"][where]=Out.FLY
		arrays_dict["angVels"][where]=arrays_dict["angVels"][where-1]
			
	def add_flights_to_raster_cells_and_contacts(self, raster_indices, all_c_fields):
		# A new contact type is now added : flights_over_cells
		#DETECT FLYING (contactless) CELLS ON THE RASTER :
		i=0
		while i < len(raster_indices)-1:
			ix, iy = raster_indices[i,0], raster_indices[i,1]
			ix_next, iy_next=raster_indices[i+1,0], raster_indices[i+1,1]
			cells_indices_distance=abs(ix_next-ix) + abs(iy_next-iy) # -> how far are the cells if I only jump through the cells edges (no diagonals) ?
			if(cells_indices_distance<=1): # consecutive contacts on the same raster cell (=0), or consecutive contacts on neighbours raster cell (=1)
				i+=1
				continue
			else:	#a fly occured : complete the rock path on the raster with flying cells
				current_pos=all_c_fields["pos"][i][0:2]
				branch=all_c_fields["pos"][i+1][0:2]-current_pos
				branch_angle=Math.atan2_unsigned(branch[1],branch[0])	#NOTE : x and y are inverted, this is a convention (see https://en.wikipedia.org/wiki/Atan2#Illustrations)
				ix2=ix ; iy2=iy
				while(abs(ix_next-ix2) + abs(iy_next-iy2)>1): #while we didn't reached a neighbour of the next contact cell ...
					SE_branch=np.array([ self.raster.X[ix2+1] , self.raster.Y[iy2] ])-current_pos#South-East
					SE_angle=Math.atan2_unsigned(SE_branch[1],SE_branch[0])
					
					SW_branch=np.array([ self.raster.X[ix2] , self.raster.Y[iy2] ])-current_pos#South-West
					SW_angle=Math.atan2_unsigned(SW_branch[1],SW_branch[0])
					
					if(branch_angle<=SE_angle and branch_angle>=SW_angle): #exiting the current cell by the BOTTOM edge
						current_pos=current_pos+branch*((self.raster.Y[iy]-current_pos[1])/branch[1])
						iy2-=1
						raster_indices=np.insert(raster_indices,i+1,[ix2,iy2],axis=0)
						self.insert_fly(all_c_fields,i+1)
						i+=1
					else:
						NW_branch=np.array([ self.raster.X[ix2] , self.raster.Y[iy2+1] ])-current_pos#North-West
						NW_angle=Math.atan2_unsigned(NW_branch[1],NW_branch[0])
						
						if(branch_angle<SW_angle and branch_angle>=NW_angle):#exiting the current cell by the LEFT edge
							current_pos=current_pos+branch*((self.raster.X[ix]-current_pos[0])/branch[0])
							ix2-=1
							raster_indices=np.insert(raster_indices,i+1,[ix2,iy2],axis=0)
							self.insert_fly(all_c_fields,i+1)
							i+=1
						else:
							NE_branch=np.array([ self.raster.X[ix2+1] , self.raster.Y[iy2+1] ])-current_pos#North-West
							NE_angle=Math.atan2_unsigned(NE_branch[1],NE_branch[0])
							if(branch_angle<NW_angle and branch_angle>=NE_angle):#exiting the current cell by the TOP edge
								current_pos=current_pos+branch*((self.raster.Y[iy+1]-current_pos[1])/branch[1])
								iy2+=1
								raster_indices=np.insert(raster_indices,i+1,[ix2,iy2],axis=0)
								self.insert_fly(all_c_fields,i+1)
								i+=1
							else:#exiting the current cell by the RIGHT edge
								current_pos=current_pos+branch*((self.raster.X[ix+1]-current_pos[0])/branch[0])
								ix2+=1
								raster_indices=np.insert(raster_indices,i+1,[ix2,iy2],axis=0)
								self.insert_fly(all_c_fields,i+1)
								i+=1
				i+=1
		return (raster_indices,all_c_fields)
	
	def run(self):
		self.raster.add_data_grid("crossings",int,0)
		self.raster.add_data_grid("heights",list)
		self.raster.add_data_grid("vels",list)
		self.raster.add_data_grid("stops",list) #at each stop, store the START cell coordinates
		self.raster.add_data_grid("Ec",list) #Kinetic energy
		for r_nb in range(self.simulation.nb_rocks):
			
			c_pos   = self.simulation.output.get_contacts_pos(r_nb)
			c_types = self.simulation.output.get_contacts_types(r_nb)
			
			#find cells from contacts pos:
			raster_indices = self.get_raster_indices_from_contacts(c_pos,c_types)
			
			#CLEANING PASS : when consecutive contacts on the same raster cell occurs, only keep the first one and the last one
			indices_duplicates_removed=self.get_indices_cleaned(raster_indices)
			raster_indices=raster_indices[indices_duplicates_removed]	# LIST OF RASTERS ON WHICH CONTACTS OCCURED
			c_pos=c_pos[indices_duplicates_removed]
			c_vels=self.simulation.output.get_contacts_vels(r_nb)[indices_duplicates_removed]
			c_types=c_types[indices_duplicates_removed]
			c_angVels=self.simulation.output.get_contacts_angVels(r_nb)[indices_duplicates_removed]
			all_c_fields={"pos":c_pos,"vels":c_vels,"types":c_types,"angVels":c_angVels}
			
			# add flights (cells with no contacts). Finally, len(raster_indices) == len(contacts), allowing to loop over both at the same time.
			raster_indices, all_c_fields = self.add_flights_to_raster_cells_and_contacts(raster_indices, all_c_fields)
			
			# Count the number of rocks that passed over each cell :
			rock_count=np.zeros(np.shape(self.raster.data["crossings"]),dtype=int) #init to 0
			for index in raster_indices:	#loop on cells the rocks passed over
				rock_count[index[0],index[1]]+=1	#increment
			rock_count[rock_count>0]=1			#limit the value to 0 to avoid multiple rebounds on a single cell
			self.raster.data["crossings"]+=rock_count	#add this rock_count to the global data
			
			self.raster.data["heights"][raster_indices[0,0],raster_indices[0,1]].append(all_c_fields["pos"][0][2])
			self.raster.data["vels"][raster_indices[0,0],raster_indices[0,1]].append(np.linalg.norm(all_c_fields["vels"][0]))
			self.raster.data["Ec"][raster_indices[0,0],raster_indices[0,1]].append(
				0.5*(
					self.simulation.output.densities[r_nb]*self.simulation.output.volumes[r_nb]*np.linalg.norm(all_c_fields["vels"][0])**2 + #translation
					np.dot(all_c_fields["angVels"][0],np.dot(self.simulation.output.inertias[r_nb],all_c_fields["angVels"][0])) #rotation
				)
			) # See below to have a more explicit computation of Ec
			for i in range(1,len(raster_indices)): #FIXME : if a rock come back into a cell, avoid it
				index=raster_indices[i]
				prev_index=raster_indices[i-1]
				if((index==prev_index).all()): # if the previous contact was in the same cell, do nothing
					continue
				previous_c_pos=all_c_fields["pos"][i-1]
				previous_c_vel=all_c_fields["vels"][i-1]
				if(prev_index[1]-index[1] == 1):# the rock came to the current cell from the north face
					yM=self.raster.Y[prev_index[1]]	#the y coordinate of north face of the cell
					time=(yM-previous_c_pos[1])/previous_c_vel[1] # time = flight time from last effective contact to the entering of the rock in the cell
					xM=previous_c_vel[0]*time+previous_c_pos[0]
				elif(prev_index[1]-index[1] == -1): # the rock came to the current cell from the south face
					yM=self.raster.Y[index[1]]	#the y coordinate of south face of the cell
					time=(yM-previous_c_pos[1])/previous_c_vel[1]
					xM=previous_c_vel[0]*time+previous_c_pos[0]
				elif(prev_index[0]-index[0] == 1):	# the rock came to the current cell from the east face
					xM=self.raster.X[prev_index[0]] #the x coordinate of east face of the cell
					time=(xM-previous_c_pos[0])/previous_c_vel[0]
					yM=previous_c_vel[1]*time+previous_c_pos[1]
				elif(prev_index[0]-index[0] == -1): # the rock came to the current cell from the west face
					xM=self.raster.X[index[0]] #the x coordinate of the west face of the cell
					time=(xM-previous_c_pos[0])/previous_c_vel[0]
					yM=previous_c_vel[1]*time+previous_c_pos[1]
				if(np.isnan(time)):	# NOTE: this is for a very specific case, if the rebound occurs exactly on a cell edge and with vx=0 and/or vy=0.
					vel=Math.Vector3(all_c_fields["vels"][i])
					absolute_height=all_c_fields["pos"][i][2]
				else: # this is the general case
					absolute_height=-0.5*self.simulation.gravity*time**2 + previous_c_vel[2]*time + previous_c_pos[2] #FIXME : compute relative height
					vel=Math.Vector3([previous_c_vel[0], previous_c_vel[1], previous_c_vel[2] - self.simulation.gravity*time])
				
				self.raster.data["heights"][index[0],index[1]].append(absolute_height)
				self.raster.data["vels"][index[0],index[1]].append(vel.norm())
				#Compute Ec and add it the the raster cell:
				I=self.simulation.output.inertias[r_nb]
				angVel=all_c_fields["angVels"][i]
				density=self.simulation.output.densities[r_nb]
				volume=self.simulation.output.volumes[r_nb]
				Ec=0.5*( density*volume*vel.norm()**2 + np.dot(angVel,np.dot(I,angVel)) ) # mv² + ω_t X I X ω
				self.raster.data["Ec"][index[0],index[1]].append(Ec)
			
			#Handle stops:
			if(c_types[-1]==Out.STOP):
				self.raster.data["stops"][index[0],index[1]].append(raster_indices[0])
		
		#Compute stats rasters based on other rasters:
		ids=np.where(self.raster.data["crossings"]!=0)
		for field in ["heights","vels", "Ec"]:
			for quantile in [90,95,99]:
				raster_data=self.raster.add_data_grid(field+"_quantile-"+str(quantile)+"%",float)
				for i,j in zip(*ids):
					raster_data[i,j]=np.quantile(self.raster.data[field][i,j],quantile/100,interpolation="linear")
		
		raster_data=self.raster.add_data_grid("number_of_source-cells",int)
		for i in range(self.raster.nx):
			for j in range(self.raster.ny):
				Len=len(self.raster.data["stops"][i,j])
				if Len>0:
					raster_data[i,j]=len(np.unique(self.raster.data["stops"][i,j],axis=0))
	
	def plot(self):
		import platrock.GUI.Plot3D
		self.plot=platrock.GUI.Plot3D
