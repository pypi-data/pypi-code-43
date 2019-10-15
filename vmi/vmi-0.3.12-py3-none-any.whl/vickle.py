import locale
import pathlib
import shutil
import tempfile
from PySide2.QtCore import *

import vmi
import vtk
import numpy as np

from OCC.Core.TopoDS import *
from OCC.Core.STEPControl import *
from OCC.Core.IFSelect import *

vtkget_ignore = ('GetDebug', 'GetGlobalReleaseDataFlag', 'GetGlobalWarningDisplay', 'GetReferenceCount',
                 'GetAAFrames', 'GetFDFrames', 'GetSubFrames', 'GetUseConstantFDOffsets', 'GetStereoCapableWindow',
                 'GetForceCompileOnly', 'GetGlobalImmediateModeRendering', 'GetImmediateModeRendering',
                 'GetScalarMaterialMode', 'GetReleaseDataFlag')


def vtkset(self, gets: dict):
    for getname in gets:
        setname = getname.replace('Get', 'Set', 1)
        try:
            getattr(self, setname)(gets[getname])
        except TypeError:
            pass


def vtkget(self):
    gets = {}
    for getname in dir(self):
        if getname.startswith('Get'):
            setname = getname.replace('Get', 'Set', 1)
            if hasattr(self, setname) and getname not in vtkget_ignore:
                try:
                    a = getattr(self, getname)()
                    if 'vtk' not in str(type(a)):
                        gets[getname] = a
                except TypeError:
                    pass
    return gets


def dumps(arg):
    if isinstance(arg, vtk.vtkImageData):
        if arg.GetNumberOfPoints() == 0:
            return ['vtkImageData', bytes()]
        else:
            with tempfile.TemporaryDirectory() as p:
                p = pathlib.Path(p) / '.nii'
                w = vtk.vtkNIFTIImageWriter()
                w.SetFileName(str(p))
                w.SetInputData(arg)
                w.Update()
                return ['vtkImageData', p.read_bytes()]
    elif isinstance(arg, vtk.vtkPolyData):
        if arg.GetNumberOfPoints() == 0:
            return ['vtkPolyData', bytes()]
        else:
            with tempfile.TemporaryDirectory() as p:
                p = pathlib.Path(p) / '.vtp'
                w = vtk.vtkPolyDataWriter()
                w.SetFileTypeToBinary()
                w.SetFileName(str(p))
                w.SetInputData(arg)
                w.Update()
                return ['vtkPolyData', p.read_bytes()]
    elif isinstance(arg, vtk.vtkLookupTable):
        p = {'GetNumberOfTableValues': arg.GetNumberOfTableValues(),
             'GetTableRange': arg.GetTableRange(),
             'GetBelowRangeColor': arg.GetBelowRangeColor(),
             'GetAboveRangeColor': arg.GetAboveRangeColor(),
             'GetUseBelowRangeColor': arg.GetUseBelowRangeColor(),
             'GetUseAboveRangeColor': arg.GetUseAboveRangeColor(),
             'GetTableValue': []}
        for i in range(arg.GetNumberOfTableValues()):
            p['GetTableValue'].append(arg.GetTableValue(i))
        return ['vtkLookupTable', p]
    elif isinstance(arg, TopoDS_Shape):
        if arg.IsNull():
            return ['TopoDS_Shape', bytes()]
        else:
            with tempfile.TemporaryDirectory() as p:
                p = pathlib.Path(p) / '.stp'
                w = STEPControl_Writer()
                w.Transfer(arg, STEPControl_AsIs)
                status = w.Write(str(p))
                if status == IFSelect_RetDone:
                    return ['TopoDS_Shape', p.read_bytes()]
                raise Exception(('IFSelect_RetVoid', 'IFSelect_RetDone', 'IFSelect_RetError',
                                 'IFSelect_RetFail', 'IFSelect_RetStop')[status])
    raise TypeError(type(arg))


