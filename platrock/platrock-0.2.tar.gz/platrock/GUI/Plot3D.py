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

import numpy as np
import matplotlib as mpl
import platrock
from descartes import PolygonPatch
import plotly.offline as plyo
import plotly.graph_objs as plygo
import platrock.Common.ColorPalettes as cp

import matplotlib as mpl
if platrock.web_ui:
	mpl.use('Agg')
	#import plotly as ply
import matplotlib.pyplot as plt
if not platrock.web_ui: plt.ion()

mpl.rcParams["figure.subplot.bottom"]=0.05
mpl.rcParams["figure.subplot.top"]=0.95
mpl.rcParams["figure.subplot.left"]=0.0
mpl.rcParams["figure.subplot.right"]=0.92

fig=plt.figure("PlatRock Raster View",facecolor="w",edgecolor="w")
ax=plt.axes()

def clear():
	global fig,ax
	plt.close("all")
	fig=plt.figure("PlatRock Raster View",facecolor="w",edgecolor="w")
	ax=plt.axes()


def draw_terrain(s, with_polygons=False):
	terrain=s.terrain
	
	#1- background raster:
	azimuth=315
	angle_altitude=45
	x, y = np.gradient(terrain.Z_raster.data["Z"].transpose())
	X,Y=np.meshgrid(terrain.Z_raster.X, terrain.Z_raster.Y)
	slope = np.pi/2. - np.arctan(np.sqrt(x*x + y*y))
	aspect = np.arctan2(-x, y)
	azimuthrad = azimuth*np.pi / 180.
	altituderad = angle_altitude*np.pi / 180.
	shaded = np.sin(altituderad) * np.sin(slope)\
	+ np.cos(altituderad) * np.cos(slope)\
	* np.cos(azimuthrad - aspect)
	plt.pcolormesh(X,Y,255*(shaded + 1)/2,cmap='Greys',rasterized=True)
	
	if(with_polygons):
		#4- terrain polygons
		for soil_param_set in terrain.soil_params:
			ax.add_patch(PolygonPatch(soil_param_set["shapely_polygon"],facecolor=np.append(soil_param_set["color"]/255,0.65),edgecolor=soil_param_set["color"][0:3]/255,linewidth=1.5))
		
		#3- rocks start positions:
		for start_param_set in s.rocks_start_params:
			ax.add_patch(PolygonPatch(start_param_set["shapely_polygon"],facecolor=np.append(start_param_set["color"]/255,0.65),edgecolor="black",linewidth=1))
	
	fig.set_size_inches(3+1,3*terrain.Z_raster.data["Z"].shape[1]/terrain.Z_raster.data["Z"].shape[0])
	ax.set_aspect("equal")
	fig.canvas.draw()
	

def draw_forest(terrain):
	ax.plot(terrain.trees_as_array[:,0],terrain.trees_as_array[:,1],"o",color="green")
	fig.canvas.draw()
	
def draw_rocks_count(raster):
	data=raster.data['crossings']
	#use masked array to set a "bad" value to the cmap. It allows to set the cmap to fully transparent when crossings==0
	masked_array = np.ma.array (data, mask=(data==0))
	cmap = mpl.cm.jet
	cmap.set_bad('gray',0.)	#gray color but opacity=0
	x,y=np.meshgrid(raster.X, raster.Y,indexing="ij")
	cm=ax.pcolormesh(x,y,masked_array,cmap=cmap,edgecolor=[0.6,0.6,0.8],linewidth=0.01,zorder=1)
	ax.set_title("Nombre de passages")
	cbar=plt.colorbar(cm,aspect=30)
	cbar.set_label("# passages")
	ax.set_aspect("equal")
	fig.canvas.draw()

def draw_mean_vel(raster):
	data=raster.data_to_mean('vels')
	#use masked array to set a "bad" value to the cmap. It allows to set the cmap to fully transparent when vel==0
	masked_array = np.ma.array (data, mask=(data==0))
	cmap = mpl.cm.jet
	cmap.set_bad('gray',0.)	#gray color but opacity=0
	x,y=np.meshgrid(raster.X, raster.Y,indexing="ij")
	cm=ax.pcolormesh(x,y,masked_array,cmap=cmap,edgecolor=[0.6,0.6,0.8],linewidth=0.01,zorder=1)
	ax.set_title("Vitesses moyennes")
	cbar=plt.colorbar(cm,aspect=30)
	cbar.set_label("$[m.s^{-1}]$")
	ax.set_aspect("equal")
	fig.canvas.draw()

