import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import vtk

import vmi

tr = QObject()
tr = tr.tr


class PolyActor(QObject, vmi.Menu, vmi.Mouse):
    def __init__(self, view: vmi.View, name=None, shape_data=None, rgb=None, point=None, line=None, pickable=None):
        QObject.__init__(self)

        self.name = name if name else tr('物体 （Poly)')
        vmi.Menu.__init__(self, name=self.name)

        vmi.Mouse.__init__(self)
        for b in self.mouse:
            for e in self.mouse[b]:
                if e == 'Enter':
                    self.mouse[b][e] = self.mouseEnter
                elif e == 'Leave':
                    self.mouse[b][e] = self.mouseLeave
                elif e == 'Press':
                    self.mouse[b][e] = self.mousePress
                elif e == 'PressMoveRelease':
                    self.mouse[b][e] = (self.mousepass if b == 'RightButton' else self.mouseRelease)
                elif e == 'PressRelease':
                    self.mouse[b][e] = (self.mousepass if b == 'RightButton' else self.mouseRelease)

        self.view = view
        self._Mapper = vtk.vtkPolyDataMapper()
        self._Prop = vtk.vtkActor()
        self._Prop._Prop = self
        self.view._Renderer.AddActor(self._Prop)

        self._Property: vtk.vtkProperty = self._Prop.GetProperty()
        self._RGB, self._Alpha = [1, 1, 1], 1.0
        self.color()
        self._Pickable = False
        self.pickable()
        self._Shade = True
        self.shade(True)
        self._AlwaysOnTop = False
        self.alwaysOnTop(False)

        self._Data = vtk.vtkPolyData()
        self._Bind = self
        self.bind()

        if shape_data is not None:
            self.bind(shape_data)

        if rgb is not None:
            self.color(rgb=rgb)

        if point is not None:
            self.size(point=point)

        if line is not None:
            self.size(line=line)

        if pickable is not None:
            self.pickable(pickable)

    def __setstate__(self, s):
        self.__init__(s['view'], s['name'])
        self.__dict__.update(s)
        s = self.__dict__

        self._Data.DeepCopy(vmi.loads(s['_Dumps']['_Data']))
        del s['_Dumps']

        for kw in s['_VTKGets']:
            vmi.vtkset(getattr(self, kw), s['_VTKGets'][kw])
        del s['_VTKGets']

        self.bind()

    def __getstate__(self):
        s = self.__dict__.copy()
        for kw in ['menu', 'actions', '__METAOBJECT__']:
            if kw in s:
                del s[kw]

        s['_Dumps'] = {'_Data': vmi.dumps(self._Data)}
        for kw in s['_Dumps']:
            del s[kw]

        s['_VTKGets'] = {name: vmi.vtkget(getattr(self, name)) for name in
                         ['_Mapper', '_Prop', '_Property']}
        for kw in s['_VTKGets']:
            del s[kw]
        return s

    def data(self):
        return self._Bind._Data

    def bind(self, other=None):
        if hasattr(other, '_Data'):
            self._Bind = other
        self._Mapper.SetInputData(self.data())
        self._Prop.SetMapper(self._Mapper)
        self.view.updateInTime()

    def clone(self, other=None):
        if other is None:
            self.data().ShallowCopy(self.data().__class__())
        elif hasattr(other, '_Data'):
            self.data().ShallowCopy(other.data())
        elif isinstance(other, self.data().__class__):
            self.data().ShallowCopy(other)
        else:
            raise TypeError(type(other))

    def alwaysOnTop(self, arg=None):
        self.view.updateInTime()
        if arg is True:
            self._AlwaysOnTop = True
            self._Mapper.SetRelativeCoincidentTopologyLineOffsetParameters(0, -66000)
            self._Mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(0, -66000)
            self._Mapper.SetRelativeCoincidentTopologyPointOffsetParameter(-66000)
        elif arg is False:
            self._AlwaysOnTop = False
            self._Mapper.SetRelativeCoincidentTopologyLineOffsetParameters(-1, -1)
            self._Mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(-1, -1)
            self._Mapper.SetRelativeCoincidentTopologyPointOffsetParameter(-1)
        return self._AlwaysOnTop

    def color(self, rgb=None, alpha=None):
        self.view.updateInTime()
        if rgb is not None:
            self._RGB = rgb
        if alpha is not None:
            self._Alpha = alpha
        self._Property.SetColor(self._RGB)
        self._Property.SetOpacity(self._Alpha)
        return {'rgb': self._RGB, 'alpha': self._Alpha}

    def colorLight(self):
        c = QColor()
        c.setRgbF(self._RGB[0], self._RGB[1], self._RGB[2])
        c = c.lighter(120)
        self._Property.SetColor(c.redF(), c.greenF(), c.blueF())
        self.view.updateInTime()

    def colorDark(self):
        c = QColor()
        c.setRgbF(self._RGB[0], self._RGB[1], self._RGB[2])
        c = c.darker(120)
        self._Property.SetColor(c.redF(), c.greenF(), c.blueF())
        self.view.updateInTime()

    def colorNormal(self):
        self._Property.SetColor(self._RGB)
        self.view.updateInTime()

    def delete(self):
        self._Data.ReleaseData()
        self.view._Renderer.RemoveActor(self._Prop)

    def pickable(self, arg=None):
        if arg is True:
            self._Pickable = True
        elif arg is False:
            self._Pickable = False
        self._Prop.SetPickable(1 if self._Pickable else 0)
        self.view.updateInTime()
        return self._Pickable

    def visible(self, visible=None):
        if visible is not None:
            self._Prop.SetVisibility(1 if visible else 0)
            self.view.updateInTime()
        return True if self._Prop.GetVisibility() else False

    def visibleToggle(self, *args):
        self.visible(not self.visible())

    def rep(self, arg=None):
        self.view.updateInTime()
        if isinstance(arg, str):
            if arg.lower() == 'points':
                self._Property.SetRepresentationToPoints()
            elif arg.lower() == 'wireframe':
                self._Property.SetRepresentationToWireframe()
            elif arg.lower() == 'surface':
                self._Property.SetRepresentationToSurface()
            elif arg.lower() == 'toggle':
                r = (self._Property.GetRepresentation() + 1) % 3
                self.rep(('points', 'wireframe', 'surface')[r])
        return ('points', 'wireframe', 'surface')[self._Property.GetRepresentation()]

    def shade(self, arg=None):
        self.view.updateInTime()
        if arg is True:
            self._Shade = True
            self._Property.SetAmbient(0)
            self._Property.SetDiffuse(1)
        elif arg is False:
            self._Shade = False
            self._Property.SetAmbient(1)
            self._Property.SetDiffuse(0)
        return self._Shade

    def size(self, **kwargs):
        self.view.updateInTime()
        if 'point' in kwargs:
            self._Property.SetPointSize(kwargs['point'])
        if 'line' in kwargs:
            self._Property.SetLineWidth(kwargs['line'])
        return {'point': self._Property.GetPointSize(),
                'line': self._Property.GetLineWidth()}

    def mouseEnter(self, **kwargs):
        self.colorLight()
        self.mousepass()

    def mousePress(self, **kwargs):
        self.colorDark()
        self.mousepass()

    def mouseRelease(self, **kwargs):
        self.colorNormal()
        self.mousepass()

    def mouseLeave(self, **kwargs):
        self.colorNormal()
        self.mousepass()


