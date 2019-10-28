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

import platrock
import numpy as np
import platrock.TwoD.Geoms as Geoms
import platrock.Common.Math as Math
import matplotlib as mpl
import plotly.offline as plyo
import plotly.graph_objs as plygo
import platrock.Common.ColorPalettes as cp
import platrock.Common.Outputs as Out

if platrock.web_ui:
	mpl.use('Agg')
	#import plotly as ply
import matplotlib.pyplot as plt
if not platrock.web_ui: plt.ion()

mpl.rcParams["figure.subplot.bottom"]=0.04
mpl.rcParams["figure.subplot.top"]=0.99
mpl.rcParams["figure.subplot.left"]=0.03
mpl.rcParams["figure.subplot.right"]=0.99

fig=plt.figure("PlatRock 2D View",facecolor="w",edgecolor="w")
ax=plt.axes()

def clear():
	global fig,ax
	plt.close("all")
	fig=plt.figure("PlatRock 2D View",facecolor="w",edgecolor="w")
	ax=plt.axes()

def draw_terrain(t):
	seg_points=t.get_points()
	delta_z=max(seg_points[:,1])-min(seg_points[:,1])
	delta_x=max(seg_points[:,0])-min(seg_points[:,0])
	fig.set_size_inches( (18,int(18*1.8*delta_z/delta_x)), forward=True)
	ax.set_ylim(np.min(seg_points[:,1])-0.1*delta_z,np.max(seg_points[:,1])+0.1*delta_z)
	ax.set_xlim(np.min(seg_points[:,0])-0.01*delta_x,np.max(seg_points[:,0])+0.01*delta_x)
	ax.set_aspect("equal")
	ax.fill_between(seg_points[:,0],seg_points[:,1],color="#844200")
	fig.canvas.draw()

def plot_trajectory(s,rock_id,nb_points=10, draw=True, with_contacts=False, use_plotly=False):
	color=s.random_generator.rand(3)
	X=np.array([],dtype=float)
	Y=np.array([],dtype=float)
	pos=s.output.get_contacts_pos(rock_id)
	vels=s.output.get_contacts_vels(rock_id)
	types=s.output.get_contacts_types(rock_id)
	trees_x=[]
	trees_y=[]
	for i in range(len(pos)-1):
		if(types[i] in [Out.START,Out.SOIL,Out.TREE]): #parabola
			x=np.linspace(pos[i][0],pos[i+1][0],nb_points)
			X=np.append(X,x)
			P=Geoms.Parabola(pos=Math.Vector2(pos[i]),vel=Math.Vector2(vels[i]),g=s.gravity)
			Y=np.append(Y,P.A*x*x+P.B*x+P.C)
		elif(types[i]==Out.MOTION):
			X=np.append(X,[pos[i][0]])
			Y=np.append(Y,[pos[i][1]])
		elif(types[i]==Out.ROLL):
			x=[pos[i][0],pos[i+1][0]]
			X=np.append(X,x)
			y=[pos[i][1],pos[i+1][1]]
			Y=np.append(Y,y)
		if(types[i]==Out.TREE or types[i]==Out.ROLL_TREE):
			trees_x.append(pos[i][0])
			trees_y.append(pos[i][1])
	if(use_plotly):
		return X,Y,np.asarray(trees_x),np.asarray(trees_y)
	ax.plot(X,Y,alpha=0.5,lw=2,color=color)
	if(with_contacts):
		normals=s.output.get_contacts_normals(rock_id)
		types=s.output.get_contacts_types(rock_id)
		for i in range(len(normals)):
			if(types[i] in [Out.START,Out.SOIL]):
				vect=Math.Vector2(normals[i]).rotated(-np.pi/2.)
				ax.plot([pos[i][0]-vect[0],pos[i][0]+vect[0]], [pos[i][1]-vect[1],pos[i][1]+vect[1]],"--",color=color)
			elif(types[i] == Out.TREE or types[i]==Out.ROLL_TREE):
				ax.plot(pos[i][0],pos[i][1],"^",ms=7,color=color)
	if(draw):
		fig.canvas.draw()

def plot_trajectories(s,rocks_ids, with_contacts=False):
	for i in rocks_ids:
		plot_trajectory(s,i,draw=False,with_contacts=with_contacts)
	fig.canvas.draw()

