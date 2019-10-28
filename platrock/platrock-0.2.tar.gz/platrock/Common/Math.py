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

# NOTE This file should not be used as it is replaced by Math.pyx cython module. Keep it however in case of fallback compatibility.

import numpy as np
import quaternion
from scipy.stats import gamma

def dot1(A,B):
	return A[0]*B[0]
def norm1(A):
	return np.sqrt(A[0]**2)
def normalized1(A):
		return A/norm1(A)

class Vector1(np.ndarray):	#this code derives from the numpy doc for subclassing np.ndarray.
	def __new__(subtype, input=0.0):
		assert(len(input)==1 or type(input)==type(0.0))
		obj = super(Vector1, subtype).__new__(subtype, 1, float,None,0,None,None)
		if(type(input)==type(0.0)):
			obj[0]=input
			return obj
		else:
			obj[0]=input[0]
			return obj

#Bound the methods to Vector1:
Vector1.dot=dot1
Vector1.normalized=normalized1
Vector1.norm=norm1

#NOTE: define Vector2 method outside the class so that they can be used by PlatRock without instanciating a Vector2 object. It is useful sometimes.
def cross2(A,B):
	return Vector1(A[0]*B[1]-A[1]*B[0])
def dot2(A,B):
	return A[0]*B[0]+A[1]*B[1]
def dot3(A,B):
	return A[0]*B[0]+A[1]*B[1]+A[2]*B[2]
def norm2(A):
	return np.sqrt(A[0]**2+A[1]**2)
def norm3(A):
	return np.sqrt(A[0]**2+A[1]**2+A[2]**2)
def normalized2(A):
	try:
		return A/norm2(A)
	except:
		return A*0.
def normalized3(A):
	try:
		return A/norm3(A)
	except:
		return A*0.
def rotated2(A,ang,ax=None):
	c=np.cos(ang)
	s=np.sin(ang)
	return Vector2([A[0]*c - A[1]*s , A[0]*s + A[1]*c])

class Vector2(np.ndarray):	#this code derives from the numpy doc for subclassing np.ndarray.
	def __new__(subtype, input=[0,0]):
		assert(len(input)==2)
		obj = super(Vector2, subtype).__new__(subtype, 2, float,None,0,None,None)
		obj[0]=input[0]
		obj[1]=input[1]
		return obj


#Bound the methods to Vector2:
Vector2.cross=cross2
Vector2.dot=dot2
Vector2.normalized=normalized2
Vector2.rotated=rotated2
Vector2.norm=norm2






def cross3(A,B):
	return Vector3([A[1]*B[2]-A[2]*B[1],A[2]*B[0]-A[0]*B[2],A[0]*B[1]-B[0]*A[1]])
def rotated3(A,ang,ax):
	output_xyz=Vector3()
	c=np.cos(ang)
	s=np.sin(ang)
	ax=ax.normalized()
	output_xyz[0]=A[0]*( ax[0]**2*(1.-c)+c )             +     A[1]*( ax[0]*ax[1]*(1-c)-ax[2]*s )    +     A[2]*( ax[0]*ax[1]*(1-c)+ax[1]*s )
	output_xyz[1]=A[0]*( ax[0]*ax[1]*(1-c)+ax[2]*s )     +     A[1]*( ax[1]**2*(1-c)+c )             +     A[2]*( ax[1]*ax[2]*(1-c)-ax[0]*s )
	output_xyz[2]=A[0]*( ax[0]*ax[2]*(1-c)-ax[1]*s )     +     A[1]*( ax[1]*ax[2]*(1-c)+ax[0]*s )    +     A[2]*( ax[2]**2*(1-c)+c )
	return output_xyz

class Vector3(np.ndarray):	#this code derives from the numpy doc for subclassing np.ndarray.
	def __new__(subtype, input=[0,0,0]):
		assert(len(input)==3)
		obj = super(Vector3, subtype).__new__(subtype, 3, float,None,0,None,None)
		obj[0]=input[0]
		obj[1]=input[1]
		obj[2]=input[2]
		return obj
#Bound:
Vector3.cross=cross3
Vector3.dot=dot3
Vector3.normalized=normalized3
Vector3.rotated=rotated3
Vector3.norm=norm3

import jsonpickle.handlers
import jsonpickle.ext.numpy
class VectorJsonPickeHandler(jsonpickle.ext.numpy.NumpyNDArrayHandler):
	def __init__(self, *args,**kwargs):
		super(VectorJsonPickeHandler,self).__init__(*args,**kwargs)
	def restore(self,data):
		obj=super(VectorJsonPickeHandler,self).restore(data)
		if(len(obj)==1):
			return Vector1(obj)
		elif(len(obj)==2):
			return Vector2(obj)
		elif(len(obj)==3):
			return Vector3(obj)
jsonpickle.handlers.register(Vector1, VectorJsonPickeHandler)
jsonpickle.handlers.register(Vector2, VectorJsonPickeHandler)
jsonpickle.handlers.register(Vector3, VectorJsonPickeHandler)

def rotate_vector(q,A):
	return A + 2.*cross3(q.vec,(q.w*A+cross3(q.vec,A)))/(q.w**2+q.x**2+q.y**2+q.z**2)
quaternion.rotate_vector=rotate_vector