class TextActor(QObject, vmi.Menu, vmi.Mouse):
    def __init__(self, view: vmi.View, name=None):
        QObject.__init__(self)

        self.name = name if name else tr('文字 （Text)')
        vmi.Menu.__init__(self, name=self.name)

        vmi.Mouse.__init__(self)
        for b in self.mouse:
            for e in self.mouse[b]:
                if e == 'Enter':
                    self.mouse[b][e] = self.mouseEnter
                elif e == 'Leave':
                    self.mouse[b][e] = self.mouseLeave
                elif e == 'Press':
                    self.mouse[b][e] = self.mousePress
                elif e == 'PressMoveRelease':
                    self.mouse[b][e] = self.mouseRelease
                elif e == 'PressRelease':
                    self.mouse[b][e] = self.mouseRelease

        self.view = view
        self._Prop = vtk.vtkTextActor()
        self._Prop._Prop = self
        self.view._Renderer.AddActor(self._Prop)

        self._Prop.SetTextScaleModeToNone()

        self._Property: vtk.vtkTextProperty = self._Prop.GetTextProperty()
        self._Property.SetFontSize(0)
        self._Property.SetFontFamily(vtk.VTK_FONT_FILE)
        self._Property.SetLineSpacing(1.2)
        self._Property.SetShadow(0)

        self._Text = ''
        self.text()

        self._Aligns = {'left': vtk.VTK_TEXT_LEFT, 'right': vtk.VTK_TEXT_RIGHT,
                        'top': vtk.VTK_TEXT_TOP, 'bottom': vtk.VTK_TEXT_BOTTOM,
                        'center': vtk.VTK_TEXT_CENTERED, }

        self._Align = ['left', 'bottom']
        self.align()
        self._Pos = [0, 0]
        self.pos()
        self._Font = 'alizh'
        self.font()
        self._FontSize = 16
        self.size()

        self._RGB, self._Alpha = [0.2, 0.2, 0.2], 1.0
        self.color()
        self._Pickable = True
        self.pickable()

    def __setstate__(self, s):
        self.__init__(s['view'], s['name'])
        self.__dict__.update(s)
        s = self.__dict__

        del s['_Dumps']

        for kw in s['_VTKGets']:
            vmi.vtkset(getattr(self, kw), s['_VTKGets'][kw])
        del s['_VTKGets']

    def __getstate__(self):
        s = self.__dict__.copy()
        for kw in ['menu', 'actions', '__METAOBJECT__']:
            if kw in s:
                del s[kw]

        s['_Dumps'] = {}
        for kw in s['_Dumps']:
            del s[kw]

        s['_VTKGets'] = {name: vmi.vtkget(getattr(self, name)) for name in
                         ['_Prop', '_Property']}
        for kw in s['_VTKGets']:
            del s[kw]
        return s

    def text(self, text=None):
        if text is not None:
            self._Text = text
        self._Prop.SetInput(self._Text)
        self.view.updateInTime()

    def align(self, h=None, v=None):
        if h is not None:
            self._Align[0] = h
        if v is not None:
            self._Align[1] = v
        self._Property.SetJustification(self._Aligns[self._Align[0]])
        self._Property.SetVerticalJustification(self._Aligns[self._Align[1]])
        self.view.updateInTime()
        return self._Align

    def pos(self, x=None, y=None):
        if x is not None:
            self._Pos[0] = x
        if y is not None:
            self._Pos[1] = y
        self._Prop.SetPosition(self._Pos)
        self.view.updateInTime()
        return self._Pos

    def font(self, font=None):
        if font is not None and font in vmi.appFonts:
            self._Font = font
        self._Property.SetFontFile(vmi.appFonts[self._Font])
        self.view.updateInTime()
        return self._Font

    def color(self, rgb=None, alpha=None):
        self.view.updateInTime()
        if rgb is not None:
            self._RGB = rgb
        if alpha is not None:
            self._Alpha = alpha
        self._Property.SetColor(self._RGB)
        self._Property.SetOpacity(self._Alpha)
        return {'rgb': self._RGB, 'alpha': self._Alpha}

    def colorLight(self):
        c = QColor()
        c.setRgbF(self._RGB[0], self._RGB[1], self._RGB[2])
        c = c.lighter(120)
        self._Property.SetColor(c.redF(), c.greenF(), c.blueF())
        self.view.updateInTime()

    def colorDark(self):
        c = QColor()
        c.setRgbF(self._RGB[0], self._RGB[1], self._RGB[2])
        c = c.darker(120)
        self._Property.SetColor(c.redF(), c.greenF(), c.blueF())
        self.view.updateInTime()

    def colorNormal(self):
        self._Property.SetColor(self._RGB)
        self.view.updateInTime()

    def delete(self):
        self.view._Renderer.RemoveActor(self._Prop)

    def pickable(self, arg=None):
        if arg is True:
            self._Pickable = True
        elif arg is False:
            self._Pickable = False
        self._Prop.SetPickable(1 if self._Pickable else 0)
        self.view.updateInTime()
        return self._Pickable

    def visible(self, visible=None):
        if visible is not None:
            self._Prop.SetVisibility(1 if visible else 0)
            self.view.updateInTime()
        return True if self._Prop.GetVisibility() else False

    def visibleToggle(self, *args):
        self.visible(not self.visible())

    def size(self, **kwargs):
        if 'font' in kwargs:
            self._FontSize = kwargs['font']
        self._Property.SetFontSize(self._FontSize)
        self.view.updateInTime()
        return self._FontSize

    def mouseEnter(self, **kwargs):
        self.colorLight()
        self.mousepass()

    def mousePress(self, **kwargs):
        self.colorDark()
        self.mousepass()

    def mouseRelease(self, **kwargs):
        self.colorNormal()
        self.mousepass()

    def mouseLeave(self, **kwargs):
        self.colorNormal()
        self.mousepass()