def plot_sample_trajectories(s,nb=10, with_contacts=False, use_plotly=False):
	rocks_to_plot=[]
	if(nb>=s.nb_rocks):
		rocks_to_plot=range(s.nb_rocks)
	else:
		rocks_to_plot=np.linspace(0,s.nb_rocks-1,nb,dtype=int)
	if not use_plotly:
		plot_trajectories(s,rocks_to_plot,with_contacts=with_contacts)
	else:
		#this will create [ [X_r1,Y_r1], [X_r2,Y_r2] ...]
		return [ plot_trajectory(s,i,use_plotly=True) for i in rocks_to_plot ]

def plot_checkpoints(s):
	for chkP in s.checkpoints:
		ax.axvline(chkP.x,lw=4,alpha=0.2,color="red")
		#if(hasattr(chkP,"heights")):
			##for i in range(len(chkP.heights)):
				#ax.arrow(chkP.x,chkP.heights[i]+chkP.base_height,chkP.vels[i][0],chkP.vels[i][1],head_width=2,head_length=2)
	fig.canvas.draw()

def get_plotly_raw_html(s, sample_trajectories=False):
	#Initialize the lists
	data = []
	annotations = []
	#1- plot the terrain:
	seg_points = s.terrain.get_points()
	terrain_dx=seg_points[:,0].max()-seg_points[:,0].min()
	terrain_dy=seg_points[:,1].max()-seg_points[:,1].min()
	bbox=[	#bounding box: [ minx, maxx, miny, maxy ]
		seg_points[:,0].min()-0.05*terrain_dx,
		seg_points[:,0].max()+0.05*terrain_dx,
		seg_points[:,1].min()-0.05*terrain_dy,
		seg_points[:,1].max()+0.05*terrain_dy,
	]
	
	i=0
	zones_polygon_centers=[]
	zones_polygon_colors=[]
	for zone in s.terrain.params_zones:
		zone_pts=seg_points[zone.start_id:zone.end_id+2,:]
		zones_polygon_centers.append(Math.get_2D_polygon_center_of_mass(np.append(zone_pts,[[zone_pts[-1,0],bbox[2]],[zone_pts[0,0],bbox[2]]],axis=0)))
		zones_polygon_colors.append(cp.color_to_html(zone["color"]))
		zero_line = plygo.Scatter(
			x=[zone_pts[0,0],zone_pts[-1,0]],
			y=[bbox[2]]*2,
			fill='none',
			line=dict(
					color="rgba(255,255,255,0)",
					width=0
			),
			hoverinfo='skip',
			mode="lines",
			name='zones'
		)
		terrain = plygo.Scatter(
			x=zone_pts[:,0],
			y=zone_pts[:,1],
			fill='tonexty',
			text="Point",
			line=dict(
				color=zones_polygon_colors[-1],
				width=3
			),
			name='terrain',
			hoverinfo='text+x+y',
		)
		data.append(zero_line)
		data.append(terrain)
		i+=1
		
	#1.1- plot markers at zones centers to handle hoverinfo/clicks events
	zones_polygon_centers=np.asarray(zones_polygon_centers)
	data.append(plygo.Scatter(
		x=zones_polygon_centers[:,0],
		y=zones_polygon_centers[:,1],
		text = ["Zone "+str(i) for i in range(len(zones_polygon_centers))],
		mode = 'markers',
		marker = dict(
			symbol = 'circle',
			size = 15,
			color = zones_polygon_colors,
		),
		hoverinfo='text',
		name="zones"
	))
	
	#2- plot the checkpoints:
	for chkP in s.checkpoints:
		data.append(
			plygo.Scatter(
				x=[chkP.x]*2,
				y=[s.terrain.get_y(chkP.x), 1e20],
				mode = 'lines',
				line=dict(
					color="rgba(255,0,0,0.5)",
					width=4
				),
				hoverinfo='skip', #dont show datapoints on mouse over
				name='',
			)
		)
		if(sample_trajectories and len(chkP.heights)>0):
			annotations.append(
				dict(
					x=chkP.x,
					y=1,
					xref="x",
					yref="paper",
					text=str(round(chkP.crossings_ratio*100,1))+"%",
					showarrow=False,
					textangle=-90,
					bordercolor="rgba(255,0,0,0.5)",
					borderwidth=4,
					borderpad=1,
					bgcolor="rgba(255,255,255,1)",
					hovertext="Mean height: "+str(round((np.asarray(chkP.heights).mean()),2))+"<br>Mean vel: "+str(round((np.linalg.norm(np.asarray(chkP.vels),axis=1).mean()),2))
			)
		)
	
	#3- plot sample trajectories:
	if(sample_trajectories):
		rocks_data = plot_sample_trajectories(s,nb=sample_trajectories, use_plotly=True)
		for rock_data in rocks_data:
			color=s.random_generator.randint(255,size=3)
			color="rgb("+",".join(color.astype(str))+")"
			#parabolas:
			data.append(
				plygo.Scatter(
					x=rock_data[0],
					y=rock_data[1],
					mode = 'lines',
					line=dict(
						color=color,
						width=1
					),
					hoverinfo='skip', #dont show datapoints on mouse over
					name='',
				)
			)
			#trees:
			data.append(
				plygo.Scatter(
					x=rock_data[2],
					y=rock_data[3],
					mode = 'markers',
					marker = dict(
						symbol = 'triangle-up',
						size = 6,
						#line = dict(width=2),
						color = color,
						opacity = 1
					),
					hoverinfo='skip', #dont show datapoints on mouse over
					name='',
				)
			)
		cdf=s.get_stops_cdf()
		data+=[
			plygo.Scatter(
				x=[seg_points[0,0],seg_points[-1,0]],
				y=[bbox[2]]*2,
				fill='none',
				line=dict(
						color="rgba(255,255,255,0)",
						width=0
				),
				hoverinfo='skip',
			),
			plygo.Scatter(
				x=cdf[0,:],
				y=cdf[1,:]*(s.terrain.get_y_range()[1]-bbox[2])+bbox[2],
				fill='tonexty',
				text=["CDF = "+str(value) for value in cdf[1,:]],
				name="CDF",
				hoverinfo='text',
				mode = 'lines',
				line=dict(
					color="rgba(0,0,0,0.7)",
					width=2,
					shape='hv',
				),
				fillcolor="rgba(0,0,0,0.15)",
			)
		]
	
	#4- Configure layout (axes, etc...):
	xrange=bbox[:2]
	yrange=bbox[2:]
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
		xaxis = dict(
			#nticks = 10,
			linecolor= 'black',
			mirror=True,
			showgrid=True,
			range = xrange,
			zeroline=False,
		),
		yaxis = dict(
			linecolor= 'black',
			mirror=True,
			showgrid=True,
			zeroline=False,
			scaleanchor = "x", #to make 1:1 scale
			range = yrange,
		),
		showlegend= False,
		hovermode = 'closest',
		annotations=annotations,
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