def atan2_signed(y,x):
	if(not y==0.):
		if(x>0.):
			return np.sign(y)*np.arctan(abs(y/x))
		elif(x<0.):
			return np.sign(y)*(np.pi-np.arctan(abs(y/x)))
		else:
			return np.sign(y)*np.pi/2.
	else:
		if(x>0.):
			return 0
		elif(x<0.):
			return np.pi
		else:
			return np.NaN

def atan2_unsigned(y,x):
	value=atan2_signed(y,x)
	if(value<0.):value+=2.*np.pi
	return value

def get_random_value_from_gamma_distribution(mean,std,size=None):
	return gamma.rvs((mean/std)**2,0,std**2/mean,size=size)

#from http://math.15873.pagesperso-orange.fr/page9.htm
def get_2D_polygon_center_of_mass(points):
	area=Gx=Gy=0
	for i in range(-1,len(points)-1,1):
		interm=points[i][0]*points[i+1][1]-points[i+1][0]*points[i][1]
		area+=interm
		Gx+=(points[i][0]+points[i+1][0])*interm
		Gy+=(points[i][1]+points[i+1][1])*interm
	area*=0.5
	Gx/=6*area
	Gy/=6*area
	return [Gx,Gy]
	
def get_2D_polygon_mass_inertia(points,density,cog_centered=False):
	if(not cog_centered):
		#Get the COG
		cog = get_2D_polygon_center_of_mass(points)
		#Center the polygon to the COG (so set COG to (0,0))
		centered_points = points[:] - cog
	else:
		centered_points=points
	#Loop on triangles around the COG (0,0) and compute its inertia
	I=0 ; m=0
	for i in range(-1,centered_points.shape[0]-1):
		#A==(0,0)
		B=Vector2(centered_points[i])
		C=Vector2(centered_points[i+1])
		tri_area=(B.cross(C)).norm()/2
		tri_inertia=density*tri_area/6 * ( B.dot(B) + B.dot(C) + C.dot(C) )
		m+=tri_area
		I+=tri_inertia
	return [m*density,I]

def get_2d_polygon_cog_mass_inertia(points,density):
	cog=get_2D_polygon_center_of_mass(points)
	return [cog]+get_2D_polygon_mass_inertia(points, cog, density)

def sort_2d_polygon_vertices(points):
	center=points.mean(axis=0)
	points[:]=points-center
	atan2_list=np.asarray([atan2_unsigned(p[1],p[0]) for p in points])
	points[:]=points[atan2_list.argsort()]+center
	
	
def center_2d_polygon_vertices(points):
	points[:]-=get_2D_polygon_center_of_mass(points)

def rotate_points_around_origin(points,radians):
	pointsX = points[:,0]*np.cos(radians) - points[:,1]*np.sin(radians)
	pointsY = points[:,0]*np.sin(radians) + points[:,1]*np.cos(radians)
	points[:] = np.array([pointsX,pointsY]).transpose()
	
def get_random_convex_polygon(n,Lx,Ly):
	
	#This is Valtr's algorithm, found here : https://cglab.ca/~sander/misc/ConvexGeneration/convex.html
	xPool = np.sort(np.random.rand(n))
	yPool = np.sort(np.random.rand(n))

	minX=xPool[0]
	maxX=xPool[-1]
	minY=yPool[0]
	maxY=yPool[-1]

	xVec = np.zeros(n)
	yVec = np.zeros(n)
	lastTop = minX
	lastBot = minX
	for i in range(1,n-1):
		x = xPool[i]
		if np.random.random()>0.5 :
			xVec[i-1]=x - lastTop
			lastTop = x
		else:
			xVec[i-1]=lastBot - x
			lastBot = x
	xVec[-2]=maxX - lastTop
	xVec[-1]=lastBot - maxX

	lastLeft = minY
	lastRight = minY
	for i in range(1,n-1):
		y = yPool[i]
		if np.random.random()>0.5 :
			yVec[i-1]=y - lastLeft
			lastLeft = y
		else:
			yVec[i-1]=lastRight - y
			lastRight = y
	yVec[-2]=maxY - lastLeft
	yVec[-1]=lastRight - maxY

	np.random.shuffle(yVec)
	vec=np.array((xVec,yVec)).transpose()
	
	angles=np.arctan2(vec[:,1],vec[:,0])
	vec=vec[angles.argsort()]

	vec[:,0]=np.cumsum(vec[:,0])
	vec[:,1]=np.cumsum(vec[:,1])
	
	xShift=minX - vec[:,0].min() - 0.5
	yShift=minY - vec[:,1].min() - 0.5
	
	vec+=np.array([xShift,yShift])
	
	# End of Valtr's algorithm
	
	#Find the largest point-point distance:
	maxDist=-np.inf
	id1=-1 ; id2=-1
	for i in range(n):
		for j in range(i+1,n):
			d=Vector2(vec[i]-vec[j]).norm()
			if(d>maxDist):
				maxDist=d
				id1=i ; id2=j
	
	#Find the angle of the largest point-point distance:
	long_vect = vec[id1]-vec[id2]
	angle = - np.arctan2(long_vect[1],long_vect[0])
	
	#Rotate the polygon to align its principal axis with X
	rotate_points_around_origin(vec,angle)
	
	#Scale with Lx and Ly:
	DX=vec[:,0].max() - vec[:,0].min()
	DY=vec[:,1].max() - vec[:,1].min()
	vec[:,0] *= Lx/DX
	vec[:,1] *= Ly/DY

	return vec











