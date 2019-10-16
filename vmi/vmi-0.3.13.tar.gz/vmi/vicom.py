import os
import pathlib
import shutil
import sys
import tempfile
import threading

import SimpleITK as sitk
import pydicom
import vtk

from PySide2.QtCore import *
import vmi


def sortSeries(dcmdir, recursive=True):
    dcmdir = str(pathlib.Path(dcmdir))
    series = []

    def func():
        roots = {dcmdir}
        if recursive:
            roots = {root for root, *_ in os.walk(dcmdir)}
        for root in roots:
            with tempfile.TemporaryDirectory() as p:
                if vmi.diffEncode(root):
                    for f in os.listdir(root):
                        f = os.path.join(root, f)
                        if os.path.isfile(f):
                            shutil.copy2(f, p)
                    root = p

                for i in sitk.ImageSeriesReader.GetGDCMSeriesIDs(root):
                    filenames = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(root, i)
                    series.append(SeriesData(filenames))

    t = threading.Thread(target=func)
    t.start()
    vmi.appwait(t)
    return series


class SeriesData(QObject, vmi.Menu):
    def __init__(self, filenames=None, name=None):
        QObject.__init__(self)

        self.name = name if name else self.tr('系列 （Series)')
        vmi.Menu.__init__(self, name=self.name)

        self._Filenames = filenames
        self._Directory = tempfile.TemporaryDirectory()

        if self._Filenames and len(self._Filenames) > 0:
            self._Filenames = [shutil.copy2(f, self._Directory.name) for f in self._Filenames]

    def __setstate__(self, s):
        self.__init__(name=s['name'])
        self.__dict__.update(s)
        s = self.__dict__

        self._Filenames = []
        self._Directory = tempfile.TemporaryDirectory()
        for kw in s['_Bytes']['_Files']:
            p = pathlib.Path(self._Directory.name) / kw
            p.write_bytes(s['_Bytes']['_Files'][kw])
            self._Filenames.append(str(p))

        del s['_Bytes']

    def __getstate__(self):
        s = self.__dict__.copy()
        for kw in ['_Filenames', '_Directory', 'menu', 'actions', '__METAOBJECT__']:
            if kw in s:
                del s[kw]

        s['_Bytes'] = {'_Files': {pathlib.Path(f).name: pathlib.Path(f).read_bytes() for f in self._Filenames}}
        return s

    def __str__(self):
        with pydicom.dcmread(self._Filenames[0]) as ds:
            r = ['', '', '', '', '']
            for e in [_ for _ in ds if _.VR != 'SQ']:
                e.showVR = False
                if e.name in ['Modality', 'Slice Thickness', 'Rows', 'Columns', 'Pixel Spacing', 'Pixel Data']:
                    r[0] += repr(e) + '\n'
                elif e.name.startswith('Patient'):
                    r[1] += repr(e) + '\n'
                elif e.name.startswith('Study'):
                    r[2] += repr(e) + '\n'
                elif e.name.startswith('Series'):
                    r[3] += repr(e) + '\n'
                elif e.name.startswith('Image'):
                    r[4] += repr(e) + '\n'
            return 'slices: {}\n'.format(len(self._Filenames)) + r[0] + r[1] + r[2] + r[3] + r[4]

    def __repr__(self):
        return self.__str__()

    def filenames(self):
        return self._Filenames

    def readITK(self):
        r = sitk.ImageSeriesReader()
        r.SetFileNames(self._Filenames)
        image = r.Execute()
        return image

    def read(self):
        image = None

        def func():
            with tempfile.TemporaryDirectory() as p:
                p = pathlib.Path(p) / '.nii'

                w = sitk.ImageFileWriter()
                w.SetFileName(str(p))
                w.SetImageIO('NiftiImageIO')
                w.Execute(self.readITK())

                r = vtk.vtkNIFTIImageReader()
                r.SetFileName(str(p))
                r.Update()

                h = r.GetNIFTIHeader()

                nonlocal image
                image = r.GetOutput()
                image.SetOrigin([-h.GetQOffsetX(), -h.GetQOffsetY(), h.GetQOffsetZ()])
                image.SetSpacing([h.GetPixDim(1), h.GetPixDim(2), h.GetPixDim(3)])

        t = threading.Thread(target=func)
        t.start()
        vmi.appwait(t)
        return image