def get_plotly_rock_raw_html(s,r):
	data = []
	
	data.append(
		plygo.Scatter(
			x=[0],
			y=[0],
			text="COG",
			hoverinfo="text",
			marker = dict(
				symbol = 'circle',
				size = 10,
				color = "black"
			),
		)
	)
	
	points=np.copy(r.vertices)
	if not s.random_rocks_ori:
		Math.rotate_points_around_origin(points,np.radians(s.rocks_ori))
	vertices = plygo.Scatter(
		x=points[:,0].tolist()+[points[0,0]],
		y=points[:,1].tolist()+[points[0,1]],
		hoverinfo="x+y",
		line=dict(
			color="rgb(102, 102, 102)",
			width=3
		),
	)
	data.append(vertices)
	shapes=[
		plygo.layout.Shape(
				type="path",
				path='M'+"L".join([','.join(i) for i in points.astype(str)])+'Z',
				fillcolor='rgba(102, 102, 102, 0.62)',
				line=dict(
					#color=zones_polygon_colors[-1],
					width=0
				),
		)
	]

	layout = plygo.Layout(
		width=400,
		height=400,
		margin=plygo.layout.Margin(
			l=40,
			r=10,
			b=20,
			t=30,
			pad=4
		),
		xaxis = dict(
			mirror=True,
			showgrid=True,
			linecolor="black",
			linewidth=1,
		),
		yaxis = dict(
			mirror=True,
			showgrid=True,
			scaleanchor = "x", #to make 1:1 scale
			linecolor="black",
			linewidth=1,
		),
		showlegend= False,
		hovermode = 'closest',
		shapes=shapes,
	)

	config = dict(
		displayModeBar= False,
		responsive= True,
	)
	
	ply_fig = plygo.Figure(data=data, layout=layout)
	return plyo.plot(ply_fig, config=config, show_link=False, output_type="div", include_plotlyjs=False)











