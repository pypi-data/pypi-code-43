import locale
import pathlib
import shutil
import tempfile
import copyreg
import pickle
from typing import Dict

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


def gets_vtkInstance(instance):
    gets = {}
    for get_name in dir(instance):
        if get_name.startswith('Get'):
            set_name = get_name.replace('Get', 'Set', 1)
            if hasattr(instance, set_name) and get_name not in vtkget_ignore:
                try:
                    a = getattr(instance, get_name)()
                    if 'vtk' not in str(type(a)):  # 排除vtk类
                        gets[get_name] = a
                except TypeError:
                    pass
    return gets


def sets_vtkInstance(instance, gets):
    for get_name in gets:
        set_name = get_name.replace('Get', 'Set', 1)
        try:
            getattr(instance, set_name)(gets[get_name])
        except TypeError:
            pass


def pickle_vtkImageData(instance: vtk.vtkImageData):
    gets = gets_vtkInstance(instance)
    if instance.GetNumberOfPoints() == 0:
        data = bytes()
    else:
        with tempfile.TemporaryDirectory() as p:
            p = pathlib.Path(p) / '.nii'
            w = vtk.vtkNIFTIImageWriter()
            w.SetFileName(str(p))
            w.SetInputData(instance)
            w.Update()
            data = p.read_bytes()
    return unpickle_vtkImageData, (gets, data,)


def unpickle_vtkImageData(gets, data):
    if len(data) == 0:
        instance = vtk.vtkImageData()
    else:
        with tempfile.TemporaryDirectory() as p:
            p = pathlib.Path(p) / '.nii'
            p.write_bytes(data)
            r = vtk.vtkNIFTIImageReader()
            r.SetFileName(str(p))
            r.Update()
            instance = r.GetOutput()
    sets_vtkInstance(instance, gets)
    return instance


def pickle_vtkLookupTable(instance: vtk.vtkLookupTable):
    gets = gets_vtkInstance(instance)
    data = []
    for i in range(instance.GetNumberOfTableValues()):
        data.append(instance.GetTableValue(i))
    return unpickle_vtkLookupTable, (gets, data,)


def unpickle_vtkLookupTable(gets, data):
    instance = vtk.vtkLookupTable()
    sets_vtkInstance(instance, gets)
    instance.SetNumberOfTableValues(len(data))
    for i in range(len(data)):
        r.SetTableValue(i, data[i])
    instance.Build()
    return instance


def pickle_vtkMatrix4x4(instance: vtk.vtkMatrix4x4):
    gets = gets_vtkInstance(instance)
    data = np.zeros((4, 4))
    for j in range(4):
        for i in range(4):
            data[i, j] = instance.GetElement(j, i)
    return unpickle_vtkMatrix4x4, (gets, data,)


def unpickle_vtkMatrix4x4(gets, data):
    instance = vtk.vtkMatrix4x4()
    sets_vtkInstance(instance, gets)
    for j in range(4):
        for i in range(4):
            instance.SetElement(j, i, data[i, j])
    return instance


def pickle_vtkPolyData(instance: vtk.vtkPolyData):
    gets = gets_vtkInstance(instance)
    if instance.GetNumberOfPoints() == 0:
        data = bytes()
    else:
        with tempfile.TemporaryDirectory() as p:
            p = pathlib.Path(p) / '.vtp'
            w = vtk.vtkPolyDataWriter()
            w.SetFileTypeToBinary()
            w.SetFileName(str(p))
            w.SetInputData(instance)
            w.Update()
            data = p.read_bytes()
    return unpickle_vtkPolyData, (gets, data,)


def unpickle_vtkPolyData(gets, data):
    if len(data) == 0:
        instance = vtk.vtkPolyData()
    else:
        with tempfile.TemporaryDirectory() as p:
            p = pathlib.Path(p) / '.vtp'
            p.write_bytes(data)
            r = vtk.vtkPolyDataReader()
            r.SetFileName(str(p))
            r.Update()
            instance = r.GetOutput()
    sets_vtkInstance(instance, gets)
    return instance


copyreg.pickle(vtk.vtkImageData, pickle_vtkImageData)
copyreg.pickle(vtk.vtkMatrix4x4, pickle_vtkMatrix4x4)
copyreg.pickle(vtk.vtkPolyData, pickle_vtkPolyData)


def pickle_TopoDS_Shape(instance: TopoDS_Shape):
    if instance.IsNull():
        data = bytes()
    else:
        with tempfile.TemporaryDirectory() as p:
            p = pathlib.Path(p) / '.stp'
            w = STEPControl_Writer()
            w.Transfer(instance, STEPControl_AsIs)
            status = w.Write(str(p))
            if status == IFSelect_RetDone:
                data = p.read_bytes()
            else:
                data = bytes()
    return unpickle_TopoDS_Shape, (data,)


def unpickle_TopoDS_Shape(data):
    if len(data) == 0:
        instance = TopoDS_Shape()
    else:
        with tempfile.TemporaryDirectory() as p:
            p = pathlib.Path(p) / '.stp'
            p.write_bytes(data)
            r = STEPControl_Reader()
            status = r.ReadFile(str(p))
            if status == IFSelect_RetDone:
                r.TransferRoots()
                instance = r.OneShape()
            else:
                instance = TopoDS_Shape()
    return instance


copyreg.pickle(TopoDS_Shape, pickle_TopoDS_Shape)


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


def read_Medraw(file_name: str) -> Dict:
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
    s = vtk.vtkConeSource()
    s.Update()
    b = pickle.dumps(s.GetOutput())
    r = pickle.loads(b)
    print(r)
    # with shelve.open('db', 'n', HIGHEST_PROTOCOL) as db:
    #     db['w'] = tempfile.TemporaryFile( )