class ImageSlice(QObject, vmi.Menu, vmi.Mouse):
    """场景表示，图像数据的断层表示
    vtk.vtkImageData -> vtk.vtkImageSlice"""

    def __init__(self, view: vmi.View, name=None):
        QObject.__init__(self)

        self.name = name if name else tr('图面 （Image slice)')
        vmi.Menu.__init__(self, name=self.name)

        self.actions = {'Visible': QAction(''),
                        'SlicePlaneValueNormal': QAction(''),
                        'SlicePlaneAxial': QAction(tr('横断位 (Axial)')),
                        'SlicePlaneSagittal': QAction(tr('矢状位 (Sagittal)')),
                        'SlicePlaneCoronal': QAction(tr('冠状位 (Coronal)')),
                        'WindowValue': QAction(''),
                        'WindowAuto': QAction(tr('自动 (Auto)')),
                        'WindowBone': QAction(tr('骨骼 (Bone)')),
                        'WindowSoft': QAction(tr('组织 (Soft)'))}

        self.actions['Visible'].triggered.connect(self.visibleToggle)
        self.actions['SlicePlaneAxial'].triggered.connect(self.slicePlaneAxial)
        self.actions['SlicePlaneSagittal'].triggered.connect(self.slicePlaneSagittal)
        self.actions['SlicePlaneCoronal'].triggered.connect(self.slicePlaneCoronal)
        self.actions['WindowAuto'].triggered.connect(self.windowAuto)
        self.actions['WindowBone'].triggered.connect(self.windowBone)
        self.actions['WindowSoft'].triggered.connect(self.windowSoft)

        def aboutToShow():
            self.actions['Visible'].setText(
                tr('可见 (Visible)') + ' = ' + (tr('显示 (Show)') if self.visible() else tr('隐藏 (Hide)')))
            self.actions['SlicePlaneValueNormal'].setText(
                tr('法向 (Normal)') + ' = ' + repr(self._BindSlicePlane._SlicePlane.GetNormal()))
            self.actions['WindowValue'].setText(
                tr('宽/位 (W/L)') + ' = ' + (repr(tuple(self._Window))))

            self.menu.clear()
            self.menu.addAction(self.actions['Visible'])

            menu = QMenu(tr('切面 (Slice plane)'))
            menu.addAction(self.actions['SlicePlaneValueNormal'])
            menu.addSeparator()
            menu.addAction(self.actions['SlicePlaneAxial'])
            menu.addAction(self.actions['SlicePlaneSagittal'])
            menu.addAction(self.actions['SlicePlaneCoronal'])
            self.menu.addMenu(menu)

            menu = QMenu(tr('窗 (Window)'))
            menu.addAction(self.actions['WindowValue'])
            menu.addSeparator()
            menu.addAction(self.actions['WindowAuto'])
            menu.addAction(self.actions['WindowBone'])
            menu.addAction(self.actions['WindowSoft'])
            self.menu.addMenu(menu)

        self.menu.aboutToShow.connect(aboutToShow)

        vmi.Mouse.__init__(self, menu=self)
        self.mouse['NoButton']['Wheel'] = self.slice
        self.mouse['LeftButton']['PressMove'] = self.windowMove

        self.view = view
        self._Mapper = vtk.vtkImageResliceMapper()
        self._Prop = vtk.vtkImageSlice()
        self._Prop._Prop = self
        self.view._Renderer.AddViewProp(self._Prop)

        self._Property = self._Prop.GetProperty()
        self._Property.SetInterpolationTypeToCubic()
        self._Property.SetUseLookupTableScalarRange(1)

        self._Data = vtk.vtkImageData()
        self._Bind = self

        self._SlicePlane = vtk.vtkPlane()
        self._BindSlicePlane = self

        self._LookupTable = vtk.vtkLookupTable()
        self._BindLookupTable = self

        self._Window = [1000, 400]

        self.bind()
        self.bindSlicePlane()
        self.bindLookupTable()
        self.windowSoft()

    def __setstate__(self, s):
        self.__init__(s['view'], s['name'])
        self.__dict__.update(s)
        s = self.__dict__

        self._Data.DeepCopy(vmi.loads(s['_Dumps']['_Data']))
        self._LookupTable.DeepCopy(vmi.loads(s['_Dumps']['_LookupTable']))
        del s['_Dumps']

        for kw in s['_VTKGets']:
            vmi.vtkset(getattr(self, kw), s['_VTKGets'][kw])
        del s['_VTKGets']

        self._Pickable = True
        self.pickable()

        self.bind()
        self.bindSlicePlane()
        self.bindLookupTable()

    def __getstate__(self):
        s = self.__dict__.copy()
        for kw in ['menu', 'menuWindow', 'menuSlicePlane', 'actions', '__METAOBJECT__']:
            if kw in s:
                del s[kw]

        s['_Dumps'] = {'_Data': vmi.dumps(self._Data),
                       '_LookupTable': vmi.dumps(self._LookupTable)}
        for kw in s['_Dumps']:
            del s[kw]

        s['_VTKGets'] = {name: vmi.vtkget(getattr(self, name)) for name in
                         ['_Mapper', '_Prop', '_Property', '_SlicePlane']}
        for kw in s['_VTKGets']:
            del s[kw]

        return s

    def data(self):
        return self._Bind._Data

    def bind(self, other=None):
        if hasattr(other, '_Data'):
            self._Bind = other
        elif other is not None:
            raise AttributeError(other)
        self._Mapper.SetInputData(self.data())
        self._Prop.SetMapper(self._Mapper)
        self.view.updateInTime()

    def bindSlicePlane(self, other=None):
        if hasattr(other, '_SlicePlane'):
            self._BindSlicePlane = other
        self._Mapper.SetSlicePlane(self._BindSlicePlane._SlicePlane)
        self.view.updateInTime()

    def bindLookupTable(self, other=None):
        if hasattr(other, '_LookupTable'):
            self._BindLookupTable = other
        self._Property.SetLookupTable(self._BindLookupTable._LookupTable)
        self.view.updateInTime()

    def clone(self, other):
        if other is None:
            self.data().DeepCopy(self.data().__class__())
        elif hasattr(other, '_Data'):
            self.data().DeepCopy(other.data())
        elif isinstance(other, self.data().__class__):
            self.data().DeepCopy(other)
        else:
            raise TypeError(type(other))

    def delete(self, *args):
        self._Data.ReleaseData()
        self.view._Renderer.RemoveViewProp(self._Prop)

    def pickable(self, arg=None):
        if arg is True:
            self._Pickable = True
        elif arg is False:
            self._Pickable = False
        self._Prop.SetPickable(1 if self._Pickable else 0)
        self.view.updateInTime()
        return self._Pickable

    def visible(self, visible=None):
        if visible is not None:
            self._Prop.SetVisibility(1 if visible else 0)
            self.view.updateInTime()
        return True if self._Prop.GetVisibility() else False

    def visibleToggle(self, *args):
        self.visible(not self.visible())

    def slicePlane(self, face=None, origin=None):
        if isinstance(origin, str):
            if origin.lower() == 'center':
                o = self.data().GetCenter()
                self._BindSlicePlane._SlicePlane.SetOrigin(o[0], o[1], o[2])
            elif origin.lower() in ('b0', 'b1', 'b2', 'b3', 'b4', 'b5'):
                i = int(origin[-1])
                o = list(self.data().GetCenter())
                o[int(i / 2)] = self.data().GetBounds()[i]
                self._BindSlicePlane._SlicePlane.SetOrigin(o[0], o[1], o[2])
        elif origin is not None:
            self._BindSlicePlane._SlicePlane.SetOrigin(origin[0], origin[1], origin[2])
        if isinstance(face, str):
            if face.lower() == 'sagittal':
                self._BindSlicePlane._SlicePlane.SetNormal(1, 0, 0)
            elif face.lower() == 'coronal':
                self._BindSlicePlane._SlicePlane.SetNormal(0, 1, 0)
            elif face.lower() == 'axial':
                self._BindSlicePlane._SlicePlane.SetNormal(0, 0, 1)
        elif face is not None:
            self._BindSlicePlane._SlicePlane.SetNormal(face[0], face[1], face[2])
        self.view.updateInTime()

    def slicePlaneAxial(self):
        self.slicePlane(face='axial')

    def slicePlaneSagittal(self):
        self.slicePlane(face='sagittal')

    def slicePlaneCoronal(self):
        self.slicePlane(face='coronal')

    def window(self, preset=None, width=None, level=None):
        if preset is None:
            if width is not None:
                self._Window[0] = width
            if level is not None:
                self._Window[1] = level

            self._Window[0] = int(self._Window[0])
            self._Window[1] = int(self._Window[1])

            r = [self._Window[1] - 0.5 * self._Window[0],
                 self._Window[1] + 0.5 * self._Window[0]]

            t = self._BindLookupTable._LookupTable
            t.SetNumberOfTableValues(self._Window[0])
            t.SetTableRange(r)
            t.SetBelowRangeColor(0, 0, 0, 1.0)
            t.SetAboveRangeColor(1, 1, 1, 1.0)
            t.SetUseBelowRangeColor(1)
            t.SetUseAboveRangeColor(1)

            for i in range(self._Window[0]):
                v = i / self._Window[0]
                t.SetTableValue(i, (v, v, v, 1.0))
            self.view.updateInTime()

        elif preset.lower() == 'auto':
            r = vtk.vtkImageHistogramStatistics()
            r.SetInputData(self.data())
            r.SetAutoRangePercentiles(1, 99)
            r.SetGenerateHistogramImage(0)
            r.Update()
            r = r.GetAutoRange()

            self.window(width=r[1] - r[0], level=0.5 * (r[0] + r[1]))
        elif preset.lower() == 'bone':
            self.window(width=1000, level=400)
        elif preset.lower() == 'soft':
            self.window(width=350, level=50)

    def windowAuto(self, **kwargs):
        self.window('auto')

    def windowBone(self, **kwargs):
        self.window('bone')

    def windowSoft(self, **kwargs):
        self.window('soft')

    def slice(self, **kwargs):
        o = list(self._BindSlicePlane._SlicePlane.GetOrigin())
        n = self._BindSlicePlane._SlicePlane.GetNormal()
        dim = self.data().GetDimensions()
        dxyz = self.data().GetSpacing()

        n = [abs(_) / (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5 for _ in n]
        dn = n[0] * dxyz[0] + n[1] * dxyz[1] + n[2] * dxyz[2]

        for i in range(3):
            if dim[i] > 1:
                o[i] += kwargs['delta'] * dn * n[i]

        if vtk.vtkMath.PlaneIntersectsAABB(self.data().GetBounds(), n, o) == 0:
            self.slicePlane(origin=o)

    def windowMove(self, **kwargs):
        dx, dy = self.view.mouseOverDisplay()

        r = self.data().GetScalarRange()
        t = (r[1] - r[0]) / 2048
        self._Window[0] += t * dx
        self._Window[1] -= t * dy

        self._Window[0] = max(self._Window[0], 0)
        self._Window[0] = min(self._Window[0], r[1] - r[0])
        self._Window[1] = max(self._Window[1], r[0])
        self._Window[1] = min(self._Window[1], r[1])
        self.window()


class ImageVolume(QObject, vmi.Menu, vmi.Mouse):
    """场景表示，图像数据的立体表示
    vtk.vtkImageData -> vtk.vtkVolume"""

    def __init__(self, view: vmi.View, name=None):
        QObject.__init__(self)

        self.name = name if name else tr('图体 （Image volume)')
        vmi.Menu.__init__(self, name=self.name)

        self.actions = {'Visible': QAction(''),
                        'Threshold': QAction(tr('阈值 (Threshold)'))}

        self.actions['Visible'].triggered.connect(self.visibleToggle)
        self.actions['Threshold'].triggered.connect(self.threshold)

        def aboutToShow():
            self.actions['Visible'].setText(
                tr('可见 (Visible)') + ' = ' + (tr('显示 (Show)') if self.visible() else tr('隐藏 (Hide)')))

            self.menu.clear()
            self.menu.addAction(self.actions['Visible'])

            menu = QMenu(tr('风格 (Style)'))
            menu.addAction(self.actions['Threshold'])
            self.menu.addMenu(menu)

        self.menu.aboutToShow.connect(aboutToShow)

        vmi.Mouse.__init__(self)

        self.view = view
        self._Mapper = vtk.vtkGPUVolumeRayCastMapper()
        self._Prop = vtk.vtkVolume()
        self._Prop._Prop = self
        self.view._Renderer.AddVolume(self._Prop)

        self._Mapper.SetBlendModeToComposite()
        self._Mapper.SetMaxMemoryInBytes(4096)
        self._Mapper.SetMaxMemoryFraction(1)
        self._Mapper.SetAutoAdjustSampleDistances(0)
        self._Mapper.SetLockSampleDistanceToInputSpacing(1)
        self._Mapper.SetUseJittering(1)

        self._Property = self._Prop.GetProperty()
        self._Property.SetInterpolationTypeToLinear()
        self._Property.SetAmbient(0.1)
        self._Property.SetDiffuse(0.9)
        self._Property.SetShade(1)

        self._Data = vtk.vtkImageData()
        self._Bind = self

        self._Color = {0: [1, 1, 1]}
        self._ScalarOpacity = {0: 0, 400: 1}
        self._GradientOpacity = {}

        self._Pickable = True
        self.pickable()

        self.bind()
        self.color()
        self.opacityScalar()
        self.opacityGradient()

    def __setstate__(self, s):
        self.__init__(s['view'], s['name'])
        self.__dict__.update(s)
        s = self.__dict__

        self._Data.DeepCopy(vmi.loads(s['_Dumps']['_Data']))
        del s['_Dumps']

        for kw in s['_VTKGets']:
            vmi.vtkset(getattr(self, kw), s['_VTKGets'][kw])
        del s['_VTKGets']

        self.bind()
        self.color()
        self.opacityScalar()
        self.opacityGradient()

    def __getstate__(self):
        s = self.__dict__.copy()
        for kw in ['menu', 'actions', '__METAOBJECT__']:
            if kw in s:
                del s[kw]

        s['_Dumps'] = {'_Data': vmi.dumps(self._Data),
                       '_Color': self._Color}
        for kw in s['_Dumps']:
            del s[kw]

        s['_VTKGets'] = {name: vmi.vtkget(getattr(self, name)) for name in
                         ['_Mapper', '_Prop', '_Property']}
        for kw in s['_VTKGets']:
            del s[kw]

        return s

    def data(self):
        return self._Bind._Data

    def bind(self, other=None):
        if hasattr(other, '_Data'):
            self._Bind = other
        elif other is not None:
            raise AttributeError(other)
        self._Mapper.SetInputData(self.data())
        self._Prop.SetMapper(self._Mapper)
        self.view.updateInTime()

    def clone(self, other):
        if other is None:
            self.data().ShallowCopy(self.data().__class__())
        elif hasattr(other, 'data'):
            self.data().ShallowCopy(other.data())
        elif isinstance(other, self.data().__class__):
            self.data().ShallowCopy(other)
        else:
            raise TypeError(type(other))

    def delete(self):
        # self._Data.ReleaseData()
        image = vtk.vtkImageData()
        image.SetExtent(0, 1, 0, 0, 0, 0)
        image.AllocateScalars(vtk.VTK_SHORT, 1)
        self.clone(image)
        self.view._Renderer.RemoveVolume(self._Prop)

    def pickable(self, arg=None):
        if arg is True:
            self._Pickable = True
        elif arg is False:
            self._Pickable = False
        self._Prop.SetPickable(1 if self._Pickable else 0)
        self.view.updateInTime()
        return self._Pickable

    def visible(self, visible=None):
        if visible is not None:
            self._Prop.SetVisibility(1 if visible else 0)
            self.view.updateInTime()
        return True if self._Prop.GetVisibility() else False

    def visibleToggle(self, *args):
        self.visible(not self.visible())

    def color(self, scalar_rgb=None):
        if scalar_rgb is not None:
            self._Color = scalar_rgb
            return self.color()
        else:
            f = vtk.vtkColorTransferFunction()
            for x in self._Color:
                r, g, b = self._Color[x]
                f.AddRGBPoint(x, r, g, b)

            self._Property.SetColor(f)
            return self._Color

    def opacityScalar(self, scalar_opacity=None):
        if scalar_opacity is not None:
            self._ScalarOpacity = scalar_opacity
            return self.opacityScalar()
        else:
            f = vtk.vtkPiecewiseFunction()
            for x in self._ScalarOpacity:
                f.AddPoint(x, self._ScalarOpacity[x])
            self._Property.SetScalarOpacity(f)
            return self._Property

    def opacityGradient(self, gradient_opacity=None):
        if gradient_opacity is not None:
            self._GradientOpacity = gradient_opacity
            return self.opacityScalar()
        else:
            f = vtk.vtkPiecewiseFunction()
            for x in self._GradientOpacity:
                f.AddPoint(x, self._GradientOpacity[x])
            self._Property.SetGradientOpacity(f)
            return self._Property

    def threshold(self, *args, value=None):
        if value is None:
            value = vmi.askInt(vtk.VTK_SHORT_MIN, 0, vtk.VTK_SHORT_MAX, tr('阈值 (Threshold value)'))
        if value is not None:
            self.opacityScalar({value - 1: 0, value: 1})