def loads(arg):
    if arg[0] == 'vtkImageData':
        if len(arg[1]) == 0:
            return vtk.vtkImageData()
        else:
            with tempfile.TemporaryDirectory() as p:
                p = pathlib.Path(p) / '.nii'
                p.write_bytes(arg[1])
                r = vtk.vtkNIFTIImageReader()
                r.SetFileName(str(p))
                r.Update()
                return r.GetOutput()
    elif arg[0] == 'vtkPolyData':
        if len(arg[1]) == 0:
            return vtk.vtkPolyData()
        else:
            with tempfile.TemporaryDirectory() as p:
                p = pathlib.Path(p) / '.vtp'
                p.write_bytes(arg[1])
                r = vtk.vtkPolyDataReader()
                r.SetFileName(str(p))
                r.Update()
                return r.GetOutput()
    elif arg[0] == 'vtkLookupTable':
        r = vtk.vtkLookupTable()
        r.SetNumberOfTableValues(arg[1]['GetNumberOfTableValues'])
        r.SetTableRange(arg[1]['GetTableRange'])
        r.SetBelowRangeColor(arg[1]['GetBelowRangeColor'])
        r.SetAboveRangeColor(arg[1]['GetAboveRangeColor'])
        r.SetUseBelowRangeColor(arg[1]['GetUseBelowRangeColor'])
        r.SetUseAboveRangeColor(arg[1]['GetUseAboveRangeColor'])
        for i in range(arg[1]['GetNumberOfTableValues']):
            r.SetTableValue(i, arg[1]['GetTableValue'][i])
        return r
    elif arg[0] == 'TopoDS_Shape':
        if len(arg[1]) == 0:
            return TopoDS_Shape()
        else:
            with tempfile.TemporaryDirectory() as p:
                p = pathlib.Path(p) / '.stp'
                p.write_bytes(arg[1])
                r = STEPControl_Reader()
                status = r.ReadFile(str(p))
                if status == IFSelect_RetDone:
                    r.TransferRoots()
                    return r.OneShape()
                else:
                    raise Exception(('IFSelect_RetVoid', 'IFSelect_RetDone', 'IFSelect_RetError',
                                     'IFSelect_RetFail', 'IFSelect_RetStop')[status])
    raise TypeError(arg[0])


def vtkread_STL(file_name):
    with tempfile.TemporaryDirectory() as p:
        p = pathlib.Path(p) / '.stl'
        shutil.copyfile(file_name, p)
        r = vtk.vtkSTLReader()
        r.SetFileName(str(p))
        r.Update()
        return r.GetOutput()


def vtkwrite_STL(file_name, file_type={'ASCII': vtk.VTK_ASCII,
                                       'Binary': vtk.VTK_BINARY}['Binary']):
    with tempfile.TemporaryDirectory() as p:
        p = pathlib.Path(p) / '.stl'
        w = vtk.vtkSTLWriter()
        w.SetFileName(str(p))
        w.SetFileType(file_type)
        w.Update()
        shutil.copyfile(p, file_name)


def diffEncode(text):
    return text.encode() != text.encode(locale.getdefaultlocale()[1])


def read_Medraw(file_name):
    f = QFile(file_name)
    f.open(QIODevice.ReadOnly)
    s = QDataStream(f)

    appName = s.readQString()
    appVersion = s.readQString()
    origin = [s.readDouble(), s.readDouble(), s.readDouble()]
    spacing = [s.readDouble(), s.readDouble(), s.readDouble()]
    extent = [s.readInt32(), s.readInt32(), s.readInt32(), s.readInt32(), s.readInt32(), s.readInt32()]

    shape = [extent[5] - extent[4] + 1, extent[3] - extent[2] + 1, extent[1] - extent[0] + 1]

    aryRef = np.zeros(shape)
    aryEdi = np.zeros(shape)

    for k in range(aryRef.shape[0]):
        for j in range(aryRef.shape[1]):
            for i in range(aryRef.shape[2]):
                aryRef[k][j][i] = s.readInt16()
                aryEdi[k][j][i] = s.readUInt8()

    imageRef = vmi.imVTK_Array(aryRef, origin, spacing)
    imageEdi = vmi.imVTK_Array(aryEdi, origin, spacing)
    return {'appName': appName, 'appVersion': appVersion, 'origin': origin, 'spacing': spacing, 'extent': extent,
            'aryRef': aryRef, 'aryEdi': aryEdi, 'imageRef': imageRef, 'imageEdi': imageEdi}


if __name__ == '__main__':
    v = vmi.View()
    slice = vmi.ImageSlice(v)
    slice.clone(read_Medraw(r'C:\Users\Medraw\Desktop\DICOM\公立医院膝关节-蒋敏\1.medraw')['imageEdi'])
    slice.slicePlaneAxial()
    v.cameraAxial()
    v.cameraFit()
    vmi.appexec(v)

    # with shelve.open('db', 'n', HIGHEST_PROTOCOL) as db:
    #     db['w'] = tempfile.TemporaryFile( )
