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
This module is used by the ThreeD model. It handles all the Objects types
"""

import numpy as np
import platrock.Common.Debug as Debug
import platrock
import quaternion
import platrock.Common.Math as Math
import copy,sys
from . import RasterTools
import osgeo.gdal as gdal
import shapely.geometry
import shapely.affinity
import platrock.Common.ColorPalettes as cp

class Point(object):
	"""
	A point, which is composing the terrain faces vertex or the rock vertex.
	
	Args:
		id (int): a unique identifier used for the 3D view
		pos (:class:`Common.Math.Vector3` [float,float,float]): absolute x,y,z position components
		vel (:class:`Common.Math.Vector3` [float,float,float]): absolute vx,vy,vz velocity components
		relPos (:class:`Common.Math.Vector3` [float,float,float]): if the point is member of a :class:`Triangulated_Object`, the refPos is the position of the point in the object coordinates (centered at COG).
		VTK_actor (:class:`vtk.VtkActor`): for 3D view
		color (list [1.,0.,0.]): the color of the object for raster or 3D views
		radius (float): the point radius, if any
		TO (:class:`Triangulated_Object`): the triangulated_object the point is member of
		faces (list [:class:`Face`]): the list of all faces the point is member of
	"""
	def __init__(self,x=0,y=0,z=0,TO=None):
		"""
		Constructor:
		
		Args:
			x(float): the x in pos
			y(float): the y in pos
			z(float): the z in pos
		"""
		Triangulated_Object.points_counter+=1
		self.id=Triangulated_Object.points_counter
		self.pos=Math.Vector3([x,y,z])
		self.vel=Math.Vector3([0.,0.,0.])
		self.relPos=Math.Vector3([x,y,z])
		self.VTK_actor=None
		self.color=[1.,0.,0.]
		self.radius=0.1
		self.TO=TO
	
	def update_pos(self):
		"""
		Update the position of the point according to its TO attibute.
		"""
		self.pos=quaternion.rotate_vector(self.TO.ori,self.relPos)
		self.pos+=self.TO.pos

class Face(object):
	"""
	A face, composing a rock or the terrain.
	
	Args:
		id (int): a unique identifier used for the 3D view
		points (:class:`numpy.ndarray` [:class:`Point`,:class:`Point`,:class:`Point`]): an array of 3 points linked by the face
		normal (:class:`Common.Math.Vector3` [float, float, float]): the normal vector of the face
		color (list [1.,0.,0.]): the color of the object for raster or 3D views
		VTK_actor (:class:`vtk.VtkActor`): for 3D view
		TO (:class:`Triangulated_Object`): the triangulated_object the face is member of
		roughness (float): the roughness of the terrain for this face
	"""
	def __init__(self,point1,point2,point3,bounce_model_number=None,R_t=None,R_n=None,roughness=None,v_half=None,phi=None,TO=None,**kwargs):	#allow **kwargs here as e and mu (siconos) parameters will be given but not used here
		"""
		Args:
			point1 (:class:`Point`): the first point the face is connected to
			point2 (:class:`Point`): the second point the face is connected to
			point3 (:class:`Point`): the third point the face is connected to
		FIXME : DOC
		"""
		#Triangulated_Object.faces_counter+=1
		#self.id=Triangulated_Object.faces_counter
		self.points=[point1,point2,point3]
		self.normal=None
		self.cog=None
		self.color=[0.68235294, 0.5372549 , 0.39215686]
		self.VTK_actor=None
		self.TO=TO
		self.xyz_bb=None
		#used only if the face belongs to the terrain:
		self.roughness=roughness
		self.R_n=R_n
		self.R_t=R_t
		self.bounce_model_number=bounce_model_number
		self.v_half=v_half
		self.phi=phi
		self.xyz_bb=np.array([	min(self.points[0].pos[0],self.points[1].pos[0],self.points[2].pos[0]),
								max(self.points[0].pos[0],self.points[1].pos[0],self.points[2].pos[0]),
								min(self.points[0].pos[1],self.points[1].pos[1],self.points[2].pos[1]),
								max(self.points[0].pos[1],self.points[1].pos[1],self.points[2].pos[1]),
								min(self.points[0].pos[2],self.points[1].pos[2],self.points[2].pos[2]),
								max(self.points[0].pos[2],self.points[1].pos[2],self.points[2].pos[2])])
	
	def is_point_inside_2D(self,point):
		"""
		From an arbitrary point
		"""
		point_xy=point.pos[0:2]	#
		face_points_xy=[p.pos[0:2] for p in self.points ]
		cross_products=[Math.cross2(face_points_xy[i-2]-face_points_xy[i],point_xy-face_points_xy[i]) for i in range(0,3)]
		cross_products_signs_sum=sum(np.sign(cross_products))
		return abs(cross_products_signs_sum)==3
	
	def is_point_inside_3D(self,point):
		"""
		This method is not used anymore. Better do this on 2D ("view from the sky") as it avoids convex edge issues (non detection by the contacts_detector).
		"""
		point_on_face=point.pos - (point.pos-self.points[0].pos).dot(self.normal)*self.normal
		cp1=((self.points[-2].pos-self.points[0].pos).cross(point_on_face-self.points[0].pos)).dot(self.normal)
		cp2=((self.points[-1].pos-self.points[1].pos).cross(point_on_face-self.points[1].pos)).dot(self.normal)
		cp3=((self.points[0].pos-self.points[2].pos).cross(point_on_face-self.points[2].pos)).dot(self.normal)
		#cross_products=[(self.points[i-2].pos-self.points[i].pos).cross(point_on_face-self.points[i].pos) for i in range(0,3)]
		#dots=[cp.dot(self.normal) for cp in cross_products]
		cross_products_signs_sum=np.sign(cp1)+np.sign(cp2)+np.sign(cp3)
		return abs(cross_products_signs_sum)==3
		
			

# /!\ ALL TRIANGULATED OBJECTS MUST INHERIT FROM THIS CLASS !
class Triangulated_Object(object):
	def __init__(self):
		self.points=np.array([])
		self.faces=np.array([])
		self.VTK_actor=None	#VTK actor for visualization
		self.opacity=1
		self.enable_points_view=False	
		self.points_as_array=np.array([])
	
	def set_points_as_array(self):
		self.points_as_array=np.asarray([p.relPos for p in self.points])
	points_counter=0


class Rock(Triangulated_Object):
	"""A falling rock."""
	def __init__(self,pos=[0.,0.,0.],vel=[0.,0.,0.],angVel=[0.,0.,0.],density=2700.):
		Triangulated_Object.__init__(self)
		self.pos = Math.Vector3(pos)
		self.ori=quaternion.from_euler_angles(0,0,0)
		self.vel=Math.Vector3(vel)
		self.volume=None
		self.mass=None
		self.I=None
		self.angVel=Math.Vector3(angVel)
		self.density=density
		self.is_stopped=False
		self.color=np.random.rand(3).tolist()
		self.contacts=[]
		self.force=Math.Vector3([0.,0.,0.])
		self.torque=Math.Vector3([0.,0.,0.])
		self.angMom=Math.Vector3([0.,0.,0.])
		self.verlet_faces_list=[]
		self.verlet_trees_list=[]
		self.terrain_active_contact=None
		self.tree_active_contact=None
		self.out_of_bounds=False
		
	def init_mass_inertia(self):
		self.volume=0.
		points=np.asarray([p.pos for p in self.points])
		point_inside=np.mean(points,axis=0)
		G=Math.Vector3()
		for f in self.faces:
			A,B,C=f.points[0].pos,f.points[1].pos,f.points[2].pos
			face_surface = ((B-A).cross(C-A)).norm()/2.
			face_normal = ((A-B).cross(C-B)).normalized()
			if(face_normal.dot(point_inside-A)>0.):
				face_normal*=-1.
			tetrahedron_volume=np.abs(face_surface*face_normal.dot(point_inside-A)/3.)
			tetrahedron_G=(A+B+C+point_inside)/4.
			G+=tetrahedron_volume*tetrahedron_G
			self.volume+=tetrahedron_volume
			
		self.mass=self.density*self.volume
		self.radius=(3.*self.volume/4./np.pi)**(1./3.)
		G/=self.volume
		for p in self.points:
			p.relPos-=G			
		self.I=2./5.*self.mass*self.radius**2
		self.I=Math.Vector3([self.I,self.I,self.I])
		self.update_members_pos()
	
	def update_members_pos(self):
		for p in self.points:
			p.update_pos()


class Sphere(Rock):
	"""
	FIXME: DOC
	"""
	def __init__(self,volume=1,**kwargs):
		super(Sphere,self).__init__(**kwargs)
		self.volume=volume
		self.radius=(self.volume*3/4/np.pi)**(1/3)
		self.points=np.array([Point(self.pos[0],self.pos[1],self.pos[2],TO=self)])	#a sphere has a single point at the center
		self.points[0].pos=self.pos #this is a "pointer", all updates to self.pos will update self.points[0]
		self.points[0].radius=self.radius #this will only be used for visualization
		self.enable_points_view=False
		self.bounding_box=Bounding_Box()
		self.init_mass_inertia()
		
	def init_mass_inertia(self):
		self.mass=self.density*self.volume
		self.I=np.ones(3)*2./5.*self.mass*self.radius**2
	def update_members_pos(self):
		pass
		

class Parallelepiped(Rock):
	def __init__(self,lengths=[1,1,1],**kwargs):
		self.lengths=Math.Vector3(lengths)
		super(Parallelepiped,self).__init__(**kwargs)
		for x in [-lengths[0]/2.,+lengths[0]/2.]:
			for y in [-lengths[1]/2.,+lengths[1]/2.]:
				for z in [-lengths[2]/2.,+lengths[2]/2.]:
					self.points=np.append(self.points,Point(x,y,z,TO=self) )
		self.faces=[
			Face( self.points[0], self.points[1], self.points[2], TO=self ),
			Face( self.points[1], self.points[2], self.points[3], TO=self ),
			Face( self.points[0], self.points[1], self.points[5], TO=self ),
			Face( self.points[0], self.points[4], self.points[5], TO=self ),
			Face( self.points[1], self.points[5], self.points[7], TO=self ),
			Face( self.points[1], self.points[3], self.points[7], TO=self ),
			Face( self.points[2], self.points[3], self.points[6], TO=self ),
			Face( self.points[3], self.points[6], self.points[7], TO=self ),
			Face( self.points[0], self.points[2], self.points[4], TO=self ),
			Face( self.points[2], self.points[4], self.points[6], TO=self ),
			Face( self.points[4], self.points[5], self.points[6], TO=self ),
			Face( self.points[5], self.points[6], self.points[7], TO=self ),
		]
		self.init_mass_inertia()
		self.set_points_as_array()
	
	def get_siconos_convex_hull(self):
		assert(len(self.points)>3)
		from siconos.mechanics.collision import SiconosConvexHull, SiconosBox
		#hull = SiconosConvexHull(self.points_as_array)
		hull = SiconosBox(self.lengths)
		dims = [self.points_as_array[:,0].max() - self.points_as_array[:,0].min(),
				self.points_as_array[:,1].max() - self.points_as_array[:,1].min(),
				self.points_as_array[:,2].max() - self.points_as_array[:,2].min()]
		hull.setInsideMargin(min(dims)*0.02)
		hull.setOutsideMargin(0)
		return hull

from . import ThreeDEnginesToolbox
class Terrain(Triangulated_Object):
	valid_input_shapefile_attrs=np.array([	["R_n",					"R<sub>n</sub>",		float,	0,	0.95	],
											["R_t",					"R<sub>t</sub>",		float,	0,	0.95	],
											["roughness",			"Roughness",			float,	0,	1.		],
											["bounce_model_number",	"Rebound model",		int,	0,	2		],
											["phi",					"φ",					float,	0,	40		],
											["v_half",				"V<sub>1/2</sub>",		float,	0,	50		],
											["mu",					"μ",					float,	0,	0.95	],
											["e",					"e",					float,	0,	0.95	]])
	def __init__(self,DEM_asc=None,params_shapefile=None,default_faces_params={"R_n":0.6, "R_t":0.6, "roughness":0.1,"bounce_model_number":0,"phi":30,"v_half":2.5,"mu":0.8,"e":0.1}):
		Triangulated_Object.__init__(self)
		self.enable_points_view=False
		self.color=[0.68235294, 0.5372549 , 0.39215686]
		self.trees=[]
		self.trees_as_array=None
		self.vertical_surface=0.
		self.Z_raster=None
		self.opacity=1
		self.faces_xyz_bb=None
		self.soil_params=[]
		self.default_faces_params=default_faces_params
		if(DEM_asc is not None):
			if(platrock.web_ui):	#don't populate/precompute here, do it in s.before_run_tasks()
				self.set_Z_raster_from_DEM_file(DEM_asc)
			else:
				self.from_DEM_file(DEM_asc)
		if(params_shapefile is not None): #NOTE: the function below needs the Z_raster to be set, as it needs the xllcorner/yllcorner data
			self.set_soil_params_from_shapefile(params_shapefile)

	def from_DEM_file(self,filename):
		self.set_Z_raster_from_DEM_file(filename)
		self.populate_from_Z_raster()
		self.precompute_datas()
	
	def precompute_datas(self):
		self.set_faces_normals_and_cogs()
		self.set_points_as_array()
		self.set_faces_xyz_bbs()
		self.min_height=self.points_as_array[:,2].min()
		
	def set_Z_raster_from_DEM_file(self,filename):
		try:
			self.Z_raster=RasterTools.from_asc(filename,"Z")
		except Exception as e:
			Debug.error("Failed to import the Esri grid file:",str(e))
	
	def set_soil_params_from_shapefile(self,params_shapefile):
		try:
			shp_file=gdal.OpenEx(params_shapefile)
			layer0=shp_file.GetLayer(0)
			self.soil_params=[]
			for i in range(layer0.GetFeatureCount()):
				self.soil_params.append({})
				feat=layer0.GetFeature(i).ExportToJson(as_object=True)
				shapely_poly = shapely.geometry.shape(feat['geometry'])
				shapely_poly = shapely.affinity.translate(shapely_poly,xoff=-self.Z_raster.xllcorner,yoff=-self.Z_raster.yllcorner)
				self.soil_params[i]["shapely_polygon"]=shapely_poly
				if(isinstance(shapely_poly,shapely.geometry.MultiPolygon)): #we will have to choose later from the sub-polys, but ponderate by the poly areas. Build the area cumulative sum once here
					areas=np.asarray([p.area for p in list(shapely_poly)])	#areas of the polygons
					self.soil_params[i]["multipoly_normalized_area_cumsum"]=np.cumsum(areas/sum(areas))
				self.soil_params[i]["color"]=cp.qualitative10[i]
				soil_params = feat['properties']
				#shapefile properties names has limited char count, so replace :
				if("bounce_mod" in list(soil_params.keys())):
					soil_params["bounce_model_number"] = soil_params.pop("bounce_mod")
				#validate the parameters from the input shapefile
				for k in list(soil_params.keys()):
					if(k not in Terrain.valid_input_shapefile_attrs[:,0]):
						soil_params.pop(k)
				self.soil_params[i]["params"]=soil_params
		except Exception as e:
			Debug.error("Failed to import the shapefile:",str(e))
			raise
		
	def set_faces_params_from_shapefile(self):
		#loop on faces to set attrbutes
		for face in self.faces:	#FIXME: this loop can be slow, optimize by replacing shapely "contains" by a cython or numpy array algo ?
			shapely_point=shapely.geometry.Point(face.cog[0:2])
			for soil_param in self.soil_params:
					if(soil_param["shapely_polygon"].contains(shapely_point)):
						face.__dict__.update(soil_param["params"])	#update will overwrite params
						break
	
	def populate_from_Z_raster(self):
			points_ids=np.ones([self.Z_raster.nx,self.Z_raster.ny])*-1 #this is a map of points ids, useful to link [x,y] cells to corresponding point ids.
			#CREATE POINTS :
			nb_points=np.count_nonzero(self.Z_raster.data["Z"]!=self.Z_raster.header_data["NODATA_value"])
			self.points=np.empty(nb_points,dtype=Point)	#to avoid increasing the size of the points array at each new point, instanciate here with the right size.
			counter=0
			for i in range(0,self.Z_raster.nx):
				for j in range(0,self.Z_raster.ny):
					if(not self.Z_raster.data["Z"][i,j]==self.Z_raster.header_data["NODATA_value"]):
						self.points[counter]=Point(self.Z_raster.X[i],self.Z_raster.Y[j],self.Z_raster.data["Z"][i,j])
						points_ids[i,j]=counter
						counter+=1
			# CREATE TRIANGLES :
			# id0---id1
			#  |   / |
			#  |  /  |
			#  | /   |
			# id2---id3
			#to avoid increasing the size of the faces array at each new face, instanciate here.
			#We don't know the exact size now, so use 2*nb_points wich is the worst-case, then finally decrease the size.
			self.faces=np.empty(2*nb_points,dtype=Face)
			counter=0
			for i in range(0,len(self.Z_raster.X)-1):
				for j in range(0,len(self.Z_raster.Y)-1):
					id0=int(points_ids[i,j])
					if(id0!=-1):
						id1=int(points_ids[ i+1 , j   ])
						id2=int(points_ids[ i   , j+1 ])
						id3=int(points_ids[ i+1 , j+1 ])
						if(id1!=-1 and id2!=-1):
							self.faces[counter]=Face(self.points[id0], self.points[id1], self.points[id2],**self.default_faces_params)
							counter+=1
							if(id3!=-1):
								self.faces[counter]=Face( self.points[id1], self.points[id2], self.points[id3],**self.default_faces_params)
								counter+=1
			self.faces=self.faces[0:counter]#clean the array
	
	
	def set_faces_normals_and_cogs(self):
		ThreeDEnginesToolbox.set_faces_normals_and_cogs(self.faces)
		#for f in self.faces:
			#normal=((f.points[0].pos-f.points[1].pos).cross(f.points[2].pos-f.points[1].pos)).normalized()
			#if(normal[2]<0.):normal*=-1.
			#f.normal=normal
			#f.cog=(f.points[0].pos + f.points[1].pos + f.points[2].pos)/3
	
	def set_faces_xyz_bbs(self):
		self.faces_xyz_bb=np.asarray([f.xyz_bb for f in self.faces])
			
	def set_vertical_surface(self):
		#compute vertical surface (=surface seen from the sky) :
		self.vertical_surface=0
		for f in self.faces:
			self.vertical_surface += 0.5*np.abs(Math.cross2(f.points[1].pos[0:2]-f.points[0].pos[0:2],f.points[2].pos[0:2]-f.points[0].pos[0:2]))
			
	def generate_random_forest(self,density,dhp_mean, dhp_std):
		self.set_vertical_surface()
		nb_trees=int(density*self.vertical_surface/10000) #NOTE: density is in trees/ha, vertical_surface is in m^2
		nb_faces=len(self.faces)
		self.trees=[]
		for i in range(nb_trees):
			pick_face = self.faces[int(np.random.random()*nb_faces)]
			pt1_xy=pick_face.points[0].pos[0:2]
			pt2_xy=pick_face.points[1].pos[0:2]
			pt3_xy=pick_face.points[2].pos[0:2]
			rand_point = pt1_xy+np.random.random()*(pt2_xy-pt1_xy) # pick a point somewhere between pt1 and pt2
			rand_point = rand_point + np.random.random()*(pt3_xy-rand_point)	# move the previous picked point toward pt3
			dhp = Math.get_random_value_from_gamma_distribution(dhp_mean,dhp_std)
			self.trees.append(Tree(pos=rand_point,dhp=dhp))
	
	def get_vtk_string(self): #NOTE: deprecated
		import vtk
		points = vtk.vtkPoints()
		triangles = vtk.vtkCellArray()
		
		for p in self.points:
			points.InsertPoint(p.id,p.relPos[0],p.relPos[1],p.relPos[2])
			
		for f in self.faces:
			triangle = vtk.vtkTriangle()
			triangle.GetPointIds().SetId(0,f.points[0].id)
			triangle.GetPointIds().SetId(1,f.points[1].id)
			triangle.GetPointIds().SetId(2,f.points[2].id)
			triangles.InsertNextCell(triangle)
			
		polydata = vtk.vtkPolyData()
		polydata.SetPoints( points )
		polydata.SetPolys( triangles )
		
		writer = vtk.vtkXMLPolyDataWriter()
		writer.SetWriteToOutputString(1)
		if vtk.VTK_MAJOR_VERSION <= 5:
			writer.SetInput(polydata)
		else:
			writer.SetInputData(polydata)
		writer.Update()
		return writer.GetOutputString()
	
	def get_siconos_mesh(self):
		from siconos.mechanics.collision import SiconosMesh
		points=self.points_as_array.transpose()
		triangles=np.empty(len(self.faces)*3, dtype=np.int)
		for fi in range(len(self.faces)):
			triangles[fi*3+0]=self.faces[fi].points[0].id-1		# "-1" as id numbering starts at 1 while here it sould start at 0
			triangles[fi*3+1]=self.faces[fi].points[1].id-1
			triangles[fi*3+2]=self.faces[fi].points[2].id-1
		shape = SiconosMesh(list(triangles), points)
		dims = points.max(axis=0) - triangles.min(axis=0)
		shape.setInsideMargin(min(dims)*0.02)
		shape.setOutsideMargin(0)
		return shape
	
	def get_siconos_heightmap(self):
		from siconos.mechanics.collision import SiconosHeightMap
		z=self.Z_raster.data["Z"][:,:]
		DX=self.Z_raster.X[-1]
		DY=self.Z_raster.Y[-1]
		offsets=[DX/2,DY/2]	#because SiconosHeightmap is a rectangle heightmap centered at zero.
		return SiconosHeightMap(z,DX,DY),offsets

class Contact(object):
	def __init__(self):
		self.dist=None
		self.rock_force=None
		self.rock_torque=None
		self.rock_pos=None
		self.rock_output_vel=None
		self.rock_output_angVel=None
		self.rock_output_ori=None
	
	def get_storage_copy(self,r):
		c=copy.copy(self)
		c.rock_force=r.force.copy()
		c.rock_torque=r.torque.copy()
		c.rock_pos=r.pos.copy()
		c.rock_output_velocity=r.vel.copy()
		c.rock_output_angVel=r.angVel.copy()
		c.rock_output_ori=copy.copy(r.ori)
		return c

class Rock_terrain_contact(Contact):
	def __init__(self,point,face):
		super(Rock_terrain_contact,self).__init__()
		self.point=point	#this is the rock point, not the contact point.
		self.face=face
	
	def get_storage_copy(self, r):
		c=super(Rock_terrain_contact,self).get_storage_copy(r)
		#NOTE : the objects below are not copied, only linked
		c.point=self.point
		c.face=self.face
		return c
		

class Rock_tree_contact(Contact):
	def __init__(self,tree):
		super(Rock_tree_contact,self).__init__()
		self.tree=tree
	
	def get_storage_copy(self, r):
		c=super(Rock_tree_contact,self).get_storage_copy(r)
		c.tree_pos=self.tree.pos.copy()
		#NOTE : the object below is not copied, only linked
		c.tree=self.tree
		return c

class Tree(object):
	def __init__(self,pos,dhp=30):
		self.pos = Math.Vector2(pos) #x,y
		self.dhp = dhp
		self.active = True
		self.color = [0,0.8,0]
		self.VTK_actor=None	#VTK actor for visualization

class Bounding_Box(object):
	def __init__(self):
		self.pos=Math.Vector3([0,0,0])
		self.half_length=0	#set this to 0 so that the Verlet algorithm detect that the bounding sphere has not yet been initialized.
		self.VTK_actor=None
		self.opacity=0.25