def draw_mean_Ec(raster):
	data=raster.data_to_mean('Ec')/1000.
	#use masked array to set a "bad" value to the cmap. It allows to set the cmap to fully transparent when vel==0
	masked_array = np.ma.array (data, mask=(data==0))
	cmap = mpl.cm.jet
	cmap.set_bad('gray',0.)	#gray color but opacity=0
	x,y=np.meshgrid(raster.X, raster.Y,indexing="ij")
	cm=ax.pcolormesh(x,y,masked_array,cmap=cmap,edgecolor=[0.6,0.6,0.8],linewidth=0.01,zorder=1)
	ax.set_title("Énergie cinétique moyenne")
	cbar=plt.colorbar(cm,aspect=30)
	cbar.set_label("$[kJ]$")
	ax.set_aspect("equal")
	fig.canvas.draw()

def draw_number_of_source_cells(raster):
	data=raster.data['number_of_source-cells']
	#use masked array to set a "bad" value to the cmap. It allows to set the cmap to fully transparent when vel==0
	masked_array = np.ma.array (data, mask=(data==0))
	cmap = mpl.cm.jet
	cmap.set_bad('gray',0.)	#gray color but opacity=0
	x,y=np.meshgrid(raster.X, raster.Y,indexing="ij")
	cm=ax.pcolormesh(x,y,masked_array,cmap=cmap,edgecolor=[0.6,0.6,0.8],linewidth=0.01,zorder=1)
	ax.set_title("Nombre de cellules source")
	cbar=plt.colorbar(cm,aspect=30)
	cbar.set_label("$Number$")
	ax.set_aspect("equal")
	fig.canvas.draw()

def draw_rocks_trajectories(s,rocks_ids):
	for rock_nb in rocks_ids:
		draw_rock_trajectory(s,rock_nb,draw=False)
	fig.canvas.draw()
			
def draw_rock_trajectory(s,nb,draw=True):
	pos=s.output.get_contacts_pos(nb)
	ax.plot(pos[:,0],pos[:,1],'-o',ms=0.5,lw=1,zorder=99)
	if(draw):
		fig.canvas.draw()

def draw_sample_trajectories(s,nb=50):
	rocks_to_plot=[]
	if(nb>=s.nb_rocks):
		rocks_to_plot=range(s.nb_rocks)
	else:
		rocks_to_plot=np.linspace(0,s.nb_rocks-1,nb,dtype=int)
	draw_rocks_trajectories(s,rocks_to_plot)

def get_plotly_raw_html(s, sample_trajectories=False):
	#Initialize the lists
	data = []
	annotations = []
	
	x=[]
	y=[]
	z=[]
	I=[]
	J=[]
	K=[]
	s.before_run_tasks()
	for p in s.terrain.points:
		x.append(p.pos[0])
		y.append(p.pos[1])
		z.append(p.pos[2])
	for f in s.terrain.faces:
		I.append(f.points[0].id-1)
		J.append(f.points[1].id-1)
		K.append(f.points[1].id-1)
		
	triangles=plygo.Mesh3d(
		x=x,
		y=y,
		z=z,
		hoverinfo='skip'
		#facecolor="rgb(255, 0,0)",
		#i=I,
		#j=J,
		#k=K,
		#name=''
	)
	data.append(triangles)
	axis = dict(
		showbackground=True,
		backgroundcolor="rgb(230, 230,230)",
		gridcolor="rgb(255, 255, 255)",
		zerolinecolor="rgb(255, 255, 255)",
    )
	#4- Configure layout (axes, etc...):
	layout = plygo.Layout(
		autosize=False,
		width=1000,
		height=800,
		margin=plygo.layout.Margin(
			l=40,
			r=10,
			b=20,
			t=30,
			pad=4
		),
		scene=dict(
			xaxis=dict(axis),
			yaxis=dict(axis),
			zaxis=dict(axis),
			#aspectratio=dict(
				#x=1,
				#y=1,
				#z=0.5
			#)
		),
		showlegend= False,
		#hovermode = 'closest',
		#annotations=annotations,
	)
	
	#5- configure plotly menubar:
	config = dict(
		modeBarButtonsToRemove = ["autoScale2d","toggleSpikelines","hoverCompareCartesian","hoverClosestCartesian","select2d","lasso2d"],
		displaylogo = False,
		displayModeBar = True,
	)
	
	#6- Generate plotly html/js:
	ply_fig = plygo.Figure(data=data, layout=layout)
	return plyo.plot(ply_fig, config=config, show_link=False, output_type="div", include_plotlyjs=False)




