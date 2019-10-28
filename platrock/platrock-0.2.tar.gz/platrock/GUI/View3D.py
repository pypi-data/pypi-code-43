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

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication
import vtk,time
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import sys
import numpy as np
from threading import Thread
import platrock.ThreeD.Simulations as Simulations
import platrock.ThreeD.Objects as Objects
import platrock.Common.Math as Math

class Window3D(object):
	def setup(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(1000, 700)
		self.centralWidget = QtGui.QWidget(MainWindow)
		self.gridlayout = QtGui.QGridLayout(self.centralWidget)
		self.vtkWidget = QVTKRenderWindowInteractor(self.centralWidget)
		self.gridlayout.addWidget(self.vtkWidget, 0, 0, 1, 1)
		self.start_stop_button = QtGui.QPushButton("START")
		if(Simulations.current_simulation and Simulations.current_simulation.status=="running"):
			self.start_stop_button.setText("PAUSE")
		self.start_stop_button.clicked.connect(self.handle_start_stop_button)
		self.gridlayout.addWidget(self.start_stop_button,0,1,1,2)

		MainWindow.setCentralWidget(self.centralWidget)
		
	def handle_start_stop_button(self):
		if(not Simulations.current_simulation.status=="running"):
			Simulations.current_simulation.status="running"
		else:
			Simulations.current_simulation.status="pause"


class View3D(QtGui.QMainWindow):
	def __init__(self, parent = None,):
		QtGui.QMainWindow.__init__(self, parent)
		self.window = Window3D()
		self.window.setup(self)
		# VTK renderer :
		self.ren = vtk.vtkRenderer()
		self.ren_win = self.window.vtkWidget.GetRenderWindow()
		self.ren_win.AddRenderer(self.ren)
		self.iren = self.ren_win.GetInteractor()
		self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
		#self.iren.GetInteractorStyle().SetInteractionModeToImage3D()
		self.addAxes()
		self.camera=self.ren_win.GetRenderers().GetFirstRenderer().GetActiveCamera()
		if(Simulations.current_simulation.limit_fps==0):
			self.fps=np.inf
		else:
			self.fps=Simulations.current_simulation.limit_fps
		self.time_last_updated=0
	
	def addAxes(self):
		transform = vtk.vtkTransform()
		terrain_points=Simulations.current_simulation.terrain.points_as_array
		transform.Translate(0.0, 0.0, terrain_points[:,2].mean())
		axes = vtk.vtkAxesActor()
		#  The axes are positioned with a user transform
		axes.SetUserTransform(transform)
		
		# properties of the axes labels can be set as follows
		# this sets the x axis label to red
		# axes->GetXAxisCaptionActor2D()->GetCaptionTextProperty()->SetColor(1,0,0);
		
		# the actual text of the axis label can be changed:
		# axes->SetXAxisLabelText("test");
		
		self.ren.AddActor(axes)
	
	def addTerrain(self,TO):
		# here each face of the "TO" has an actor
		for f in TO.faces:
			points = vtk.vtkPoints()
			triangles = vtk.vtkCellArray()
			for p in f.points:
				points.InsertPoint(p.id,p.pos[0],p.pos[1],p.pos[2])
			triangle = vtk.vtkTriangle()
			triangle.GetPointIds().SetId(0,f.points[0].id)
			triangle.GetPointIds().SetId(1,f.points[1].id)
			triangle.GetPointIds().SetId(2,f.points[2].id)
			triangles.InsertNextCell(triangle)
			
			# polydata object
			pd = vtk.vtkPolyData()
			pd.SetPoints( points )
			pd.SetPolys( triangles )
			# mapper
			mapper = vtk.vtkPolyDataMapper()
			if vtk.VTK_MAJOR_VERSION <= 5:
				mapper.SetInput(pd)
			else:
				mapper.SetInputData(pd)
				
			# actor
			actor = vtk.vtkActor()
			actor.SetMapper(mapper)
			actor.GetProperty().SetColor(f.color)
			actor.GetProperty().SetOpacity(TO.opacity)
			self.ren.AddActor(actor)
			f.VTK_actor=actor
	
	def addTriangulatedSurface(self,TO):
		# here the entire "TO" has one actor
		points = vtk.vtkPoints()
		triangles = vtk.vtkCellArray()
		
		for p in TO.points:
			points.InsertPoint(p.id,p.relPos[0],p.relPos[1],p.relPos[2])
			
		for f in TO.faces:
			triangle = vtk.vtkTriangle()
			triangle.GetPointIds().SetId(0,f.points[0].id)
			triangle.GetPointIds().SetId(1,f.points[1].id)
			triangle.GetPointIds().SetId(2,f.points[2].id)
			triangles.InsertNextCell(triangle)
			f.vtk_source=triangle
			
		# polydata object
		pd = vtk.vtkPolyData()
		pd.SetPoints( points )
		pd.SetPolys( triangles )
		TO.vtk_polydata=pd
		# mapper
		mapper = vtk.vtkPolyDataMapper()
		if vtk.VTK_MAJOR_VERSION <= 5:
			mapper.SetInput(pd)
		else:
			mapper.SetInputData(pd)
			
		# actor
		actor = vtk.vtkActor()
		actor.SetMapper(mapper)
		actor.GetProperty().SetColor(TO.color)
		actor.GetProperty().SetOpacity(TO.opacity)
		self.ren.AddActor(actor)
		TO.VTK_actor=actor
	
	def addTrees(self,terrain):
		lowest_terrain_point_z=terrain.points_as_array[:,2].min()
		highest_terrain_point_z=terrain.points_as_array[:,2].max()+50.
		cylinders_height=highest_terrain_point_z-lowest_terrain_point_z
		
		for t in terrain.trees:
			source = vtk.vtkCylinderSource()
			source.SetCenter(0,0,0)
			source.SetResolution(10)
			source.SetRadius(t.dhp/2./100)
			source.SetHeight(cylinders_height)
			
			mapper = vtk.vtkPolyDataMapper()
			mapper = vtk.vtkPolyDataMapper()
			if vtk.VTK_MAJOR_VERSION <= 5:
				mapper.SetInput(source.GetOutput())
			else:
				mapper.SetInputConnection(source.GetOutputPort())
			
			actor = vtk.vtkActor()
			actor.SetMapper(mapper)
			actor.GetProperty().SetColor(t.color)
			actor.RotateX(90.0)
			actor.SetPosition([t.pos[0],t.pos[1],lowest_terrain_point_z+cylinders_height/2.])
			self.ren.AddActor(actor)
			t.VTK_actor=actor
	
	
	def addPointsSpheres(self,TO):
		for p in TO.points:
			source = vtk.vtkSphereSource()
			source.SetCenter(0,0,0)
			source.SetRadius(p.radius)
			
			# mapper
			mapper = vtk.vtkPolyDataMapper()
			if vtk.VTK_MAJOR_VERSION <= 5:
				mapper.SetInput(source.GetOutput())
			else:
				mapper.SetInputConnection(source.GetOutputPort())
	
			# actor
			actor = vtk.vtkActor()
			actor.SetMapper(mapper)
			actor.GetProperty().SetColor(p.color)
			actor.GetProperty().SetOpacity(TO.opacity)
			point_global_rf=p.pos
			actor.SetPosition(point_global_rf)
			# assign actor to the renderer
			self.ren.AddActor(actor)
			p.VTK_actor=actor
			if(len(TO.points)==1):	#spheres for instance
				TO.VTK_actor=actor
	
	def addBoundingBox(self,TO):
		source = vtk.vtkCubeSource()
		source.SetCenter(0,0,0)
		source.SetXLength(TO.bounding_box.half_length*2)
		source.SetYLength(TO.bounding_box.half_length*2)
		source.SetZLength(TO.bounding_box.half_length*2)
		#source.SetThetaResolution(50)
		#source.SetPhiResolution(50)
		TO.bounding_box.vtk_source=source
		mapper = vtk.vtkPolyDataMapper()
		if vtk.VTK_MAJOR_VERSION <= 5:
			mapper.SetInput(source.GetOutput())
		else:
			mapper.SetInputConnection(source.GetOutputPort())
		actor = vtk.vtkActor()
		actor.SetMapper(mapper)
		actor.GetProperty().SetColor(0.53,0.8,0.92)
		actor.GetProperty().SetOpacity(TO.bounding_box.opacity)
		actor.SetPosition(TO.bounding_box.pos)
		# assign actor to the renderer
		self.ren.AddActor(actor)
		TO.bounding_box.VTK_actor=actor
	
	def addAngVel(self,rock):
		if(rock.angVel.norm()>0):
			
			
			cylinder_length=rock.angVel.norm()
			x,y,z=rock.angVel.normalized()*cylinder_length
			rotation=Math.Vector3([0,1,0]).cross(rock.angVel)
			angle=np.arcsin(y / np.sqrt(sum(rock.angVel**2)))
			source = vtk.vtkCylinderSource()
			#source.SetCenter(0,0,0)
			source.SetResolution(10)
			source.SetRadius(rock.radius/5.)
			source.SetHeight(np.sqrt(x**2 + y**2 + z**2))
			transform = vtk.vtkTransform()
			transform.Translate(rock.pos+0.5*Math.Vector3([x,y,z]))
			transform.RotateWXYZ(np.degrees(angle),rotation_axis[0],rotation_axis[1],rotation_axis[2])
			
			transformFilter=vtk.vtkTransformPolyDataFilter()
			transformFilter.SetTransform(transform)
			transformFilter.SetInputConnection(source.GetOutputPort())
			transformFilter.Update()
			
			mapper = vtk.vtkPolyDataMapper()
			mapper = vtk.vtkPolyDataMapper()
			if vtk.VTK_MAJOR_VERSION <= 5:
				mapper.SetInput(transformFilter.GetOutput())
			else:
				mapper.SetInputConnection(transformFilter.GetOutputPort())
			
			actor = vtk.vtkActor()
			actor.SetMapper(mapper)
			#actor.GetProperty().SetColor(t.color)
			#actor.RotateWXYZ(angle,np.degrees(rotation_axis[0]),np.degrees(rotation_axis[1]),np.degrees(rotation_axis[2]))
			#actor.SetPosition()
			self.ren.AddActor(actor)
			#rock.VTK_angVel_actor=actor

class ViewThread(Thread):
	def run(self):
		self.view=None
		app = QApplication(sys.argv)
		self.view = View3D()
		self.view.show()
		self.view.iren.Initialize() # Need this line to actually show the render inside Qt
		sys.exit(app.exec_())

def updateTreeColor(tree):
	tree.VTK_actor.GetProperty().SetColor(tree.color)
	#V.iren.Render()

def updateTO(TO):
	TO.VTK_actor.SetPosition(TO.pos)
	TO.VTK_actor.SetOrientation(0.,0.,0.)
	TO.VTK_actor.RotateWXYZ(TO.ori.angle()/np.pi*180.,TO.ori.vec[0],TO.ori.vec[1],TO.ori.vec[2])

	if(TO.enable_points_view):
		for p in TO.points:
			point_global_rf=p.pos
			p.VTK_actor.SetPosition(point_global_rf)
			p.VTK_actor.GetProperty().SetColor(p.color)
	if("bounding_box" in TO.__dict__):
		updateBoundingBox(TO)
	#V.addAngVel(TO)
	#V.iren.Render()

def updateBoundingBox(TO):
	TO.bounding_box.VTK_actor.SetPosition(TO.bounding_box.pos)
	TO.bounding_box.vtk_source.SetXLength(TO.bounding_box.half_length*2)
	TO.bounding_box.vtk_source.SetYLength(TO.bounding_box.half_length*2)
	TO.bounding_box.vtk_source.SetZLength(TO.bounding_box.half_length*2)

def updateTerrainTO(TO):
	for f in TO.faces:
		f.VTK_actor.GetProperty().SetColor(f.color)
	#V.iren.Render()

def updateTerrainColors(TO):
	colors=vtk.vtkUnsignedCharArray()
	colors.SetNumberOfComponents(3)
	faces_colors=(np.asarray([f.color for f in TO.faces])*255).astype(int)
	for fc in faces_colors:
		colors.InsertNextTuple3(fc[0],fc[1],fc[2])
	TO.vtk_polydata.GetCellData().SetScalars(colors)
	#V.iren.Render()
	

viewThread=ViewThread()
viewThread.setDaemon(True)
viewThread.start()
while(viewThread.view==None):
	time.sleep(0.1)
#time.sleep(1) #wait until the thread has created the view
V=viewThread.view

def draw_terrain(s):
	V.addTerrain(s.terrain)
	V.ren.ResetCamera()
	V.iren.Render()

def draw_rock(r):
	if(type(r)==Objects.Sphere):
		V.addPointsSpheres(r)
	else:
		V.addTriangulatedSurface(r)
	if(r.enable_points_view):
		V.addPointsSpheres(r)
	if('bounding_box' in r.__dict__):
		V.addBoundingBox(r)
	V.iren.Render()

def take_snapshot(filename):
	windowto_image_filter = vtk.vtkWindowToImageFilter()
	windowto_image_filter.SetInput(V.ren_win)
	windowto_image_filter.SetMagnification(1)  # image quality
	windowto_image_filter.SetInputBufferTypeToRGB()
	# Read from the front buffer.
	windowto_image_filter.ReadFrontBufferOff()
	windowto_image_filter.Update()
	
	writer = vtk.vtkPNGWriter()
	writer.SetFileName(filename)
	writer.SetInputConnection(windowto_image_filter.GetOutputPort())
	writer.Write()

def draw_trees(s):
	V.addTrees(s.terrain)
	V.ren.ResetCamera()
	V.iren.Render()
	
