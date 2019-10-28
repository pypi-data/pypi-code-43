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

import numpy as np
import platrock.TwoD.Objects
from  platrock.Common.PyUtils import FriendImporter
import platrock.Common.Math as Math
from siconos.mechanics.collision import SiconosConvexHull2d

class Rock(FriendImporter):
	friendClass=platrock.TwoD.Objects.Rock
	friendImportNames=[	
		"pos",
		"vel",
		"angVel",
		"density",
		"is_stopped",
		"current_segment",
		"flying_direction",
		"color",
		"out_of_bounds",
		"update_current_segment",
		"setup_kinematics",
	]
	valid_shape_params=np.empty([0,5])
	def __init__(self, x=0., height=1., vel=[1.,0.], angVel=0., density=2800., vertices=np.array([[0.,0.],[0.,1.],[1.,0.],[1.,1.]]), ori=0, **kwargs):
		FriendImporter.__init__(self, x,height,vel,angVel,density=density)
		self.ori=ori
		self.vertices=np.asarray(vertices)
		self.set_geometrical_quantities()

	def set_geometrical_quantities(self):
		Math.sort_2d_polygon_vertices(self.vertices)
		Math.center_2d_polygon_vertices(self.vertices)
		self.mass, self.I = Math.get_2D_polygon_mass_inertia(self.vertices,self.density,cog_centered=True)
		self.volume=self.mass/self.density
		self.dims = [	self.vertices[:,0].max() - self.vertices[:,0].min(),
					self.vertices[:,1].max() - self.vertices[:,1].min()]
	
	def get_siconos_shape(self):
		siconos_shape=SiconosConvexHull2d(self.vertices)
		siconos_shape.setInsideMargin(min(self.dims)*0.02)
		siconos_shape.setOutsideMargin(0)
		return siconos_shape

class Rectangle(Rock):
	valid_shape_params=np.array([
		["Lx",		"Length (m)",		float,	0.1,		10,	1],
		["Lz",		"Width (m)",		float,	0.1,		10,	0.5],
	])
	def __init__(self,**kwargs):
		for param_name in self.valid_shape_params[:,0]:
			self.__dict__[param_name]=kwargs.pop(param_name)
		vertices=np.array([[-self.Lx/2, -self.Lz/2], [self.Lx/2, -self.Lz/2], [self.Lx/2, self.Lz/2], [-self.Lx/2, self.Lz/2]])
		super(Rectangle,self).__init__(vertices=vertices,**kwargs)

class Ellipse(Rock):
	valid_shape_params=np.array([
		["Lx",		"Length (m)",		float,	0.1,		10	,	1],
		["Lz",		"Width (m)",		float,	0.1,		10	,	0.5],
		["nbPts",	"Number of points",	int,	3,			100,	10],
	])
	def __init__(self,**kwargs):
		for param_name in self.valid_shape_params[:,0]:
			self.__dict__[param_name]=kwargs.pop(param_name)
		t=np.linspace(0,np.pi*2,self.nbPts+1)[:-1]
		vertices=np.array([self.Lx*np.cos(t) , self.Lz*np.sin(t)]).transpose()
		super(Ellipse,self).__init__(vertices=vertices,**kwargs)

class Random(Rock):
	valid_shape_params=np.array([
		["Lx",		"Length (m)",		float,	0.1,		10	,	1],
		["Lz",		"Width (m)",		float,	0.1,		10	,	0.5],
		["nbPts",	"Number of points",	int,	3,			100,	10],
	])
	def __init__(self,**kwargs):
		for param_name in self.valid_shape_params[:,0]:
			self.__dict__[param_name]=kwargs.pop(param_name)
		vertices=Math.get_random_convex_polygon(self.nbPts,self.Lx,self.Lz)
		super().__init__(vertices=vertices,**kwargs)

Contact=platrock.TwoD.Objects.Contact
ParamsDict=platrock.TwoD.Objects.ParamsDict
ParamsZone=platrock.TwoD.Objects.ParamsZone

class Segment(FriendImporter):
	friendClass=platrock.TwoD.Objects.Segment
	friendImportNames=[	
		"points",
		"set_geometrical_quantities",
		"get_y",
	]
	
	def __init__(self,start_point,end_point,e=0.5,mu=0.3,mu_r=0.5):
		FriendImporter.__init__(self,start_point,end_point)
		self.e=e
		self.mu=mu
		self.mu_r=mu_r
		self.set_geometrical_quantities()

class Terrain(platrock.TwoD.Objects.Terrain):
	valid_input_attrs=np.array([	["e",		"e",				float,	0,		1.	],
									["mu",		"μ",				float,	0,		1.	],
									["mu_r",	"μ<sub>r</sub>",	float,	0,		1.	]])
	def __init__(self,file=None):
		super(Terrain,self).__init__(file,segments_type=Segment)
		del self.rebound_models_available
	
	def check_segments_parameters_consistency(self):
		pass

























