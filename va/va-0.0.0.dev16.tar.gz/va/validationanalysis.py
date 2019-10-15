"""
validationanalysis.py

ValidationAnalysis is a class including methods for map validation
Methods:
    Orthogonal projections
    Atom and residue inclusion
    Central slice
    Map-density distribution
    Volume estimate
    FSC
    RAPS
    Largest image variance
    Memory prediction

Copyright [2013] EMBL - European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the
"License"); you may not use this file except in
compliance with the License. You may obtain a copy of
the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the
specific language governing permissions and limitations
under the License.

"""

__author__ = 'Zhe Wang'
__email__ = 'zhe@ebi.ac.uk'
__date__ = '2018-07-24'

import numpy as np
import pandas as pd
from numpy.fft import fftshift, fftn
from PIL import Image
from scipy.interpolate import RegularGridInterpolator
from collections import OrderedDict
from math import floor, ceil, log10, pi
import json, codecs
import matplotlib as mpl
import bisect
import math

mpl.use('Agg')
import matplotlib.pyplot as plt
import os, timeit, sys, glob, subprocess
from six import iteritems
from distutils.spawn import find_executable
import re
try:
    from PATHS import MAP_SERVER_PATH
    from PATHS import PROSHADEPATH
    from PATHS import MESHMAKERPATH
    from PATHS import CHIMERA
except ImportError:
    MAP_SERVER_PATH = None
    PROSHADEPATH = None
    CHIMERA = None
    MESHMAKERPATH = None

try:
    import vtk
except ImportError:
    print('ChimeraX will be used to produce for the surface view.')


##############################

# def pssum(i, dist, indiaxis, indiaxist, psmap):
#     if i != len(indiaxis) - 1:
#         indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
#
#         psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
#         return psum


# test 3

def pssum(a, indiaxis, indiaxist, shared_array):
    res = []
    for i in a:
        if i != len(indiaxis) - 1:
            indices = np.argwhere((shared_array > indiaxist[i]) & (shared_array <= indiaxist[i + 1]))
            if i == 0 or i == 1:
                print(np.ndarray.tolist(indices))
                print(len(indices[0]))
                print('indiaxist[{}]={}, indiaxist[{}+1]'.format(i, indiaxist[i], indiaxist[i+1] ))
            res.append(indices)
    return res


# def pcal(a, indiaxis, dist, indiaxist):
#     b = []
#     for i in a:
#         b.append(pssum(i, indiaxis, dist, indiaxist))
#     return b

# def pssum(lenind, psmap):
#     psum = log10(psmap.sum() / len(lenind))
#     return psum
#
# def pcal(a, allindices, allpsmap):
#     b = []
#     print('indside pcal')
#     print(len(allindices))
#     for i in a:
#
#         lenind = allindices[i]
#         psmap = allpsmap[i]
#
#         b.append(pssum(lenind, psmap))
#     return b




############################

class ValidationAnalysis:
    """
    Validation Analysis class

    """

    def __init__(self, map, model=None, pid=None, halfeven=None, halfodd=None, contourlevel=None,
                 emdid=None, dir=None, met=None, resolution=None, fscfile=None, masks=None):
        """

            Constructor function of ValidationAnalysis class

        :param map: Map instance from TEMPy package
        :param model: Model instance from TEMPy CIF file parser
        :param pid: structure id
        :param halfmap: Map instance for FSC calculation
        :param contourlevel: Float value which recommended by the author or EMDB

        """

        self.models = model
        self.map = map
        self.mapname = os.path.basename(os.path.splitext(map.filename)[0])
        self.mapname = os.path.basename(map.filename)
        self.pid = pid
        self.emdid = emdid
        self.hmeven = halfeven
        self.hmodd = halfodd
        self.met = met
        self.resolution = resolution
        self.fscfile = fscfile
        self.allmasks = masks
        if contourlevel is not None:
            self.cl = float(contourlevel)
        else:
            self.cl = contourlevel
        if self.emdid:
            digits = [i for i in str(self.emdid)]
            if len(digits) == 4:
                subdir = '{}/{}/'.format(digits[0] + digits[1], self.emdid)
                self.workdir = MAP_SERVER_PATH + subdir + 'va/'
            elif len(digits) == 5:
                subdir = '{}/{}/{}/'.format(digits[0] + digits[1], digits[2], self.emdid)
                self.workdir = MAP_SERVER_PATH + subdir + 'va/'
            else:
                pass
        else:
            self.workdir = dir



    def orthogonal_projections(self):
        """

            Produce projections images with the density map information.
            If image size larger than 300*300, output images with two sets.
            One contains original projections, the other has scaled 300*300 projections

        :return: None

        """
        start = timeit.default_timer()
        errlist = []

        mapdata = self.map.getMap()
        xprojection = np.sum(mapdata, axis=2)
        xrescaled = (((xprojection - xprojection.min()) * 255.0) / (xprojection.max() - xprojection.min())).astype(
            'uint8')
        xflipped = np.flipud(xrescaled)
        ximg = Image.fromarray(xflipped)
        try:
            ximg.save(self.workdir + self.mapname + '_xprojection.jpeg')
        except IOError as ioerr:
            xerr = 'Saving original x projection err:{}'.format(ioerr)
            errlist.append(xerr)
            sys.stderr.write(xerr + '\n')

        width, height = ximg.size
        xscalename = self.workdir + self.mapname + '_scaled_xprojection.jpeg'

        try:
            if width > 300 and height > 300:
                if width >= height:
                    largerscaler = 300. / width
                    newheight = int(ceil(largerscaler * height))
                    imx = Image.fromarray(xflipped).resize((300, newheight), Image.ANTIALIAS)
                    imx.save(xscalename)
                else:
                    largerscaler = 300. / height
                    newwidth = int(ceil(largerscaler * width))
                    imx = Image.fromarray(xflipped).resize((newwidth, 300), Image.ANTIALIAS)
                    imx.save(xscalename)
                # imx = Image.fromarray(xflipped).resize((300,300))
                # imx.save(xscalename)
            else:
                if width >= height:
                    scaler = 300. / width
                    newheight = int(ceil(scaler * height))
                    imx = Image.fromarray(xflipped).resize((300, newheight), Image.ANTIALIAS)
                    imx.save(xscalename)
                else:
                    scaler = 300. / height
                    newwidth = int(ceil(scaler * width))
                    imx = Image.fromarray(xflipped).resize((newwidth, 300), Image.ANTIALIAS)
                    imx.save(xscalename)
        except:
            xerr = 'Saving scaled x projection err:{}'.format(sys.exc_info()[1])
            errlist.append(xerr)
            sys.stderr.write(xerr + '\n')

        yprojection = np.sum(mapdata, axis=1)
        yrescaled = (((yprojection - yprojection.min()) * 255.0) / (yprojection.max() - yprojection.min())).astype(
            'uint8')
        yrotate = np.rot90(yrescaled)
        yimg = Image.fromarray(yrotate)
        try:
            yimg.save(self.workdir + self.mapname + '_yprojection.jpeg')
        except IOError as ioerr:
            yerr = 'Saving original y projection err:{}'.format(ioerr)
            errlist.append(yerr)
            sys.stderr.write(yerr + '\n')

        width, height = yimg.size
        yscalename = self.workdir + self.mapname + '_scaled_yprojection.jpeg'

        try:
            if width > 300 and height > 300:
                if width >= height:
                    largerscaler = 300. / width
                    newheight = int(ceil(largerscaler * height))
                    imy = Image.fromarray(yrotate).resize((300, newheight), Image.ANTIALIAS)
                    imy.save(yscalename)
                else:
                    largerscaler = 300. / height
                    newwidth = int(ceil(largerscaler * width))
                    imy = Image.fromarray(yrotate).resize((newwidth, 300), Image.ANTIALIAS)
                    imy.save(yscalename)
                # imy = Image.fromarray(yrotate).resize((300,300))
                # imy.save(yscalename)
            else:
                if width >= height:
                    scaler = 300. / width
                    newheight = int(ceil(scaler * height))
                    imy = Image.fromarray(yrotate).resize((300, newheight), Image.ANTIALIAS)
                    imy.save(yscalename)
                else:
                    scaler = 300. / height
                    newwidth = int(ceil(scaler * width))
                    imy = Image.fromarray(yrotate).resize((newwidth, 300), Image.ANTIALIAS)
                    imy.save(yscalename)
        except:
            yerr = 'Saving scaled y projection err:{}'.format(sys.exc_info()[1])
            errlist.append(yerr)
            sys.stderr.write(yerr + '\n')

        zprojection = np.sum(mapdata, axis=0)
        zrescaled = (((zprojection - zprojection.min()) * 255.0) / (zprojection.max() - zprojection.min())).astype(
            'uint8')
        zflipped = np.flipud(zrescaled)
        zimg = Image.fromarray(zflipped)
        try:
            zimg.save(self.workdir + self.mapname + '_zprojection.jpeg')
        except IOError as ioerr:
            zerr = 'Saving original z projection err:{}'.format(ioerr)
            errlist.append(zerr)
            sys.stderr.write(zerr + '\n')

        width, height = zimg.size
        zscalename = self.workdir + self.mapname + '_scaled_zprojection.jpeg'
        try:
            if width > 300 and height > 300:
                if width >= height:
                    largerscaler = 300./ width
                    newheight = int(ceil(largerscaler * height))
                    imz = Image.fromarray(zflipped).resize((300, newheight), Image.ANTIALIAS)
                    imz.save(zscalename)
                else:
                    largerscaler = 300./ height
                    newwidth = int(ceil(largerscaler * width))
                    imz = Image.fromarray(zflipped).resize((newwidth, 300), Image.ANTIALIAS)
                    imz.save(zscalename)
                # imz = Image.fromarray(zflipped).resize((300, 300))
                # imz.save(zscalename)
            else:
                if width >= height:
                    scaler = 300. / width
                    newheight = int(ceil(scaler * height))
                    imz = Image.fromarray(zflipped).resize((300, newheight), Image.ANTIALIAS)
                    imz.save(zscalename)
                else:
                    scaler = 300. / height
                    newwidth = int(ceil(scaler * width))
                    imz = Image.fromarray(zflipped).resize((newwidth, 300), Image.ANTIALIAS)
                    imz.save(zscalename)
        except:
            zerr = 'Saving scaled z projection err:{}'.format(sys.exc_info()[1])
            errlist.append(zerr)
            sys.stderr.write(zerr + '\n')

        projectionjson = dict()
        projectionjson['x'] = os.path.basename(xscalename) if os.path.isfile(xscalename) else None
        projectionjson['y'] = os.path.basename(yscalename) if os.path.isfile(yscalename) else None
        projectionjson['z'] = os.path.basename(zscalename) if os.path.isfile(zscalename) else None
        if errlist:
            projectionjson['err'] = {'orthogonal_projection_err': errlist}
        finaldict = {'orthogonal_projection': projectionjson}

        try:
            with codecs.open(self.workdir + self.mapname + '_projection.json', 'w',
                             encoding='utf-8') as f:
                json.dump(finaldict, f)
        except IOError as ioerr:
            jsonerr = 'Saving projection into json error: {}'.format(ioerr)
            sys.stderr.write(jsonerr + '\n')

        end = timeit.default_timer()
        print('Projections time: {}'.format(end-start))
        print('------------------------------------')

        return None

    def surfaces(self):
        """


        :return:
        """

        vtkpack, chimeraapp = self.surface_envcheck()
        if self.models is not None:
            sufcheck = [ False if model.filename.endswith('.pdb') else True for model in self.models ]
        else:
            sufcheck = [True]
        # Add if model is cif using chimera for now
        if self.cl is not None and self.met != 'tomo':
            if vtkpack and False in sufcheck:
                self.surfaceview()
            elif chimeraapp:
                self.surfaceview_chimera(chimeraapp)
                # self.modelfitsurface(chimeraapp)
            else:
                # print('No proper VTK or Chimera can be used for producing surface view. Please check.', file=sys.stderr)
                sys.stderr.write('No proper VTK or Chimera can be used for producing surface view. Please check.\n')
                print('------------------------------------')
        else:
            print('No contour level, no surface view.')

    # Surface view VTK way
    def surfaceview(self):
        """
    
            Produce surface views from X, y, Z directions. When model is there,
            model and map surface views for x, y, z directions were produced.
            This is only possible when we run on the server side as it needs
            vtp files. That means it also need the emdid to produce the 
            surface views.
    
    
        :return: None
        """
        start = timeit.default_timer()

        outmapximage = outmapyimage = outmapzimage = None
        if self.emdid is not None:
            vtproot = MAP_SERVER_PATH
            digits = [i for i in str(self.emdid)]
            if len(digits) == 4:
                vtpFile = '{}/{}/{}/va/emd_{}_{}.vtp'.format(vtproot, digits[0] + digits[1], self.emdid, self.emdid,
                                                             self.cl)
            elif len(digits) == 5:
                vtpFile = '{}/{}/{}/{}/va/emd_{}_{}.vtp'.format(vtproot, digits[0] + digits[1], digits[2], self.emdid,
                                                                self.emdid,
                                                                self.cl)
            else:
                pass
            if not os.path.isfile(vtpFile):
                print('VTP file of the map does not exist.')
                vtpFile = self.genvtp(self.map.filename)
                print('A vtp file correspond to density map is generated.')


            factGraphics = vtk.vtkGraphicsFactory()
            factGraphics.SetOffScreenOnlyMode(1)
            factGraphics.SetUseMesaClasses(1)
            reader = vtk.vtkXMLPolyDataReader()
            reader.SetFileName(vtpFile)
            reader.Update()

            mapper = vtk.vtkPolyDataMapper()
            mapper.ScalarVisibilityOff()
            mapper.SetInputConnection(reader.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(1.0, 0.8, 0.1)
            actor.GetProperty().SetInterpolationToPhong()
            actor.GetProperty().SetDiffuse(0.9)
            actor.GetProperty().SetSpecular(0.6)
            actor.GetProperty().SetSpecularPower(30)
            actor.GetProperty().BackfaceCullingOn()
            actor.GetProperty().FrontfaceCullingOn()

            # Create the graphics structure. The renderer renders into the render
            # window. The render window interactor captures mouse events and will
            # perform appropriate camera or actor manipulation depending on the
            # nature of the events.

            ren = vtk.vtkRenderer()
            renWin = vtk.vtkRenderWindow()
            renWin.SetOffScreenRendering(1)
            renWin.SetSize(3000, 3000)
            renWin.AddRenderer(ren)

            # Add the actors to the renderer, set the background and size
            # actor.RotateY(90)
            ren.AddActor(actor)
            ren.SetBackground(0.9, 0.9, 0.9)
            ren.GetActiveCamera().SetParallelProjection(1)
            renWin.Render()

            # Output maps images only
            ren.ResetCamera()
            ren.GetActiveCamera().Zoom(1.30)
            outmapzimage = '{}emd_{}_zsurface.jpeg'.format(self.workdir, self.emdid)
            self.write_image(outmapzimage, renWin)

            actor.RotateX(90)
            actor.RotateY(90)
            # ren.ResetCamera()
            outmapyimage = '{}emd_{}_ysurface.jpeg'.format(self.workdir, self.emdid)
            self.write_image(outmapyimage, renWin)

            actor.RotateZ(90)
            actor.RotateX(90)
            # ren.ResetCamera()
            outmapximage = '{}emd_{}_xsurface.jpeg'.format(self.workdir, self.emdid)
            self.write_image(outmapximage, renWin)

            # Model exist
            if self.models:
                for model in self.models:
                    pdbid = model.filename.split('/')[-1].split('.')[0]
                    # Todo: put the final decided path here as for the pdb or ent file
                    # ****: has to use .pdb or .ent for the model need to be changed to cif file
                    # pdbroot = ''
                    entroot = MAP_SERVER_PATH
                    if len(digits) == 4:
                        entFile = '{}{}/{}/va/'.format(entroot, digits[0] + digits[1], self.emdid)
                    elif len(digits) == 5:
                        entFile = '{}{}/{}/{}/va/'.format(entroot, digits[0] + digits[1], digits[2], self.emdid)
                    else:
                        pass
                    model = '{}pdb{}.ent'.format(entFile, pdbid)
                    if not os.path.isfile(model):
                        print('Model: %s is not in the working folder for model map view, please check.' % model)
                    # Change the view back
                    actor.RotateX(-90)
                    actor.RotateZ(-90)
                    actor.RotateY(-90)
                    actor.RotateX(-90)
                    ren.ResetCamera()

                    actor.GetProperty().SetOpacity(0.5)
                    pdb_reader = vtk.vtkPDBReader()
                    model_mapper = vtk.vtkPolyDataMapper()
                    model_actor = vtk.vtkActor()
                    model_actor.GetProperty().SetLineWidth(6)
                    pdb_reader.SetFileName(model)

                    # Test of backbone structure
                    # setup ribbon filter
                    ribbonFilter = vtk.vtkProteinRibbonFilter()
                    ribbonFilter.SetInputConnection(pdb_reader.GetOutputPort())
                    ribbonFilter.Update()
                    model_mapper.SetInputData(ribbonFilter.GetOutput())
                    model_mapper.Update()


                    # model_mapper.SetInputConnection(pdb_reader.GetOutputPort())
                    model_actor.SetMapper(model_mapper)
                    ren.AddActor(model_actor)
                    ren.ResetCamera()
                    ren.GetActiveCamera().Zoom(1.30)
                    renWin.Render()

                    # Output model and maps overlay images
                    outzimage = '{}{}_emd_{}_zsurface.jpeg'.format(self.workdir, pdbid, self.emdid)
                    self.write_image(outzimage, renWin)

                    actor.RotateX(90)
                    actor.RotateY(90)
                    model_actor.RotateX(90)
                    model_actor.RotateY(90)
                    # ren.ResetCamera()
                    outyimage = '{}{}_emd_{}_ysurface.jpeg'.format(self.workdir, pdbid, self.emdid)
                    self.write_image(outyimage, renWin)

                    actor.RotateZ(90)
                    actor.RotateX(90)
                    model_actor.RotateZ(90)
                    model_actor.RotateX(90)
                    # ren.ResetCamera()
                    outximage = '{}{}_emd_{}_xsurface.jpeg'.format(self.workdir, pdbid, self.emdid)
                    self.write_image(outximage, renWin)
            print('Surface views were generated by VTK method.')

            # else:
            #    # Ouput maps images only
            #    ren.ResetCamera()
            #    ren.GetActiveCamera().Zoom(0.55)
            #    outzimage = '{}{}_emd_{}_zsurface.jpeg'.format(self.workdir, pdbid, self.emdid )
            #    write_image(outzimage, renWin)

            #    actor.RotateX(90)
            #    actor.RotateY(90)
            #    #ren.ResetCamera()
            #    outyimage = '{}{}_emd_{}_ysurface.jpeg'.format(self.workdir, pdbid, self.emdid )
            #    self.write_image(outyimage, renWin)

            #    actor.RotateZ(90)
            #    actor.RotateX(90)
            #    #ren.ResetCamera()
            #    outximage = '{}{}_emd_{}_xsurface.jpeg'.format(self.workdir, pdbid, self.emdid )
            #    self.write_image(outximage, renWin)

        else:
            if self.map is not None and self.cl is not None:
                checkvtpresult = self.checkvtp()
                if checkvtpresult:
                    vtpFile = checkvtpresult
                else:
                    # First function here produce vtp file based on map with the cl
                    vtpFile = self.genvtp(self.map.filename)
                    print('A vtp file correspond to density map is generated.')

                factGraphics = vtk.vtkGraphicsFactory()
                factGraphics.SetOffScreenOnlyMode(1);
                factGraphics.SetUseMesaClasses(1)
                reader = vtk.vtkXMLPolyDataReader()
                reader.SetFileName(vtpFile)
                reader.Update()

                mapper = vtk.vtkPolyDataMapper()
                mapper.ScalarVisibilityOff()
                mapper.SetInputConnection(reader.GetOutputPort())

                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(1.0, 0.8, 0.1)
                actor.GetProperty().SetInterpolationToPhong()
                actor.GetProperty().SetDiffuse(0.9)
                actor.GetProperty().SetSpecular(0.6)
                actor.GetProperty().SetSpecularPower(30)
                actor.GetProperty().BackfaceCullingOn()
                actor.GetProperty().FrontfaceCullingOn()

                # Create the graphics structure. The renderer renders into the render
                # window. The render window interactor captures mouse events and will
                # perform appropriate camera or actor manipulation depending on the
                # nature of the events.

                ren = vtk.vtkRenderer()
                renWin = vtk.vtkRenderWindow()
                renWin.SetOffScreenRendering(1)
                renWin.SetSize(3000, 3000)
                renWin.AddRenderer(ren)

                # Add the actors to the renderer, set the background and size
                # actor.RotateY(90)
                ren.AddActor(actor)
                ren.SetBackground(0.9, 0.9, 0.9)
                ren.GetActiveCamera().SetParallelProjection(1)
                renWin.Render()

                # Ouput maps images only
                ren.ResetCamera()
                ren.GetActiveCamera().Zoom(1.30)
                outmapzimage = '{}{}_zsurface.jpeg'.format(self.workdir, self.mapname)
                self.write_image(outmapzimage, renWin)

                actor.RotateX(90)
                actor.RotateY(90)
                # ren.ResetCamera()
                outmapyimage = '{}{}_ysurface.jpeg'.format(self.workdir, self.mapname)
                self.write_image(outmapyimage, renWin)

                actor.RotateZ(90)
                actor.RotateX(90)
                # ren.ResetCamera()
                outmapximage = '{}{}_xsurface.jpeg'.format(self.workdir, self.mapname)
                self.write_image(outmapximage, renWin)

                # Model exist
                if self.models:
                    # print "self.models:%s" % self.models
                    for model in self.models:
                        pdbid = model.filename.split('/')[-1].split('.')[0]
                        pdbroot = self.workdir
                        model = '{}pdb{}.ent'.format(pdbroot, pdbid)
                        # Change the view back
                        actor.RotateX(-90)
                        actor.RotateZ(-90)
                        actor.RotateY(-90)
                        actor.RotateX(-90)
                        ren.ResetCamera()

                        actor.GetProperty().SetOpacity(0.5)
                        pdb_reader = vtk.vtkPDBReader()
                        model_mapper = vtk.vtkPolyDataMapper()
                        model_actor = vtk.vtkActor()
                        model_actor.GetProperty().SetLineWidth(6)
                        pdb_reader.SetFileName(model)

                        model_mapper.SetInputConnection(pdb_reader.GetOutputPort())
                        model_actor.SetMapper(model_mapper)
                        ren.AddActor(model_actor)
                        ren.ResetCamera()
                        ren.GetActiveCamera().Zoom(1.50)
                        renWin.Render()

                        # Output model and maps overlay images
                        outzimage = '{}{}_emd_{}_zsurface.jpeg'.format(self.workdir, pdbid, self.mapname)
                        self.write_image(outzimage, renWin)

                        actor.RotateX(90)
                        actor.RotateY(90)
                        model_actor.RotateX(90)
                        model_actor.RotateY(90)
                        # ren.ResetCamera()
                        outyimage = '{}{}_emd_{}_ysurface.jpeg'.format(self.workdir, pdbid, self.mapname)
                        self.write_image(outyimage, renWin)

                        actor.RotateZ(90)
                        actor.RotateX(90)
                        model_actor.RotateZ(90)
                        model_actor.RotateX(90)
                        # ren.ResetCamera()
                        outximage = '{}{}_emd_{}_xsurface.jpeg'.format(self.workdir, pdbid, self.mapname)
                        self.write_image(outximage, renWin)
                print('Surface views were generated by VTK method')
            elif self.cl is None:
                print('Without contour level no surface view will be produced.')

        self.scale_surfaceview()

        outzimage = '{}emd_{}_zsurface.jpeg'.format(self.workdir, self.emdid)

        surfaceviewjson = dict()
        if outmapximage:
            mapxlist = outmapximage.split('_')
            mapxscaleimage = '_'.join(mapxlist[:-1]) + '_scaled_' + mapxlist[-1]
            surfaceviewjson['x'] = os.path.basename(mapxscaleimage) if os.path.isfile(mapxscaleimage) else None
        if outmapyimage:
            mapylist = outmapyimage.split('_')
            mapyscaleimage = '_'.join(mapylist[:-1]) + '_scaled_' + mapylist[-1]
            surfaceviewjson['y'] = os.path.basename(mapyscaleimage) if os.path.isfile(mapyscaleimage) else None
        if outmapzimage:
            mapzlist = outmapzimage.split('_')
            mapzscaleimage = '_'.join(mapzlist[:-1]) + '_scaled_' + mapzlist[-1]
            surfaceviewjson['z'] = os.path.basename(mapzscaleimage) if os.path.isfile(mapzscaleimage) else None
        finaldict = {'map_surface': surfaceviewjson}

        with codecs.open(self.workdir + self.mapname + '_mapsurfaceview.json', 'w',
                         encoding='utf-8') as f:
            json.dump(finaldict, f)

        jpegs = glob.glob(self.workdir + '/*surface.jpeg')
        modelsurf = dict()
        finalmmdict = dict()
        if self.models:
            # print "self.models:%s" % self.models
            for model in self.models:
                modelname = model.filename.split('/')[-1].split('.')[0]
                modelmapsurface = dict()
                for jpeg in jpegs:
                    if modelname in jpeg and 'xsurface' in jpeg:
                        modelmapsurface['x'] = modelname + '_emd_' + self.mapname + '_scaled_xsurface.jpeg'
                    if modelname in jpeg and 'ysurface' in jpeg:
                        modelmapsurface['y'] = modelname + '_emd_' + self.mapname + '_scaled_ysurface.jpeg'
                    if modelname in jpeg and 'zsurface' in jpeg:
                        modelmapsurface['z'] = modelname + '_emd_' + self.mapname + '_scaled_zsurface.jpeg'
                modelsurf[modelname] = modelmapsurface
            finalmmdict['mapmodel_surface'] = modelsurf

            with codecs.open(self.workdir + self.mapname + '_mapmodelsurfaceview.json', 'w',
                             encoding='utf-8') as f:
                json.dump(finalmmdict, f)


        end = timeit.default_timer()
        print('Surfaceview time: {}'.format(end-start))
        print('------------------------------------')

        return None

    # For mask views
    def masks(self):
        """


        :return:
        """

        vtkpack, chimeraapp = self.surface_envcheck()
        if self.allmasks is not None:
            if chimeraapp:
                self.maskviewchimera(chimeraapp)
            elif vtkpack:
                self.maskviews()
            else:
                # print('No proper VTK or Chimera can be used for producing mask view. Please check.', file=sys.stderr)
                sys.stderr.write('No proper VTK or Chimera can be used for producing mask view. Please check.\n')
                print('------------------------------------')
        else:
            print('No masks for this entry!')

    def masksvtp(self, maskresult):
        """
           Produce vtp files for those which does not have a vtp file before
           todo: need to be changed when maskresult returned is a dictionary

        :param masks:
        :return:
        """
        masks = []

        meshmaker = False
        if MESHMAKERPATH is not None:
            meshmaker = True
            meshmakerpath = MESHMAKERPATH
        else:
            try:
                assert find_executable('meshmaker') is not None
                meshmakerpath = find_executable('meshmaker')
                meshmaker = True
            except AssertionError:
                # print('meshmaker executable is not there.', file=sys.stderr)
                sys.stderr.write('meshmaker executable is not there.\n')
            sys.stderr.write('No proper VTK or Chimera can be used for producing mask view. Please check.\n')

        if not maskresult:
            return None
        else:
            for mask in maskresult:
                # if mask.endswith('.map'):
                if mask:
                    # maskname = mask[:-4]
                    # maskvtp = maskname + '.vtp'
                    maskvtp = mask + '.vtp'
                if os.path.isfile(maskvtp):
                    masks.append(maskvtp)
                    print('Vtp file for mask: %s exist.' % maskvtp)
                else:
                    masks.append(maskvtp)
                    # Todo:Contour level for masks use 1.0 for now and will be loaded from mmcif file later
                    cmd = meshmakerpath + ' ' + mask + ' -c ' + '1.0' + ' -o ' + maskname + ' -D -v'
                    print(cmd)
                    # if self.emdid:
                    #     cmd = 'source ' + CONDAPATH + ';source activate meshmaker; meshmaker ' + mask + ' -c ' \
                    #           + '1.0' + ' -o ' + maskname + ' -D -v'
                    #     print cmd
                    # else:
                    #     cmd = 'source activate meshmaker; meshmaker ' + mask + ' -c ' \
                    #           + '1.0' + '-o ' + maskname + ' -D -v'
                    #process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
                    recode = process.wait()
                    code, error = process.communicate()
                    if recode == 0:
                        print('Produce file: %s successfully' % maskvtp)
                    else:
                        print(code, error)
            return masks


    def maskviews(self):
        """
            Generate mask views by using vtk method

        :return:
        """

        maskresult = [item for item in self.allmasks if os.path.isfile(item)]
        masksdict = dict()
        if not maskresult:
            print('There is no masks offered for this map.')
            print('------------------------------------')
        else:
            masks = self.masksvtp(maskresult)
            if masks:
                root = os.path.dirname(masks[0])
                mapvtp = '{}/{}_{}.vtp'.format(self.workdir, self.mapname, str(self.cl))
            for mask in masks:
                masksdict[mask] = self.maskviews_vtk(mapvtp, mask)
            with codecs.open(self.workdir + self.mapname + '_mapmaskview.json', 'w',
                             encoding='utf-8') as f:
                json.dump(masksdict, f)

            print('Masks view by using VTK method.')
        return None

    def maskviewchimera(self, chimeraapp):
        """
            Generate mask views by using chimera method
        :return:
        """

        start = timeit.default_timer()
        errlist = []

        maskresults = [ item for item in self.allmasks if os.path.isfile(item)]
        masksdict = dict()
        finaldict = dict()
        if not maskresults:
            print('There is no masks offered for this map.')
        else:
            # for mask in maskresults:
            for mask in self.allmasks:
                try:
                    masksdict[os.path.basename(mask)] = self.maskviews_chimera(mask, chimeraapp)
                except:
                    err = 'Saving mask {} views error: {}.'.format(mask, sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')
            if errlist:
                masksdict['err'] = {'mask_view_err': errlist}
            finaldict['masks'] = masksdict
            try:
                with codecs.open(self.workdir + self.mapname + '_mapmaskview.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(finaldict, f)
                print('Masks view by using ChimeraX method.')
            except:
                sys.stderr.write('Saving masks to json error: {}.\n'.format(sys.exc_info()[1]))

        end = timeit.default_timer()
        print('Maskview time: {}'.format(end-start))
        print('------------------------------------')
        return None

    def maskviews_vtk(self, mapvtp, maskvtp):
        """
            Using the vtk method to generate mask views

        :return:
        """

        root = os.path.dirname(maskvtp)
        maskvtpfile = maskvtp[:-4].split('/')[-1]
        mapvtp = root + '/' + self.mapname + '_' + str(self.cl) + '.vtp'


        factGraphics = vtk.vtkGraphicsFactory()
        factGraphics.SetOffScreenOnlyMode(1)
        factGraphics.SetUseMesaClasses(1)
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(mapvtp)
        reader.Update()

        # add map vtp into it
        map_reader = vtk.vtkXMLPolyDataReader()
        map_reader.SetFileName(maskvtp)
        map_mapper = vtk.vtkPolyDataMapper()
        map_mapper.ScalarVisibilityOff()
        map_mapper.SetInputConnection(map_reader.GetOutputPort())
        map_actor = vtk.vtkActor()
        map_actor.SetMapper(map_mapper)

        map_actor.GetProperty().SetColor(0.0, 0.0, 1.0)
        map_actor.GetProperty().SetInterpolationToPhong()
        map_actor.GetProperty().SetDiffuse(0.9)
        map_actor.GetProperty().SetSpecular(0.6)
        map_actor.GetProperty().SetSpecularPower(30)
        map_actor.GetProperty().BackfaceCullingOn()
        map_actor.GetProperty().FrontfaceCullingOn()
        ############

        mapper = vtk.vtkPolyDataMapper()
        mapper.ScalarVisibilityOff()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.8, 0.1)
        actor.GetProperty().SetInterpolationToPhong()
        actor.GetProperty().SetDiffuse(0.9)
        actor.GetProperty().SetSpecular(0.6)
        actor.GetProperty().SetSpecularPower(30)
        actor.GetProperty().BackfaceCullingOn()
        actor.GetProperty().FrontfaceCullingOn()
        actor.GetProperty().SetOpacity(0.5)

        # Create the graphics structure. The renderer renders into the render
        # window. The render window interactor captures mouse events and will
        # perform appropriate camera or actor manipulation depending on the
        # nature of the events.

        ren = vtk.vtkRenderer()
        renWin = vtk.vtkRenderWindow()
        renWin.SetOffScreenRendering(1)
        renWin.SetSize(3000, 3000)
        renWin.AddRenderer(ren)

        # Add the actors to the renderer, set the background and size
        # actor.RotateY(90)
        ren.AddActor(actor)
        ren.AddActor(map_actor)
        ren.SetBackground(0.9, 0.9, 0.9)
        ren.GetActiveCamera().SetParallelProjection(1)
        renWin.Render()

        # Output maps images only
        ren.ResetCamera()
        ren.GetActiveCamera().Zoom(1.30)
        outzimage = '{}{}_zmask.jpeg'.format(self.workdir, maskvtpfile)
        self.write_image(outzimage, renWin)

        actor.RotateX(90)
        actor.RotateY(90)
        map_actor.RotateX(90)
        map_actor.RotateY(90)
        # ren.ResetCamera()
        outyimage = '{}{}_ymask.jpeg'.format(self.workdir, maskvtpfile)
        self.write_image(outyimage, renWin)

        actor.RotateZ(90)
        actor.RotateX(90)
        map_actor.RotateZ(90)
        map_actor.RotateX(90)
        # ren.ResetCamera()
        outximage = '{}{}_xmask.jpeg'.format(self.workdir, maskvtpfile)
        self.write_image(outximage, renWin)
        self.scale_maskimg()

        onemaskdict = dict()
        onemaskdict['x'] = os.path.basename(outximage) if os.path.isfile(outximage) else None
        onemaskdict['y'] = os.path.basename(outyimage) if os.path.isfile(outyimage) else None
        onemaskdict['z'] = os.path.basename(outzimage) if os.path.isfile(outzimage) else None

        return onemaskdict

    def maskviews_chimera(self, mask, chimeraapp):
        """
            Generate mask view by using Chimera
            Todo: a contour level needed here for the mask

        :return:
        """

        # mapname = self.workdir + self.mapname + '.map'
        errlist = []
        mapname = self.workdir + self.mapname
        maskname = mask[:-4].split('/')[-1]
        maskfn = '{}_{}'.format(maskname, self.mapname)
        chimeracmd = maskfn + '_chimera.cxc'
        locCHIMERA = chimeraapp
        mskcl = self.allmasks[mask]
        # In case there is no mask contour level, here we use 1.0 instead
        contour = "level " + str(mskcl) if mskcl is not None else 1.0
        with open(self.workdir + chimeracmd, 'w') as f:
            f.write(
                # Chimera version
                # 'open ccp4:' + str(mapname) + '\n'
                # "open ccp4:" + str(mask) + '\n'
                # "volume #0 style surface expandSinglePlane True " + '\n'
                # "volume #1 style surface expandSinglePlane True " + '\n'
                # "volume #0 color #B8860B step 1 " + contour + '\n'
                # "volume #1 color blue step 1 level " + '1.' + '\n'
                # "set projection orthographic" + '\n'
                # "surftransp 50 #0" + '\n'  # make the surface a little bit see-through
                # "background solid light gray" + '\n'
                # "copy file " + str(maskfn) + "_zmaskview.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                # "turn x -90" + '\n'
                # "center" + '\n'
                # "copy file " + str(maskfn) + "_xmaskview.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                # "turn z -90" + '\n'
                # "center" + '\n'
                # "copy file " + str(maskfn) + "_ymaskview.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                # "close all" + "\n"
                # "exit"
                # ChimeraX version
                'open ' + str(mapname) + ' format ccp4' +'\n'
                'open ' + str(mask) + ' format ccp4' +'\n'
                "volume #1 style surface expandSinglePlane True " + '\n'
                "volume #2 style surface expandSinglePlane True " + '\n'
                "volume #1 color #B8860B step 1 level " + str(self.cl) + '\n'
                "volume #2 color blue step 1 " + contour + '\n'
                "volume #1 transparency 0.5" + '\n'
                "set bgColor light gray" + '\n'
                "view cofr True" + '\n'
                "save image " + str(maskfn) + "_zmaskview.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                "turn x -90" + '\n'
                "view cofr True" + '\n'
                "save image " + str(maskfn) + "_xmaskview.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                "turn z -90" + '\n'
                "view cofr True" + '\n'
                "save image " + str(maskfn) + "_ymaskview.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                "close all" + "\n"
                "exit"
            )
        try:
            subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmd,
                                    cwd=self.workdir, shell=True)
        except:
            subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmd, cwd=self.workdir, shell=True)

        self.scale_maskimg()


        onemaskdict = dict()
        onemaskdict['x'] = maskfn + '_scaled_xmaskview.jpeg' if os.path.isfile(self.workdir + maskfn + '_xmaskview.jpeg') else None
        onemaskdict['y'] = maskfn + '_scaled_ymaskview.jpeg' if os.path.isfile(self.workdir + maskfn + '_ymaskview.jpeg') else None
        onemaskdict['z'] = maskfn + '_scaled_zmaskview.jpeg' if os.path.isfile(self.workdir + maskfn + '_zmaskview.jpeg') else None

        return onemaskdict

    def checkvtp(self):
        """

            Check if there is a vtp file exist or not

        :return:
        """


        vtpreg = self.workdir + '*.vtp'
        globresult = glob.glob(vtpreg)
        vtpname = '{}{}_{}.vtp'.format(self.workdir, self.mapname, self.cl)
        if vtpname in globresult:
            vtpfullname = vtpname
            print('%s exist already.' % vtpname)
            return vtpfullname
        else:
            if globresult is not None:
                print('vtp file: %s exist, please check.' % globresult)
            return None

    def genvtp(self, fullmappath):
        """

            Generate vtp file for non-server input

        :param fullmappath:
        :return:
        """

        meshmaker = False
        if MESHMAKERPATH is not None:
            meshmaker = True
            meshmakerpath = MESHMAKERPATH
        else:
            try:
                assert find_executable('meshmaker') is not None
                meshmakerpath = find_executable('meshmaker')
                meshmaker = True
            except AssertionError:
                # print('meshmaker executable is not there', file=sys.stderr)
                sys.stderr.write('meshmaker executable is not there.\n')

        if meshmaker and self.cl is not None:
            outvtpname = '{}{}_{}'.format(self.workdir, self.mapname, self.cl)
            cmd = meshmakerpath + ' ' + fullmappath + ' -c ' + str(self.cl) + ' -o ' + outvtpname + ' -D -v'
            process = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
            code = process.wait()
            if code == 0:
                result = outvtpname + '.vtp'
                print('Produce file: %s successfully' % result)
                return result
            else:
                print('Meshmaker did not produce the vtp file check the inputs.')
                return None
        else:
            print('Did not find proper meshmaker or the no contour level available .')

        # meshmaker = False
        # try:
        #     assert find_executable('meshmaker') is not None
        #     meshmakerpath = find_executable('meshmaker')
        #     meshmaker = True
        # except AssertionError:
        #     print >> sys.stderr, 'meshmaker executable is not there.'
        #     print >> sys.stderr, 'Try to use the conda environment.'
        #     outvtpname = '{}{}_{}'.format(self.workdir, self.mapname, self.cl)
        #     if self.emdid:
        #         cmd = 'source ' + CONDAPATH + ';source activate meshmaker; meshmaker ' + fullmappath + ' -c ' + str(self.cl) + ' -o ' + outvtpname + ' -D -v'
        #         print cmd
        #     else:
        #         cmd = 'source activate meshmaker; meshmaker ' + fullmappath + ' -c ' + str(self.cl) + '-o ' + outvtpname + ' -D -v'
        #     process = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
        #     code = process.wait()
        #     if code == 0:
        #         result = outvtpname + '.vtp'
        #         print 'Produce file: %s successfully' % result
        #         return result
        #     else:
        #         print 'Meshmaker did not produce the vtip file check the inputs.'
        #         return None
        #
        # if meshmaker:
        #     outvtpname = '{}{}_{}'.format(self.workdir, self.mapname, self.cl)
        #     if self.emdid:
        #         cmd = 'source ' + CONDAPATH + ';source activate meshmaker; meshmaker ' + fullmappath + ' -c ' + str(self.cl) + ' -o ' + outvtpname + ' -D -v'
        #         print cmd
        #     else:
        #         cmd = 'source activate meshmaker; meshmaker ' + fullmappath + ' -c ' + str(self.cl) + '-o ' + outvtpname + ' -D -v'
        #     #cmd = [meshmakerpath, fullmappath, '-c', str(self.cl), '-o', outvtpname, '-D', '-v']
        #     process = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
        #     code = process.wait()
        #     if code == 0:
        #         result = outvtpname + '.vtp'
        #         print 'Produce file: %s successfully' % result
        #         return result
        #     else:
        #         print 'Meshmaker did not produce the vtip file check the inputs.'
        #         return None
        # else:
        #     print >> sys.stderr, 'Meshmaker is not installed. There will not any vtp files used to generate surface view.'
        #     return None

    @staticmethod
    def write_image(imageFile, renWin):
        # Write the current view of the renderer to an image
        if imageFile:
            writer = vtk.vtkBMPWriter()
            windowto_image_filter = vtk.vtkWindowToImageFilter()
            windowto_image_filter.SetInput(renWin)
            # image quality
            windowto_image_filter.SetInputBufferTypeToRGB()

            writer.SetFileName(imageFile)
            writer.SetInputConnection(windowto_image_filter.GetOutputPort())
            writer.Write()
        else:
            raise RuntimeError('Need a filename.')

    # Surface Chimera way
    def surfaceview_chimera(self, chimeraapp):
        """
            Generate surface view by using headless Chimera and pychimera

        """
        import mmap

        start = timeit.default_timer()
        errlist = []
        mmerrlist = []

        mapname = self.workdir + self.mapname
        if not os.path.isfile(mapname) and os.path.isfile(self.mapname):
            mapname = self.mapname

        locCHIMERA = chimeraapp
        contour = "level " + str(self.cl) if self.cl is not None else ''
        # map surface view alone
        mapchimeracmd = self.mapname + '_chimera.cxc'
        assemble = False
        with open(self.workdir + mapchimeracmd, 'w') as f:
            f.write(
                # Chimera version
                # 'open ccp4:' + str(mapname) + '\n'
                # "volume #0 style surface expandSinglePlane True " + '\n'
                # "volume #0 color #B8860B step 1 " + contour + '\n'
                # "set projection orthographic" + '\n'
                # "surftransp 50" + '\n'  # make the surface a little bit see-through
                # "background solid light gray" + '\n'
                # "copy file " + str(self.mapname) + "_zsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                # "turn x -90" + '\n'
                # "center" + '\n'
                # "copy file " + str(self.mapname) + "_xsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                # "turn z -90" + '\n'
                # "center" + '\n'
                # "copy file " + str(self.mapname) + "_ysurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                # "close all" + "\n"
                # "stop"

                # ChimeraX version
                "open " + str(mapname) + " format ccp4" + '\n'
                "volume #1 style surface expandSinglePlane True" + '\n'
                # "volume #1 color #B8860B step 1 level " + str(self.cl) + '\n'
                "volume #1 step 1 level " + str(self.cl) + '\n'
                "set bgColor white" + '\n'
                "lighting full \n"
                "view cofr True \n"
                "save image " + str(self.mapname) + "_zsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                "turn x -90" + '\n'
                "view cofr True" + '\n'
                "save image " + str(self.mapname) + "_xsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                "turn z -90" + '\n'
                "view cofr True" + '\n'
                "save image " + str(self.mapname) + "_ysurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                "close all" + "\n"
                "exit" + '\n'
            )
        try:
            subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + mapchimeracmd,
                                  # stdout=subprocess.STDOUT, cwd=self.workdir, shell=True)
                                    cwd=self.workdir, shell=True)
        except:
            try:
                subprocess.check_call(locCHIMERA + " " + self.workdir + mapchimeracmd, cwd=self.workdir, shell=True)
            except subprocess.CalledProcessError as suberr:
                err = 'Surface view by chimera error: {}'.format(suberr)
                errlist.append(err)
                sys.stderr.write(err + '\n')


        # map and models view together
        if self.models:
            for model in self.models:
                # pdbid = model.filename.split('/')[-1].split('.')[0]
                pdbid = os.path.basename(model.filename)
                surfacefn = '{}_{}'.format(pdbid, self.mapname)
                chimeracmd = surfacefn + '_chimera.cxc'
                with open(self.workdir + chimeracmd, 'w') as f:
                    f.write(
                        # Chimera version
                        # 'open ccp4:' + str(mapname) + '\n'
                        # "open cif:" + str(model.filename) + '\n'
                        # "volume #0 style surface expandSinglePlane True " + '\n'
                        # "volume #0 color #B8860B step 1 " + contour + '\n'
                        # "set projection orthographic" + '\n'
                        # "surftransp 50" + '\n'  # make the surface a little bit see-through
                        # "background solid light gray" + '\n'
                        # "copy file " + str(surfacefn) + "_zsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                        # "turn x -90" + '\n'
                        # "center" + '\n'
                        # "copy file " + str(surfacefn) + "_xsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                        # "turn z -90" + '\n'
                        # "center" + '\n'
                        # "copy file " + str(surfacefn) + "_ysurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                        # "close all" + "\n"
                        # "stop"

                        # ChimeraX version
                        'open ' + str(mapname) + " format ccp4" + '\n'
                        "open " + str(model.filename) + " format mmcif" + '\n'
                        "hide selAtoms" + '\n'
                        "show selAtoms ribbons" + '\n'
                        "color #2 #003BFF" + '\n'
                        "volume #1 style surface expandSinglePlane True " + '\n'
                        "volume #1 color #B8860B step 1 " + contour + '\n'
                        "volume #1 transparency 0.5" + '\n'  # make the surface a little bit see-through
                        "set bgColor light gray" + '\n'
                        "view cofr True \n"
                        "save image " + str(surfacefn) + "_zsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                        "turn x -90" + '\n'
                        "view cofr True" + '\n'
                        "save image " + str(surfacefn) + "_xsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                        "turn z -90" + '\n'
                        "view cofr True" + '\n'
                        "save image " + str(surfacefn) + "_ysurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                        "close all" + "\n"
                        "exit"

                    )
                with open(str(model.filename)) as f:
                    s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                    # python 3 mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
                    if s.find('transform to point frame') != -1:
                        assemble = True
                    else:
                        assemble = False
                chimeracmdassemble = surfacefn + '_chimera_assemble.cxc'
                if assemble:
                    with open(self.workdir + chimeracmdassemble, 'w') as f:
                        f.write(
                            # ChimeraX version
                            "open " + str(mapname) + " format ccp4" + '\n'
                            "open " + str(model.filename) + " format mmcif" + '\n'
                            "hide selAtoms" + '\n'
                            "show selAtoms ribbons" + '\n'
                            "color #2 #003BFF" + '\n'
                            "volume #1 style surface expandSinglePlane True" + '\n'
                            "volume #1 color #B8860B step 1 " + contour + '\n'
                            "volume #1 transparency 0.5" + '\n'  # make the surface a little bit see-through
                            "sym #2 assembly 1\n"
                            "set bgColor light gray" + '\n'
                            "view cofr True \n"
                            "save image " + str(self.mapname) + "_assemble_zsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "turn x -90" + '\n'
                            "view cofr True" + '\n'
                            "save image " + str(self.mapname) + "_assemble_xsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "turn z -90" + '\n'
                            "view cofr True" + '\n'
                            "save image " + str(self.mapname) + "_assemble_ysurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "close all" + "\n"
                            "exit" + '\n'
                        )



                try:
                    subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmd,
                                          cwd=self.workdir, shell=True)
                    if assemble:
                        subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmdassemble,
                                              cwd=self.workdir, shell=True)
                except:
                    try:
                        subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmd, cwd=self.workdir, shell=True)
                        if assemble:
                            subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmdassemble,
                                                  cwd=self.workdir, shell=True)
                    except subprocess.CalledProcessError as suberr:
                        err = 'Saving model {} and map err: {}'.format(str(model.filename), suberr)
                        mmerrlist.append(err)
                        sys.stderr.write(err + '\n')

        print('Surface views were generated by Chimera method')
        try:
            self.scale_surfaceview()
        except:
            err = 'Scaling the surface views err: {}'.format(sys.exc_info()[1])
            errlist.append(err)
            mmerrlist.append(err)
            sys.stderr.write(err + '\n')

        surfaceviewjson = dict()
        outmapximage = str(self.mapname) + '_xsurface.jpeg'
        mapxlist = outmapximage.split('_')
        mapxscaleimage = '_'.join(mapxlist[:-1]) + '_scaled_' + mapxlist[-1]
        surfaceviewjson['x'] = os.path.basename(mapxscaleimage) if os.path.isfile(self.workdir + mapxscaleimage) else None

        outmapyimage = str(self.mapname) + '_ysurface.jpeg'
        mapylist = outmapyimage.split('_')
        mapyscaleimage = '_'.join(mapylist[:-1]) + '_scaled_' + mapylist[-1]
        surfaceviewjson['y'] = os.path.basename(mapyscaleimage) if os.path.isfile(self.workdir + mapyscaleimage) else None

        outmapzimage = str(self.mapname) + '_zsurface.jpeg'
        mapzlist = outmapzimage.split('_')
        mapzscaleimage = '_'.join(mapzlist[:-1]) + '_scaled_' + mapzlist[-1]
        surfaceviewjson['z'] = os.path.basename(mapzscaleimage) if os.path.isfile(self.workdir + mapzscaleimage) else None
        if errlist:
            surfaceviewjson['err'] = {'map_surface_err': errlist}

        finaldict = {'map_surface': surfaceviewjson}

        try:
            with codecs.open(self.workdir + self.mapname + '_mapsurfaceview.json', 'w',
                             encoding='utf-8') as f:
                json.dump(finaldict, f)
        except:
            err = 'Saving map surface view json error: {}.'.format(sys.exc_info()[1])
            sys.stderr.write(err + '\n')

        jpegs = glob.glob(self.workdir + '/*surface.jpeg')
        modelsurf = dict()
        finalmmdict = dict()
        if self.models:
            # print "self.models:%s" % self.models
            for model in self.models:
                modelname = os.path.basename(model.filename)
                surfacefn = '{}_{}'.format(modelname, self.mapname)
                modelmapsurface = dict()
                for jpeg in jpegs:
                    if modelname in jpeg and 'xsurface' in jpeg:
                        modelmapsurface['x'] = str(surfacefn) + '_scaled_xsurface.jpeg'
                    if modelname in jpeg and 'ysurface' in jpeg:
                        modelmapsurface['y'] = str(surfacefn) + '_scaled_ysurface.jpeg'
                    if modelname in jpeg and 'zsurface' in jpeg:
                        modelmapsurface['z'] = str(surfacefn) + '_scaled_zsurface.jpeg'
            #     modelsurf[modelname] = modelmapsurface
            # if mmerrlist:
            #     modelsurf['err'] = {'mapmodel_surface_err': mmerrlist}
            # finalmmdict['mapmodel_surface'] = modelsurf
            #
            # try:
            #     with codecs.open(self.workdir + self.mapname + '_mapmodelsurfaceview.json', 'w',
            #                      encoding='utf-8') as f:
            #         json.dump(finalmmdict, f)
            # except:
            #     err = 'Saving model and map surface views json error: {}.'.format(sys.exc_info()[1])
            #     sys.stderr.write(err + '\n')

                with open(str(model.filename)) as f:
                    s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                    # python 3 mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
                    if s.find('transform to point frame') != -1:
                        assemble = True
                    else:
                        assemble = False
                assemblemapsurface = dict()
                if assemble:
                    modelname = os.path.basename(model.filename)
                    surfacefn = '{}_{}'.format(modelname, self.mapname)
                    for jpeg in jpegs:
                        if modelname in jpeg and 'xsurface' in jpeg:
                            assemblemapsurface['x_assemble'] = str(surfacefn) + '_scaled_xsurface.jpeg'
                        if modelname in jpeg and 'ysurface' in jpeg:
                            assemblemapsurface['y_assemble'] = str(surfacefn) + '_scaled_ysurface.jpeg'
                        if modelname in jpeg and 'zsurface' in jpeg:
                            assemblemapsurface['z_assemble'] = str(surfacefn) + '_scaled_zsurface.jpeg'

                mergeddict = dict(modelmapsurface, **assemblemapsurface)
                modelsurf[modelname] = mergeddict
        if mmerrlist:
            modelsurf['err'] = {'mapmodel_surface_err': mmerrlist}
        finalmmdict['mapmodel_surface'] = modelsurf

        try:
            with codecs.open(self.workdir + self.mapname + '_mapmodelsurfaceview.json', 'w',
                                encoding='utf-8') as f:
                json.dump(finalmmdict, f)
        except:
            err = 'Saving model and map surface views json error: {}.'.format(sys.exc_info()[1])
            sys.stderr.write(err + '\n')

        end = timeit.default_timer()
        print('Surfaceview time: %s' % (end - start))
        print('------------------------------------')

    def modelfitsurface(self, chimeraapp):

        # read json
        start = timeit.default_timer()
        injson = glob.glob(self.workdir + '*residue_inclusion.json')
        basedir = self.workdir
        mapname = self.mapname
        locCHIMERA = chimeraapp
        errlist = []

        fulinjson = injson[0] if injson else None

        try:
            with open(fulinjson, 'r') as f:
                args = json.load(f)
        except TypeError:
            err = 'Open residue_inclusion error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')
        else:
            if args is not None:
                models = args['residue_inclusion']
                try:
                    del models['err']
                except:
                    print('There is no error information in the residue inclusion json result.')

                print('There is/are %s model(s).' % len(models))

                for (key, value) in iteritems(models):
                    # for (key2, value2) in iteritems(value):
                    keylist = list(value)
                    for key in keylist:
                        if key != 'name':
                            colors = value[key]['color']
                            residues = value[key]['residue']
                        else:
                            modelname = value[key]
                            model = self.workdir + modelname
                            chimerafname = '{}_{}_fit_chimera.cxc'.format(modelname, mapname)
                            print(chimerafname)
                            surfacefn = '{}{}_{}'.format(basedir, modelname, mapname)
                            chimeracmd = chimerafname
                    with open(self.workdir + chimeracmd, 'w') as fp:
                        fp.write("open " + str(model) + " format mmcif" + '\n')
                        fp.write('show selAtoms ribbons' + '\n')
                        fp.write('hide selAtoms' + '\n')

                        for (color, residue) in zip(colors, residues):
                            chain, restmp = residue.split(':')
                            # Not sure if all the letters should be replaced
                            res = re.sub("\D", "", restmp)
                            fp.write(
                                'color /' + chain + ':' + res + ' ' + color + '\n'
                            )
                        fp.write(
                            "set bgColor white" + '\n'
                            "lighting soft" + '\n'
                            "view cofr True" + '\n'
                            "save image " + str(surfacefn) + "_zfitsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "turn x -90" + '\n'
                            "view cofr True" + '\n'
                            "save image " + str(surfacefn) + "_xfitsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "turn z -90" + '\n'
                            "view cofr True" + '\n'
                            "save image " + str(surfacefn) + "_yfitsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "close all" + "\n"
                            "exit"
                        )
                    try:
                        subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmd,
                                              cwd=self.workdir, shell=True)
                        print('Colored models were produced.')
                    except:
                        try:
                            subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmd, cwd=self.workdir,
                                                shell=True)
                            print('Colored models were produced.')
                        except subprocess.CalledProcessError as suberr:
                            err = 'Saving model {} fit surface view error: {}.'.format(modelname, suberr)
                            errlist.append(err)
                            sys.stderr.write(err + '\n')
                    try:
                        self.scale_surfaceview()
                    except:
                        err = 'Scaling model fit surface view error: {}.'.format(sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    jpegs = glob.glob(self.workdir + '/*surface.jpeg')
                    modelsurf = dict()
                    finalmmdict = dict()
                    if self.models:
                        # print "self.models:%s" % self.models
                        for model in self.models:
                            modelname = os.path.basename(model.filename)
                            surfacefn = '{}_{}'.format(modelname, self.mapname)
                            modelmapsurface = dict()
                            for jpeg in jpegs:
                                if modelname in jpeg and 'xfitsurface' in jpeg:
                                    modelmapsurface['x'] = str(surfacefn) + '_scaled_xfitsurface.jpeg'
                                if modelname in jpeg and 'yfitsurface' in jpeg:
                                    modelmapsurface['y'] = str(surfacefn) + '_scaled_yfitsurface.jpeg'
                                if modelname in jpeg and 'zfitsurface' in jpeg:
                                    modelmapsurface['z'] = str(surfacefn) + '_scaled_zfitsurface.jpeg'
                            if errlist:
                                modelmapsurface['err'] = {'model_fit_err': errlist}
                            modelsurf[modelname] = modelmapsurface
                        finalmmdict['modelfit_surface'] = modelsurf

                        try:
                            with codecs.open(self.workdir + self.mapname + '_modelfitsurfaceview.json', 'w',
                                             encoding='utf-8') as f:
                                json.dump(finalmmdict, f)
                        except:
                            sys.stderr.write('Saving model fit surface view to json error: {}.\n'.format(sys.exc_info()[1]))

                end = timeit.default_timer()
                print('Modelfitsurface time: %s' % (end - start))
                print('------------------------------------')





    def scale_surfaceview(self):
        """
            Scale the surface view images size to 300X300

        :return: None
        """

        # import imageio
        import glob

        for imgfile in glob.glob(self.workdir + '*surface.jpeg'):
            if 'scaled' not in imgfile:
                namelist = imgfile.split('/')[-1].split('_')
                nameone = '_'.join(namelist[:-1])
                nametwo = namelist[-1]
                # npimg = imageio.imread(imgfile)
                npimg = Image.open(imgfile)
                # zoomimg = self.zoomin(npimg, 1.00)
                # im = Image.fromarray(zoomimg).resize((300, 300))
                im = npimg.resize((300, 300))
                im.save(self.workdir + nameone + '_scaled_' + nametwo)

        return None

    def scale_maskimg(self):
        """

        :return: None
        """

        # import imageio
        import glob

        for imgfile in glob.glob(self.workdir + '*maskview.jpeg'):
            if 'scaled' not in imgfile:
                namelist = imgfile.split('/')[-1].split('_')
                nameone = '_'.join(namelist[:-1])
                nametwo = namelist[-1]
                # npimg = imageio.imread(imgfile)
                npimg = Image.open(imgfile)
                # zoomimg = self.zoomin(npimg, 1.00)
                # im = Image.fromarray(zoomimg).resize((300, 300))
                im = npimg.resize((300, 300))
                im.save(self.workdir + nameone + '_scaled_' + nametwo)

        return None


    def zoomin(self,img, factor, **kwargs):
        """
            Zoom in to the surface view images
        :param img: img object of input
        :return:
        """
        from scipy.ndimage import zoom

        h, w = img.shape[:2]
        zoom_tuple = (factor,) * 2 + (1,) * (img.ndim - 2)
        if factor != 1.:
            # Bounding box of the zoomed-in region within the input array
            zh = int(np.round(h / factor))
            zw = int(np.round(w / factor))
            top = (h - zh) // 2
            left = (w - zw) // 2

            out = zoom(img[top:top + zh, left:left + zw], zoom_tuple, **kwargs)
            trim_top = ((out.shape[0] - h) // 2)
            trim_left = ((out.shape[1] - w) // 2)
            out = out[trim_top:trim_top + h, trim_left:trim_left + w]

        # If factor == 1, just return the input array
        else:
            out = img

        return out

    @staticmethod
    def surface_envcheck():
        """

            Check the running environment for surface view.
            If the machine is headless, remind the user vtk or Chimera have to be build in the headless way.
            If vtk can not imported, try use Chimera.

        :return: tuple of vtkpack and chimeraapp binary value
        """

        display = os.getenv('DISPLAY')
        if display is None:
            print('You may running this program on a headless machine. Please make sure either headless VTK or headless' \
                  'Chimera are properly installed accordingly.')

        vtkpack = False
        chimeraapp = False
        try:
            import vtk
            vtkpack = True
        except ImportError:
            # print('VTK is not installed or imported properly. Trying to use Chimera to produce surface views.', file=sys.stderr)
            sys.stderr.write('VTK is not installed or imported properly. Trying to use Chimera to produce surface views.\n')

        try:
            if CHIMERA is not None:
                chimeraapp = CHIMERA
                print(chimeraapp)
            else:
                assert find_executable('ChimeraX') is not None
                chimeraapp = find_executable('ChimeraX')
                print(chimeraapp)
        except AssertionError:
            # print('Chimera executable is not there.', file=sys.stderr)
            sys.stderr.write('ChimeraX executable is not there.\n')

        return vtkpack, chimeraapp

    # Density distribution
    def density_distribution(self):
        """

            Produce density value distribution information with the density map information.
            x was divided into 128 bins
            y was scaled by logarithmic 10 (for 0 value add 1 to igonre artifacts)

        :param: None
        :return: None

        """

        start = timeit.default_timer()
        bins = 128
        errlist = []
        datadict = {}
        try:
            mapdata = self.map.getMap()
            flatmap = mapdata.flatten()
            bins = np.linspace(min(flatmap), max(flatmap), 128)
            hist, bin_edges = np.histogram(flatmap, bins=bins)
            hist[hist < 1] = 1
            newhist = np.log10(hist)

            # plt.plot(np.round(bin_edges[:-1], 10).tolist(), np.round(newhist, 10).tolist())
            # plt.savefig('test.png')

            datadict = {
                'density_distribution': {'y': np.round(newhist, 10).tolist(), 'x': np.round(bin_edges[:-1], 10).tolist()}}
        except:
            err = 'Density distribution error:{}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')

        if errlist:
            datadict = {'density_distribution': {'err': {'density_distribution_error': errlist}}}

        try:
            with codecs.open(self.workdir + self.mapname + '_density_distribution.json', 'w',
                             encoding='utf-8') as f:
                json.dump(datadict, f)
        except:
            sys.stderr.write('Saving denisty distribution to json error.')

        end = timeit.default_timer()
        print('Density distribution time: %s' % (end - start))
        print('------------------------------------')

        return None

    # Atom and residue includsion
    @staticmethod
    def __floatohex(numlist):
        """

            Produce hex color between red and green

        :param numlist: A list of RGB values
        :return: A list of hex value between R and G with B = 0

        """

        # rgbs = [[int((1 - num) * 255), int(num * 255), 0] for num in numlist]
        # rgbs = [[int((1 - num) * 255)*0.5, 120, int(num * 255)*0.5] for num in numlist]
        rgbs = [[122, int((num) * 255), int(num * 255)] for num in numlist]
        resultlist = []
        resultlist = ['#%02X%02X%02X' % (rgb[0], rgb[1], rgb[2]) for rgb in rgbs]
        # for rgb in rgbs:
        #    result = '#%02X%02X%02X' % (rgb[0], rgb[1], rgb[2])
        #    resultlist.append(result)

        return resultlist

    def __interPolation(self):
        """

            Usc scipy regulargrid interpolation method feed with all maps info

        :param map: Electron density map in mrc/map format
        :param model: Protein model in mmcif format
        :return: A interpolation function

        """

        mapdata = self.map.getMap()
        tmpmapdata = np.swapaxes(mapdata, 0, 2)
        clim, blim, alim = mapdata.shape
        x = range(alim)
        y = range(blim)
        z = range(clim)
        myinter = RegularGridInterpolator((x, y, z), tmpmapdata)

        return myinter

    def __interthird(self):
        """

            Interpolate density value of one atom, if indices are on the same plane use nearest method
            otherwise use linear

        :param map: TEMPy map instance
        :param model: Structure instance from TEMPy package mmcif parser
        :return: List contains all density interpolations of atoms from model

        """

        myinter = self.__interPolation()
        # Might having multple models
        models = []
        if isinstance(self.models, list):
            models = self.models
        else:
            models.append(self.models)
        map = self.map
        contour = self.cl
        # Range of contour level values for scaler bar
        # Todo: Right now with fixed number of points on both sides of the recommended contour level, could improve to
        # Todo: generate a reasonable range surround the recommended contour level
        # Setting a smarter range between (contour-sig,contour, countour + sig)
        mapsig = map.std()
        # contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # contourrange = np.concatenate((np.linspace(map.min(), contour, 3, endpoint=False), np.linspace(contour, map.max(), 3)), axis=None)
        # When running for EMDB keep it as a flexible range for onedep or other users only run it once for recommended
        # contour level:

        # if self.emdid:
        #     contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                    np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # else:
        #     contourrange = np.asarray([contour])

        contourrange = np.asarray([contour])
        result = {}
        for model in models:
            allcontoursdict = OrderedDict()
            atomoutsidenum = 0
            modelname = model.filename.split('/')[-1]
            for contour in contourrange:
                interpolations = []
                allkeys = []
                allvalues = []
                preresid = 0
                prechain = ''
                preres = ''
                rescount = 0
                sumatominterbin = 0
                for atom in model:
                    # if 'H' not in atom.atom_name:
                    onecoor = [atom.x, atom.y, atom.z]
                    oneindex = self.__getindices(onecoor)[1]
                    if oneindex[0] > map.x_size() - 1 or oneindex[0] < 0 or \
                            oneindex[1] > map.y_size() - 1 or oneindex[1] < 0 or \
                            oneindex[2] > map.z_size() - 1 or oneindex[2] < 0:
                        curinterpolation = map.min()
                        atomoutsidenum += 1
                    else:
                        curinterpolation = myinter(oneindex).tolist()[0]
                    interpolations.append(curinterpolation)
                    atominterbin = 1 if curinterpolation > contour else 0
                    if (rescount == 0) or (atom.res_no == preresid and atom.chain == prechain):
                        sumatominterbin += atominterbin
                        rescount += 1
                        preresid = atom.res_no
                        prechain = atom.chain
                        preres = atom.res

                    else:
                        keystr = prechain + ':' + str(preresid) + preres
                        allkeys.append(keystr)
                        # value = float(sumatominterbin)/rescount
                        value = float('%.4f' % round((float(sumatominterbin) / rescount), 4))
                        allvalues.append(value)
                        sumatominterbin = atominterbin
                        preresid = atom.res_no
                        prechain = atom.chain
                        rescount = 1

                keystr = prechain + ':' + str(preresid) + preres
                allkeys.append(keystr)
                value = float('%.4f' % round((float(sumatominterbin) / rescount), 4))
                allvalues.append(value)
                allcontoursdict[str(contour)] = (allkeys, allvalues)
                print('Model: %s at contour level %s has %s atoms stick out of the density.' % (modelname, contour,
                                                                                                 atomoutsidenum))

            # result[modelname] = (interpolations, allkeys, allvalues)
            # result: {modelname #1: (interpolations #1, {contour1: (allkeys, allvalues), contour2: (allkeys, allvalues)
            # ...}), modelname #2: (interpolations #2, {contour1: (allkeys, allvalues),...}),...}
            result[modelname] = (interpolations, allcontoursdict)

        return result


    def map_matrix(self, apixs, angs):
        """

            calculate the matrix to transform Cartesian coordinates to fractional coordinates
            (check the definination to see the matrix formular)

        :param apixs: array of apix lenght
        :param angs: array of anglex in alpha, beta, gamma order
        :return:
        """

        ang = (angs[0]*math.pi/180, angs[1]*math.pi/180, angs[2]*math.pi/180)
        insidesqrt = 1 + 2 * math.cos(ang[0]) * math.cos(ang[1]) * math.cos(ang[2]) - \
                     math.cos(ang[0])**2 - \
                     math.cos(ang[1])**2 - \
                     math.cos(ang[2])**2

        cellvolume = apixs[0]*apixs[1]*apixs[2]*math.sqrt(insidesqrt)

        m11 = 1/apixs[0]
        m12 = -math.cos(ang[2])/(apixs[0]*math.sin(ang[2]))

        m13 = apixs[1] * apixs[2] * (math.cos(ang[0]) * math.cos(ang[2]) - math.cos(ang[1])) / (cellvolume * math.sin(ang[2]))
        m21 = 0
        m22 = 1 / (apixs[1] * math.sin(ang[2]))
        m23 = apixs[0] * apixs[2] * (math.cos(ang[1]) * math.cos(ang[2]) - math.cos(ang[0])) / (cellvolume * math.sin(ang[2]))
        m31 = 0
        m32 = 0
        m33 = apixs[0] * apixs[1] * math.sin(ang[2]) / cellvolume
        prematrix = [[m11, m12, m13], [m21, m22, m23], [m31, m32, m33]]
        matrix = np.asarray(prematrix)

        return matrix


    def matrix_indices(self, apixs, onecoor):
        """

            Method 2: using the fractional coordinate matrix to calculate the indices when the maps are non-orthogonal

        :return:
        """

        # Method 2: by using the fractional coordinate matrix
        # Chosen as the main function for the current implementation

        # Figure out the order of the x, y, z based on crs info in the header
        crs = list(self.map.header[16:19])
        # ordinds save the indices correspoding to x, y ,z
        ordinds = [crs.index(1), crs.index(2), crs.index(3)]
        angs = self.map.header[13:16]
        matrix = self.map_matrix(apixs, angs)
        result = matrix.dot(np.asarray(onecoor))
        xindex = result[0] - self.map.header[4 + ordinds[0]]
        yindex = result[1] - self.map.header[4 + ordinds[1]]
        zindex = result[2] - self.map.header[4 + ordinds[2]]

        return (xindex, yindex, zindex)



    def projection_indices(self, onecoor):
        """

            Method 1: using the projection way to calculate the indices when the maps are non-orthogonal

        :return: tumple which contains all three float new indices in (x, y, z) order
        """

        map = self.map
        zdim = map.header[12]
        znintervals = map.header[9]
        z_apix = zdim / znintervals

        ydim = map.header[11]
        ynintervals = map.header[8]
        y_apix = ydim / ynintervals

        xdim = map.header[10]
        xnintervals = map.header[7]
        x_apix = xdim / xnintervals

        theta = (map.header[13] / 90) * (math.pi / 2)
        beta = (map.header[14] / 90) * (math.pi / 2)
        gamma = (map.header[15] / 90) * (math.pi / 2)

        insidesqrt = 1 + 2 * math.cos(theta) * math.cos(beta) * math.cos(gamma) - \
                     math.cos(theta) * math.cos(theta) - \
                     math.cos(beta) * math.cos(beta) - \
                     math.cos(gamma) * math.cos(gamma)

        cellvolume = x_apix * y_apix * z_apix * math.sqrt(insidesqrt)

        cellheightz = cellvolume / (x_apix * y_apix * math.sin(gamma))
        cellheighty = cellvolume / (x_apix * z_apix * math.sin(beta))
        cellheightx = cellvolume / (z_apix * y_apix * math.sin(theta))

        # Figure out the order of the x, y, z based on crs info in the header
        crs = list(map.header[16:19])
        # ordinds save the indices correspoding to x, y ,z
        ordinds = [crs.index(1), crs.index(2), crs.index(3)]

        # Trying to move the atom coordinate which has not work yet

        # move the coordinate according to move of the map
        # x: c*cos(gamma) + b + a*cos(beta)
        # y: c*sin(gamma) + sqrt(a**2 - (a*cos(beta))**2 - cellhz**2)
        # z: hz
        # a = math.fabs(map.header[4 + ordinds[2]]*z_apix)
        # b = math.fabs(map.header[4 + ordinds[0]]*x_apix)
        # c = math.fabs(map.header[4 + ordinds[1]]*y_apix)
        # # for 8720 seems correct
        # # xshift = c*math.cos(gamma) + b - a*math.cos(beta)
        # # yshift = c*math.sin(gamma)
        # # zshift = (-1)*map.header[4 + ordinds[2]]*cellheightz
        # for 8765 correct
        # xshift = c*math.cos(gamma) + b - a*math.cos(beta)
        # yshift = c*math.sin(gamma)
        # zshift = (-1)*map.header[4 + ordinds[2]]*cellheightz
        # print('---shift---')
        # print(xshift)
        # print(yshift)
        # print(zshift)
        # print(c*math.sin(gamma))
        # print(c)
        # print(math.radians(gamma))
        # print(gamma)
        # print(c*math.cos(gamma))
        # print(b)
        # print(a*math.cos(beta))
        # print(map.header[4 + ordinds[2]])

        # Mehtod 1: Calculateing the distances from the atom to different planes(x'y', x'z', y'z') and divided by
        # The unit cell height(calculated by using unit cell volume divided by the plane surface area) to get the
        # indices, then deduct the origin index which give the final results. When calculating the sign of the
        # distance, find a plane parallel to the projection plane and it pass through the atom, the cutoff of this
        # plane and the correspoding axis give the location of the atom projection cutoff at the axis
        # (this should also be able to used to calculate the final indices(not tried)). If this point is outside
        # the normal cell dimension range, then the distance should be negative and vice verse
        relativex = onecoor[0] - map.header[49]
        relativey = onecoor[1] - map.header[50]
        relativez = onecoor[2] - map.header[51]

        # Z index by using the relativez / cellheightz
        zind = relativez / cellheightz
        zindex = zind - map.header[4 + ordinds[2]]

        # X index by calculating the plane first and then calculate the distance from atom to plane
        # Plane x'z'
        # Ax + By + Cz + D = 0 with three data points: (0, 0, 0), (b, 0, 0),
        # (a*cos(alpha), sqrt(a**2 - (celllhz)**2 - (a*cos(alpha)**2), cellhz), x' unit cell length is b, alpha is
        # the angle between x' and z'(which are the cell axes)
        # By using these three points the plane of x'z' can be calculated
        # A=0, B=cellhz, C = -sqrt(a**2 - (cellhz)**2 - (a*cos(alpha))**2), D=0
        A = 0
        B = cellheightz
        C = -math.sqrt(z_apix ** 2 - cellheightz ** 2 - (z_apix * math.cos(beta)) ** 2)
        D = 0

        # distance from atom to x'z' plane:
        #         |Ax + By + Cz + D|
        # d = -----------------------------
        #       sqrt(A**2 + B**2 + C**2)
        dy = math.fabs(B * relativey + C * relativez) / math.sqrt(A ** 2 + B ** 2 + C ** 2)

        # The parallel plan which pass the atom and intersect with the x is:
        # Ax) + B(y + a) + Cz + D = 0
        # a = -(Ax + By + Cz + D)/A
        # xcut = -a
        ycut = -(A * onecoor[0] + onecoor[1] + (C / B) * onecoor[2])
        ycut = -ycut
        if ycut < 0 or ycut > map.header[0 + ordinds[1]] * y_apix * math.sin(gamma):
            dy = -dy

        yind = dy / cellheighty
        yindex = yind - map.header[4 + ordinds[1]]

        # Plane z'y'
        # Ax + By + Cz + D = 0 with three data points: (0, 0, 0), (a*cos(alpha),
        # sqrt(a**2 - (cellhz)**2 - (a*cos(alpha)**2), cellhz),
        # (d*cos(gamma), d*sin(gamma), 0)
        # beta is the angle between x' and z'; gamma is the angle between x' and y'; d is the cell unit length
        # along y'
        # Using these three points a plane can be calculated
        # A=-tg(beta), B = 1, D=0,
        #      a*cos(alpha)*tg(beta) - t
        # C = --------------------------- ,     t = sqrt(a**2 - (cellhz)**2 - (a*cos(alpha))**2)
        #            cellhz
        # A = -math.tan(gamma)
        # B = 1
        # D = 0
        # t = math.sqrt(z_apix**2 - cellheightz**2 - (z_apix*math.cos(beta))**2)
        # C = (z_apix * math.cos(beta)*math.tan(gamma) - t) / cellheightz

        if map.header[15] == 90.:
            singamma = 1.
            cosgamma = 0.
        else:
            singamma = math.sin(gamma)
            cosgamma = math.cos(gamma)

        if map.header[14] == 90.:
            singbeta = 1.
            cosbeta = 0.
        else:
            sinbeta = math.sin(beta)
            cosbeta = math.cos(beta)

        A = -singamma
        B = cosgamma
        D = 0
        t = math.sqrt(z_apix ** 2 - cellheightz ** 2 - (z_apix * cosbeta) ** 2)
        C = (z_apix * cosbeta * singamma - t * cosgamma) / cellheightz

        # distance from atom to z'y' plane:
        #         |Ax + By + Cz + D|
        # d = -----------------------------
        #       sqrt(A**2 + B**2 + C**2)
        dx = math.fabs(A * relativex + B * relativey + C * relativez) / math.sqrt(A ** 2 + B ** 2 + C ** 2)
        xcut = (-(onecoor[0] + (B / A) * onecoor[1] + (C / A) * onecoor[2]))
        xcut = -xcut
        if xcut < 0 or xcut > map.header[0 + ordinds[0]] * x_apix:
            dx = -dx
        xind = dx / cellheightx
        xindex = xind - map.header[4 + ordinds[0]]


        return(xindex, yindex, zindex)


    def __getindices(self, onecoor):
        """

            Find one atom's indices correspoding to its cubic or plane
            the 8 (cubic) or 4 (plane) indices are saved in indices variable

        :param map: Density map instance from TEMPy.MapParser
        :param onecoor: List contains the atom coordinates in (x, y, z) order
        :return: Tuple contains two list of index: first has the 8 or 4 indices in the cubic;
                 second has the float index of the input atom

        """

        # For non-cubic or skewed density maps, they might have different apix on different axises
        map = self.map
        zdim = map.header[12]
        znintervals = map.header[9]
        z_apix = zdim / znintervals

        ydim = map.header[11]
        ynintervals = map.header[8]
        y_apix = ydim / ynintervals

        xdim = map.header[10]
        xnintervals = map.header[7]
        x_apix = xdim / xnintervals

        if map.header[13] == map.header[14] == map.header[15] == 90.:
            # Figure out the order of the x, y, z based on crs info in the header
            crs = list(map.header[16:19])
            # ordinds save the indices correspoding to x, y ,z
            ordinds = [crs.index(1), crs.index(2), crs.index(3)]

            zindex = float(onecoor[2] - map.header[51]) / z_apix - map.header[4 + ordinds[2]]
            yindex = float(onecoor[1] - map.header[50]) / y_apix - map.header[4 + ordinds[1]]
            xindex = float(onecoor[0] - map.header[49]) / x_apix - map.header[4 + ordinds[0]]

            zfloor = int(floor(zindex))
            if zfloor >= map.z_size() - 1:
                zceil = zfloor
            else:
                zceil = zfloor + 1

            yfloor = int(floor(yindex))
            if yfloor >= map.y_size() - 1:
                yceil = yfloor
            else:
                yceil = yfloor + 1

            xfloor = int(floor(xindex))
            if xfloor >= map.x_size() - 1:
                xceil = xfloor
            else:
                xceil = xfloor + 1
        else:
            # Method 2: by using the fractional coordinate matrix
            # Chosen as the primary for the current implementation
            apixs = [x_apix, y_apix, z_apix]
            # Method 1: by using the atom projection on planes
            # xindex, yindex, zindex = self.projection_indices(onecoor))
            xindex, yindex, zindex = self.matrix_indices(apixs, onecoor)

            zfloor = int(floor(zindex))
            if zfloor >= map.z_size() - 1:
                zceil = zfloor
            else:
                zceil = zfloor + 1

            yfloor = int(floor(yindex))
            if yfloor >= map.y_size() - 1:
                yceil = yfloor
            else:
                yceil = yfloor + 1

            xfloor = int(floor(xindex))
            if xfloor >= map.x_size() - 1:
                xceil = xfloor
            else:
                xceil = xfloor + 1

        indices = np.array(np.meshgrid(np.arange(xfloor, xceil + 1), np.arange(yfloor, yceil + 1),
                                       np.arange(zfloor, zceil + 1))).T.reshape(-1, 3)
        oneindex = [xindex, yindex, zindex]

        return (indices, oneindex)

    def __getfractions(self, interpolation, model):
        """

            Produce atom inclusion fraction information for full atoms and backbone trace

        :param interpolation: List of interpolation values
        :param map: Electron density map in mrc/map format
        :param model: Protein model in mmcif format
        :return: Tuple contains full atom inclusion fractions and backbone inclusion fractions

        """

        map = self.map
        bins = np.linspace(map.min(), map.max(), 129)
        binlist = bins.tolist()
        bisect.insort(binlist, self.cl)
        clindex = binlist.index(self.cl)
        binlist.pop(clindex - 1)
        bins = np.asarray(binlist)

        newinterpolation = []
        for i in range(len(interpolation)):
            if 'H' not in model[i].atom_name:
                newinterpolation.append(interpolation[i])

        hist, bin_edges = np.histogram(newinterpolation, bins=bins)
        # hist = np.hstack((hist[0], hist))
        # append 0 value to the end of the list to make it the same length as the length of data points
        hist = np.append(hist, 0.)
        # Full atom includsion
        cumusum = 0
        a = []
        natom = len(interpolation)

        for i in range(len(hist)):
            cumusum += hist[i]
            fractions = (1 - float(cumusum) / natom)
            a.append(fractions)

        traceinter = []
        for i in range(len(interpolation)):
            if (model[i].atom_name == 'N' or model[i].atom_name == 'C' or model[i].atom_name == 'O' or
                    model[i].atom_name == 'CA' or model[i].atom_name == "C3'" or model[i].atom_name == "C4'" or
                    model[i].atom_name == "C5'" or model[i].atom_name == "O3'" or model[i].atom_name == "O5'" or
                    model[i].atom_name == 'P' or model[i].atom_name == 'OXT'):
                traceinter.append(interpolation[i])

        # Backbone inclusion

        tracehist, trace_binedges = np.histogram(traceinter, bins=bins)
        tracenatom = len(traceinter)
        tracehist = np.append(tracehist, 0.)
        tracecumsum = 0
        b = []
        for j in range(len(tracehist)):
            tracecumsum += tracehist[j]
            tracefractions = (1 - float(tracecumsum) / tracenatom)
            b.append(tracefractions)

        return a, b

    def atom_inclusion(self):
        """

            Generate atom inclusion and residue atom inclusion information verses different contour level
            Both full atoms and backbone information are included.
            Results wrote to JSON file

        :return: None

        """
        if self.models is None:
            # print('REMINDER: atom inclusion and residue inclusion will not be calculated without model structure.',
            #       file=sys.stderr)
            sys.stderr.write('REMINDER: atom inclusion and residue inclusion will not be calculated without '
                             'model structure.\n')
            print('------------------------------------')
        elif self.cl is None:
            # print('REMINDER: atom inclusion and residue inclusion will not be calculated without contour level given '
            #       'by "-cl".', file=sys.stderr)
            sys.stderr.write('REMINDER: atom inclusion and residue inclusion will not be calculated '
                             'without contour level given.\n')
            print('------------------------------------')
        else:
            start = timeit.default_timer()
            map = self.map

            # modelnames = [ model.filename for model in self.models ]
            combinresult = self.__interthird()
            atomindict = OrderedDict()
            resindict = OrderedDict()
            datadict = OrderedDict()
            resdict = OrderedDict()
            counter = 0
            errlist = []
            reserrlist = []
            for key, value in combinresult.items():
                try:
                    # interpolations, allkeys, allvalues = self.__interthird()
                    # interpolations, allkeys, allvalues = value
                    interpolations, allcontoursdict = value
                    if isinstance(self.models, list):
                        models = [curmodel for curmodel in self.models if key in curmodel.filename]
                    else:
                        models = list()
                        models.append(self.models)

                    if len(models) == 1:
                        model = models[0]
                    elif len(models) == 0:
                        print('There is no model!')
                        exit()
                    else:
                        print('There are more than one model which should be only one.')
                        exit()

                    result = self.__getfractions(interpolations, model)
                    levels = np.linspace(map.min(), map.max(), 129)

                    binlist = levels.tolist()
                    bisect.insort(binlist, self.cl)
                    clindex = binlist.index(self.cl)
                    binlist.pop(clindex - 1)
                    levels = np.asarray(binlist)

                    datadict[str(counter)] = {'name': key, 'level': [round(elem, 10) for elem in levels.tolist()],
                                              'all_atom': [round(elem, 10) for elem in result[0]],
                                              'backbone': [round(elem, 10) for elem in result[1]]}

                    # plt.plot([round(elem, 10) for elem in levels.tolist()], [round(elem, 10) for elem in result[0]])
                    # plt.plot([round(elem, 10) for elem in levels.tolist()], [round(elem, 10) for elem in result[1]])
                    # plt.savefig('test.png')
                    # exit()
                except:
                    err = 'Atom inclusion calculation error(Model: {}): {}.'.format(key, sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')
                if errlist:
                    datadict[str(counter)] = {'err': {'atom_inclusion_err': errlist}}

                contourdict = OrderedDict()
                try:
                    for contour, keysvalues in allcontoursdict.items():
                        allvalues = keysvalues[1]
                        allkeys = keysvalues[0]
                        colours = self.__floatohex(allvalues)
                        contourkey = str(round(float(contour), 10))
                        contourdict[contourkey] = OrderedDict([('color', colours), ('inclusion', allvalues),
                                                               ('residue', allkeys)])

                    contourdict['name'] = key
                    resdict[str(counter)] = contourdict
                except:
                    err = 'Residue inclusion calculation error(Model: {}): {}.'.format(key, sys.exc_info()[1])
                    reserrlist.append(err)
                    sys.stderr.write(err + '\n')
                if reserrlist:
                    resdict[str(counter)] = {'err': {'residue_inclusion_err': reserrlist}}
                counter += 1

            # datadict['err'] = {'atom_inclusion_err': errlist}
            atomindict['atom_inclusion_by_level'] = datadict
            # resdict['err'] = {'residue_inclusion_err': errlist}
            resindict['residue_inclusion'] = resdict

            try:
                with codecs.open(self.workdir + self.mapname + '_atom_inclusion.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(atomindict, f)
            except:
                sys.stderr.write('Saving to atom inclusion json error: {}.\n'.format(sys.exc_info()[1]))

            try:
                with codecs.open(self.workdir + self.mapname + '_residue_inclusion.json', 'w',
                                 encoding='utf-8') as f1:
                    json.dump(resindict, f1)
            except:
                sys.stderr.write('Saving to residue inclusion json error: {}.\n'.format(sys.exc_info()[1]))



            end = timeit.default_timer()
            print('Inclusion time: %s' % (end - start))
            print('------------------------------------')
        return None

    # Volumecontour

    def volumecontour(self):
        """

            Generate Volume versus contour level plot.
            Result wrote to a JSON file.
            View indices as siting on the central of each voxel, no interpolation needed.

        :return: None

        """

        start = timeit.default_timer()
        map = self.map
        # temprary solution as the tempy give apix as one value but here from mrcfile we use a tuple
        # check functionn frommrc_totempy in preparation.py
        apix = map.apix
        mapdata = map.getMap()
        errlist = []
        datadict = dict()
        try:
            bins = np.linspace(mapdata.min(), mapdata.max(), 129)
            hist, bin_edges = np.histogram(mapdata, bins=bins)
            preresult = map.map_size() - np.cumsum(hist)
            addedpre = np.insert(preresult, 0, map.map_size())
            if type(apix) is tuple:
                tmpresult = addedpre * ((apix[0]*apix[1]*apix[2]) / (10 ** 3))
            else:
                tmpresult = addedpre * ((apix**3) / (10**3))

            datadict = {
                'volume_estimate': {'volume': np.round(tmpresult, 10).tolist(), 'level': np.round(bins, 10).tolist()}}
        except:
            err = 'Volume estimate calculation error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')
        if errlist:
            datadict = {'volume_estimate': {'err': {'volume_estimate_error': errlist}}}
        try:
            with codecs.open(self.workdir + self.mapname + '_volume_contour.json', 'w',
                             encoding='utf-8') as f:
                json.dump(datadict, f)
        except:
            sys.stderr.write('Saving volume estimate to json error:{}.\n'.format(sys.exc_info()[1]))

        end = timeit.default_timer()
        print('Volume contour time: %s' % (end - start))
        print('------------------------------------')

        return None

    # Central slices

    def central_slice(self):
        """

            Produce central slices for x, y, z axes

        :return: None

        """

        start = timeit.default_timer()
        errlist = []

        map = self.map
        workdir = self.workdir
        xmid = int(float(map.x_size()) / 2)
        ymid = int(float(map.y_size()) / 2)
        zmid = int(float(map.z_size()) / 2)

        xcentral = map.fullMap[:, :, xmid]
        xdenom = (xcentral.max() - xcentral.min()) if xcentral.max() != xcentral.min() else 1
        xrescaled = (((xcentral - xcentral.min()) * 255.0) / xdenom).astype('uint8')
        xflipped = np.flipud(xrescaled)
        ximg = Image.fromarray(xflipped)
        try:
            ximg.save(self.workdir + self.mapname + '_xcentral_slice.jpeg')
        except IOError as ioerr:
            xerr = 'Saving original x central slice err:{}'.format(ioerr)
            errlist.append(xerr)
            sys.stderr.write(xerr + '\n')

        width, height = ximg.size
        xscalename = self.workdir + self.mapname + '_scaled_xcentral_slice.jpeg'

        try:
            if width > 300 and height > 300:
                if width >= height:
                    largerscaler = 300. / width
                    newheight = int(ceil(largerscaler * height))
                    imx = Image.fromarray(xflipped).resize((300, newheight), Image.ANTIALIAS)
                    imx.save(xscalename)
                else:
                    largerscaler = 300. / height
                    newwidth = int(ceil(largerscaler * width))
                    imx = Image.fromarray(xflipped).resize((newwidth, 300), Image.ANTIALIAS)
                    imx.save(xscalename)
                # imx = Image.fromarray(xflipped).resize((300,300))
                # imx.save(xscalename)
            else:
                if width >= height:
                    scaler = 300. / width
                    newheight = int(ceil(scaler * height))
                    imx = Image.fromarray(xflipped).resize((300, newheight), Image.ANTIALIAS)
                    imx.save(xscalename)
                else:
                    scaler = 300. / height
                    newwidth = int(ceil(scaler * width))
                    imx = Image.fromarray(xflipped).resize((newwidth, 300), Image.ANTIALIAS)
                    imx.save(xscalename)
        except:
            xerr = 'Saving scaled x central slice err:{}'.format(sys.exc_info()[1])
            errlist.append(xerr)
            sys.stderr.write(xerr + '\n')

        ycentral = map.fullMap[:, ymid, :]
        ydenom = (ycentral.max() - ycentral.min()) if ycentral.max() != ycentral.min() else 1
        yrescaled = (((ycentral - ycentral.min()) * 255.0) / ydenom).astype('uint8')
        yrotate = np.rot90(yrescaled)
        yimg = Image.fromarray(yrotate)
        try:
            yimg.save(self.workdir + self.mapname + '_ycentral_slice.jpeg')
        except IOError as ioerr:
            yerr = 'Saving original y central slice err:{}'.format(ioerr)
            errlist.append(yerr)
            sys.stderr.write(yerr + '\n')

        width, height = yimg.size
        yscalename = self.workdir + self.mapname + '_scaled_ycentral_slice.jpeg'
        try:
            if width > 300 and height > 300:
                if width >= height:
                    largerscaler = 300. / width
                    newheight = int(ceil(largerscaler * height))
                    imy = Image.fromarray(yrotate).resize((300, newheight), Image.ANTIALIAS)
                    imy.save(yscalename)
                else:
                    largerscaler = 300. / height
                    newwidth = int(ceil(largerscaler * width))
                    imy = Image.fromarray(yrotate).resize((newwidth, 300), Image.ANTIALIAS)
                    imy.save(yscalename)
                # imy = Image.fromarray(yrotate).resize((300, 300))
                # imy.save(yscalename)
            else:
                if width >= height:
                    scaler = 300. / width
                    newheight = int(ceil(scaler * height))
                    imy = Image.fromarray(yrotate).resize((300, newheight), Image.ANTIALIAS)
                    imy.save(yscalename)
                else:
                    scaler = 300. / height
                    newwidth = int(ceil(scaler * width))
                    imy = Image.fromarray(yrotate).resize((newwidth, 300), Image.ANTIALIAS)
                    imy.save(yscalename)
        except:
            yerr = 'Saving scaled y central slice err:{}'.format(sys.exc_info()[1])
            errlist.append(yerr)
            sys.stderr.write(yerr + '\n')

        zcentral = map.fullMap[zmid, :, :]
        zdenom = (zcentral.max() - zcentral.min()) if zcentral.max() != zcentral.min() else 1
        zrescaled = (((zcentral - zcentral.min()) * 255.0) / zdenom).astype('uint8')
        zflipped = np.flipud(zrescaled)
        zimg = Image.fromarray(zflipped)
        try:
            zimg.save(self.workdir + self.mapname + '_zcentral_slice.jpeg')
        except IOError as ioerr:
            zerr = 'Saving original z central slice err:{}'.format(ioerr)
            errlist.append(zerr)
            sys.stderr.write(zerr + '\n')

        width, height = zimg.size
        zscalename = self.workdir + self.mapname + '_scaled_zcentral_slice.jpeg'
        try:
            if width > 300 and height > 300:
                if width >= height:
                    largerscaler = 300. / width
                    newheight = int(ceil(largerscaler * height))
                    imz = Image.fromarray(zflipped).resize((300, newheight), Image.ANTIALIAS)
                    imz.save(zscalename)
                else:
                    largerscaler = 300. / height
                    newwidth = int(ceil(largerscaler * width))
                    imz = Image.fromarray(zflipped).resize((newwidth, 300), Image.ANTIALIAS)
                    imz.save(zscalename)
                # imz = Image.fromarray(zflipped).resize((300, 300))
                # imz.save(zscalename)
            else:
                if width >= height:
                    scaler = 300. / width
                    newheight = int(ceil(scaler * height))
                    imz = Image.fromarray(zflipped).resize((300, newheight), Image.ANTIALIAS)
                    imz.save(zscalename)
                else:
                    scaler = 300. / height
                    newwidth = int(ceil(scaler * width))
                    imz = Image.fromarray(zflipped).resize((newwidth, 300), Image.ANTIALIAS)
                    imz.save(zscalename)
        except:
            zerr = 'Saving original z scaled central slice err:{}'.format(sys.exc_info()[1])
            errlist.append(zerr)
            sys.stderr.write(zerr + '\n')


        cslicejson = dict()
        cslicejson['x'] = os.path.basename(xscalename) if os.path.isfile(xscalename) else None
        cslicejson['y'] = os.path.basename(yscalename) if os.path.isfile(yscalename) else None
        cslicejson['z'] = os.path.basename(zscalename) if os.path.isfile(zscalename) else None
        if errlist:
            cslicejson['err'] = {'central_slice_err': errlist}
        finaldict = {'central_slice': cslicejson}

        try:
            with codecs.open(self.workdir + self.mapname + '_centralslice.json', 'w',
                             encoding='utf-8') as f:
                json.dump(finaldict, f)
        except IOError as ioerr:
            print('Saving central slices to json err: {}'.format(ioerr))

        end = timeit.default_timer()
        print('CentralSlice time: %s' % (end - start))
        print('------------------------------------')

        return None


    ################### test

    # def pssum(self,i, dist, indiaxis):
    #     if i != len(indiaxis) - 1:
    #         indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
    #         psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
    #         return psum

    # def pssum(self,indices):
    #     # if i != len(indiaxis) - 1:
    #     # indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
    #     psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
    #     return psum


    def pararaps(self):
        """

            Calculation of the rotationally average power spectrum (RAPS)
            Results wrote to JSON file

        :return: None

        """
        import multiprocessing as mp
        import itertools
        threadcount = 2
        pool = mp.Pool(threadcount)

        if self.map.x_size() == self.map.y_size() == self.map.z_size():
            errlist = []
            start = timeit.default_timer()
            map = self.map
            apix = map.apix
            fftmap = map.fourier_transform()
            psmap = fftmap.copy()
            psmean = np.mean(psmap.fullMap)
            psstd = np.std(psmap.fullMap)
            psmap.fullMap = np.abs((psmap.fullMap - psmean) / psstd) ** 2

            midstart = timeit.default_timer() - start
            print(' -- RAPS Fourier-transformation time: %s' % midstart)

            zgrid = np.arange(floor(psmap.z_size() / 2.0) * -1, ceil(psmap.z_size() / 2.0)) / float(floor(psmap.z_size()))
            ygrid = np.arange(floor(psmap.y_size() / 2.0) * -1, ceil(psmap.y_size() / 2.0)) / float(floor(psmap.y_size()))
            xgrid = np.arange(floor(psmap.x_size() / 2.0) * -1, ceil(psmap.x_size() / 2.0)) / float(floor(psmap.x_size()))
            xdis = xgrid ** 2
            ydis = ygrid ** 2
            zdis = zgrid ** 2
            dist = np.sqrt(zdis[:, None, None] + ydis[:, None] + xdis)

            allaxis = [zgrid, ygrid, xgrid]
            tmpindiaxis = max(allaxis, key=len)
            indiaxist = tmpindiaxis[tmpindiaxis >= 0]
            indiaxis = np.linspace(0, 1 / (2 * apix), len(indiaxist))
            print('dist:')
            print(allaxis)
            print(dist.shape)
            print(indiaxis)
            print(psmap.z_size())
            print('-------')
            print(dist[98,96,96])


            aps = []
            # for i in range(len(indiaxis)):
            #     if i != len(indiaxis) - 1:
            #         indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
            #         psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
            #         aps.append(psum)

            allindices = []
            allpsmap = []
            # for i in range(len(indiaxis)):
            #     if i != len(indiaxis) -1:
            #         indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
            #
            #         psum = psmap.fullMap[tuple(indices.T)].sum()
            #         allindices.append(indices)
            #         allpsmap.append(psum)
            # print(allindices)
            odd = []
            even =[]
            counter = 0
            rlist = []
            templist = []
            for i in range(len(indiaxis)-1):
                counter += 1
                if i == 0:
                    templist.append(i)
                elif i % 40 == 0:
                    rlist.append(templist)
                    templist = []
                    templist.append(i)
                else:
                    templist.append(i)

            rlist.append(templist)

            def split_list(inp_list, nr):
                """
                Splits evenly a list
                :param inp_list: list
                :param nr: number of parts
                :return: list of "nr" lists
                """
                new_list = []
                nr_el = 1.0 / nr * len(inp_list)
                for i in range(nr):
                    start = int(round(i * nr_el))
                    end = int(round((i + 1) * nr_el))
                    new_list.append(inp_list[start:end])
                return new_list
            inputlist = range(0, len(indiaxis)-1)
            rlist = split_list(inputlist, threadcount)

            # Try with shared object
            import multiprocessing
            import ctypes
            x, y, z = dist.shape

            shared_array_base = multiprocessing.Array(ctypes.c_double, x*y*z)
            # shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
            shared_array = np.frombuffer(shared_array_base.get_obj())
            shared_array = shared_array.reshape(dist.shape)



            shared_array[:] = dist[:]
            # aps = [pool.apply(pcal, args=(i, allindices, allpsmap)) for i in rlist]
            aps = [pool.apply(pssum, args=(i, indiaxis, indiaxist, shared_array)) for i in rlist]
            # aps = aps[:-1]
            # aps = pool.map(self.pssum, [ i for i in allindices])
            newaps = list(itertools.chain.from_iterable(aps))
            # print(len(newaps))

            for i in range(len(indiaxis)-1):
                if i != len(indiaxis) -1:
                    psum = log10(psmap.fullMap[tuple(newaps[i].T)].sum() / len(newaps[i]))
                    allpsmap.append(psum)

            print(allpsmap)

            ##################

            datadict = {'rotationally_averaged_power_spectrum': {'y': np.round(allpsmap, 4).tolist(),
                                                                 'x': np.round(indiaxis[:-1], 4).tolist()}}
            err = 'RAPS calculation error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            datadict = {'rotationally_averaged_power_spectrum': {'err': {'raps_err': errlist}}}
            sys.stderr.write(err + '\n')

            if bool(datadict):
                try:
                    with codecs.open(self.workdir + self.mapname + '_raps.json', 'w', encoding='utf-8') as f:
                        json.dump(datadict, f)
                except:
                    sys.stderr.write('Saving RAPS to json error: {}.'.format(sys.exc_info()[1]))
            else:
                sys.stderr.write('No raps data in the dictionary, no raps json file.\n')

            end = timeit.default_timer()
            print('RAPS time: %s' % (end - start))
            print('------------------------------------')
        else:
            print('No RAPS calculation for non-cubic map.')
            print('------------------------------------')


        return None

    def raps(self):
        """

            Calculation of the rotationally average power spectrum (RAPS)
            Results wrote to JSON file

        :return: None

        """

        if self.map.x_size() == self.map.y_size() == self.map.z_size():
            errlist = []
            start = timeit.default_timer()
            datadict = dict()
            try:
                map = self.map
                # temprary solution as the tempy give apix as one value but here from mrcfile we use a tuple
                if type(map.apix) is tuple:
                    apix = map.apix[0]
                else:
                    apix = map.apix
                fftmap = map.fourier_transform()
                psmap = fftmap.copy()
                psmean = np.mean(psmap.fullMap)
                psstd = np.std(psmap.fullMap)
                psmap.fullMap = np.abs((psmap.fullMap - psmean) / psstd) ** 2

                midstart = timeit.default_timer() - start
                print(' -- RAPS Fourier-transformation time: %s' % midstart)

                zgrid = np.arange(floor(psmap.z_size() / 2.0) * -1, ceil(psmap.z_size() / 2.0)) / float(floor(psmap.z_size()))
                ygrid = np.arange(floor(psmap.y_size() / 2.0) * -1, ceil(psmap.y_size() / 2.0)) / float(floor(psmap.y_size()))
                xgrid = np.arange(floor(psmap.x_size() / 2.0) * -1, ceil(psmap.x_size() / 2.0)) / float(floor(psmap.x_size()))
                # zgrid = np.arange(floor(psmap.z_size()*2 / 2.0) * -1, ceil(psmap.z_size()*2 / 2.0)) / float(floor(psmap.z_size()))
                # ygrid = np.arange(floor(psmap.y_size()*2 / 2.0) * -1, ceil(psmap.y_size()*2 / 2.0)) / float(floor(psmap.y_size()))
                # xgrid = np.arange(floor(psmap.x_size()*2 / 2.0) * -1, ceil(psmap.x_size()*2 / 2.0)) / float(floor(psmap.x_size()))
                xdis = xgrid ** 2
                ydis = ygrid ** 2
                zdis = zgrid ** 2
                dist = np.sqrt(zdis[:, None, None] + ydis[:, None] + xdis)

                allaxis = [zgrid, ygrid, xgrid]
                tmpindiaxis = max(allaxis, key=len)
                indiaxist = tmpindiaxis[tmpindiaxis >= 0]
                indiaxis = np.linspace(0, 1 / (2 * apix), len(indiaxist))

                aps = []
                for i in range(len(indiaxis)):
                    if i != len(indiaxis) - 1:
                        indices = np.argwhere((dist >= indiaxist[i]) & (dist < indiaxist[i + 1]))
                        psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
                        aps.append(psum)
                    else:
                        indices = np.argwhere(dist == indiaxist[i])
                        psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
                        aps.append(psum)
                datadict = {'rotationally_averaged_power_spectrum': {'y': np.round(aps, 10).tolist(),
                                                                     'x': np.round(indiaxis, 10).tolist()}}
                # plt.plot(np.round(indiaxis, 4).tolist(), np.round(aps, 4).tolist())
                # plt.savefig('test')

            except:
                err = 'RAPS calculation error: {}.'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            if errlist:
                datadict = {'rotationally_averaged_pwer_spectrum': {'err': {'raps_err': errlist}}}

            if bool(datadict):
                try:
                    with codecs.open(self.workdir + self.mapname + '_raps.json', 'w', encoding='utf-8') as f:
                        json.dump(datadict, f)
                except:
                    sys.stderr.write('Saving RAPS to json error: {}.'.format(sys.exc_info()[1]))
            else:
                sys.stderr.write('No raps data in the dictionary, no raps json file.\n')

            end = timeit.default_timer()
            print('RAPS time: %s' % (end - start))
            print('------------------------------------')
        else:
            print('No RAPS calculation for non-cubic map.')
            print('------------------------------------')


        return None

    def __interpolated_intercept(self, x, y1, y2):
        """

            Find the intercept of two curves, given by the same x data

        """

        def intercept(point1, point2, point3, point4):
            """

                Find the intersection between two lines
                the first line is defined by the line between point1 and point2
                the second line is defined by the line between point3 and point4
                each point is an (x,y) tuple.

                So, for example, you can find the intersection between
                intercept((0,0), (1,1), (0,1), (1,0)) = (0.5, 0.5)

                :return: Intercept, in (x,y) format

            """

            def line(p1, p2):
                A = (p1[1] - p2[1])
                B = (p2[0] - p1[0])
                C = (p1[0] * p2[1] - p2[0] * p1[1])

                return A, B, -C

            def intersection(L1, L2):
                D = L1[0] * L2[1] - L1[1] * L2[0]
                Dx = L1[2] * L2[1] - L1[1] * L2[2]
                Dy = L1[0] * L2[2] - L1[2] * L2[0]

                x = Dx / D
                y = Dy / D

                return x, y

            L1 = line([point1[0], point1[1]], [point2[0], point2[1]])
            L2 = line([point3[0], point3[1]], [point4[0], point4[1]])

            R = intersection(L1, L2)

            return R

        idx = np.argwhere(np.diff(np.sign(y1 - y2)) != 0)
        xc, yc = intercept((x[idx], y1[idx]), ((x[idx + 1], y1[idx + 1])), ((x[idx], y2[idx])),
                           ((x[idx + 1], y2[idx + 1])))
        return xc, yc

    def fscs(self):
        """



        :return: None
        """
        if self.hmeven is not None and self.hmodd is not None:
            startfsc = timeit.default_timer()
            self.fsc(self.hmeven, self.hmodd)
            stop = timeit.default_timer()
            print('FSC: %s' % (stop - startfsc))
            print('------------------------------------')
        else:
            print('Mising half map(s).')

        fscxmlre = '*_fsc.xml'
        fscxmlarr = glob.glob(self.workdir + fscxmlre)
        if fscxmlarr or self.fscfile:
            startfsc = timeit.default_timer()
            self.readfsc()
            stop = timeit.default_timer()
            print('Load FSC: %s' % (stop - startfsc))
            print('------------------------------------')
        else:
            print('No given FSC data to be loaded.')

    def readfsc(self, asym=1.0):
        """

        :return:
        """
        import xml.etree.ElementTree as ET

        errlist = []
        finaldict = dict()

        if self.fscfile is not None:
            xlist = []
            ylist = []
            cpmap = None
            try:
                filefsc = self.workdir + self.fscfile
                tree = ET.parse(filefsc)
                root = tree.getroot()
                for child in root:
                    x = float(child.find('x').text)
                    y = float(child.find('y').text)
                    xlist.append(x)
                    ylist.append(y)
                cpmap = self.map
                cpmap.fullMap = fftshift(fftn(self.map.fullMap))
            except:
                err = 'Read FSC from XML error: {}.'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            try:
                # Grid here to generate for tracing the indices of grids with in the shells.
                zgrid = np.arange(floor(cpmap.z_size() / 2.0) * -1, ceil(cpmap.z_size() / 2.0)) / float(
                    floor(cpmap.z_size()))
                ygrid = np.arange(floor(cpmap.y_size() / 2.0) * -1, ceil(cpmap.y_size() / 2.0)) / float(
                    floor(cpmap.y_size()))
                xgrid = np.arange(floor(cpmap.x_size() / 2.0) * -1, ceil(cpmap.x_size() / 2.0)) / float(
                    floor(cpmap.x_size()))
                xdis = xgrid ** 2
                ydis = ygrid ** 2
                zdis = zgrid ** 2
                # dist = np.sqrt(zdis[:, None, None] + ydis[:, None] + xdis)

                allaxis = np.array([zgrid, ygrid, xgrid])
                tmpindiaxis = max(allaxis, key=len)
                indiaxist = tmpindiaxis[tmpindiaxis >= 0]
                lindi = len(indiaxist)
                # indiaxis = np.linspace(0, 1 / (2 * cpmap.apix), lindi)

                # Looping through all shells
                threesig = []
                halfbit = []
                onebit = []
                # for i in range(len(indiaxis)):
                for i in range(len(xlist)):
                    # if i < len(indiaxis) - 1:
                        # indices = np.argwhere((dist >= indiaxist[i]) & (dist < indiaxist[i + 1]))

                    volumediff = (4.0 / 3.0) * pi * ((i + 1) ** 3 - i ** 3)
                    nvoxring = volumediff / (1 ** 3)
                    effnvox = (nvoxring * ((1.5 * 0.66) ** 2)) / (2 * asym)
                    if effnvox < 1.0: effnvox = 1.0
                    sqreffnvox = np.sqrt(effnvox)

                    # 3-sigma curve
                    if i != 0:
                        sigvalue = 3 / (sqreffnvox + 3.0 - 1.0)
                    else:
                        sigvalue = 1
                    threesig.append(sigvalue)

                    # Half bit curve
                    if i != 0:
                        bitvalue = (0.2071 + 1.9102 / sqreffnvox) / (1.2071 + 0.9102 / sqreffnvox)
                    else:
                        bitvalue = 1
                    halfbit.append(bitvalue)

                    if i != 0:
                        onebitvalue = (0.5 + 2.4142 / sqreffnvox) / (1.5 + 1.4142 / sqreffnvox)
                    else:
                        onebitvalue = 1
                    onebit.append(onebitvalue)

                threesig.append(threesig[-1])
                halfbit.append(halfbit[-1])
                onebit.append(onebit[-1])

                a = np.asarray(xlist)
                b = np.asarray(ylist[1:])
                c = np.asarray(threesig[1:])
                d = np.asarray(halfbit[1:])
                e = np.asarray(onebit[1:])
                f = np.full((len(xlist)), 0.5)
                g = np.full((len(xlist)), 0.333)
                h = np.full((len(xlist)), 0.143)
                # f = np.full((len(indiaxis)), 0.5)
                # g = np.full((len(indiaxis)), 0.333)
                # h = np.full((len(indiaxis)), 0.143)

                cc = c if len(c) < len(b) else c[:len(b)]
                dd = d if len(d) < len(b) else d[:len(b)]
                ee = e if len(e) < len(b) else e[:len(b)]
                ff = f if len(f) < len(b) else f[:len(b)]
                gg = g if len(g) < len(b) else g[:len(b)]
                hh = h if len(h) < len(b) else h[:len(b)]

                if len(c) < len(b):
                    b = b[:len(c)]
                else:
                    c = c[:len(b)]

                if len(d) < len(b):
                    b = b[:len(d)]
                else:
                    d = d[:len(b)]


                if len(e) < len(b):
                    b = b[:len(e)]
                else:
                    e = e[:len(b)]


                if len(f) < len(b):
                    b = b[:len(f)]
                else:
                    f = f[:len(b)]


                if len(g) < len(b):
                    b = b[:len(g)]
                else:
                    g = g[:len(b)]

                if len(h) < len(b):
                    b = b[:len(h)]
                else:
                    h = h[:len(b)]

                xthreesig, ythreesig = self.__interpolated_intercept(a, b, c)
                xhalfbit, yhalfbit = self.__interpolated_intercept(a, b, d)
                xonebit, yonebit = self.__interpolated_intercept(a, b, e)
                xhalf, yhalf = self.__interpolated_intercept(a, b, f)
                xonethree, yonethree = self.__interpolated_intercept(a, b, g)
                xgold, ygold = self.__interpolated_intercept(a, b, h)

                if xthreesig.size == 0 and ythreesig.size == 0:
                    txthreesig = None
                    tythreesig = None
                else:
                    txthreesig = np.round(xthreesig[0][0], 4)
                    tythreesig = np.round(ythreesig[0][0], 4)

                if xhalfbit.size == 0 and yhalfbit.size == 0:
                    txhalfbit = None
                    tyhalfbit = None
                else:
                    txhalfbit = np.round(xhalfbit[0][0], 4)
                    tyhalfbit = np.round(yhalfbit[0][0], 4)

                if xonebit.size == 0 and yonebit.size == 0:
                    txonebit = None
                    tyonebit = None
                else:
                    txonebit = np.round(xonebit[0][0], 4)
                    tyonebit = np.round(yonebit[0][0], 4)

                if xhalf.size == 0 and yhalf.size == 0:
                    txhalf = None
                    tyhalf = None
                else:
                    txhalf = np.round(xhalf[0][0], 4)
                    tyhalf = np.round(yhalf[0][0], 4)

                if xonethree.size == 0 and yonethree.size == 0:
                    txonethree = None
                    tyonethree = None
                else:
                    txonethree = np.round(xonethree[0][0], 4)
                    tyonethree = np.round(yonethree[0][0], 4)

                if xgold.size == 0 and ygold.size == 0:
                    txgold = None
                    tygold = None
                else:
                    txgold = np.round(xgold[0][0], 4)
                    tygold = np.round(ygold[0][0], 4)

                xlen = len(xlist)

                datadict = {
                    'curves': {'fscy': np.round(np.real(ylist), 4).tolist(), 'threesigma': np.round(threesig, 4).tolist()[:xlen],
                               'halfbit': np.round(halfbit, 4).tolist()[:xlen],
                               'onebit': np.round(onebit, 4).tolist()[:xlen], '0.5': f.tolist()[:xlen], '0.333': g.tolist()[:xlen],
                               '0.143': h.tolist()[:xlen],
                               'level': np.round(np.real(xlist), 4).tolist(),
                               'fscx': np.round(np.real(xlist), 4).tolist()},
                    'intersections': {'threesig': {'x': txthreesig, 'y': tythreesig},
                                      'halfbit': {'x': txhalfbit, 'y': tyhalfbit},
                                      'onebit': {'x': txonebit, 'y': tyonebit},
                                      '0.5': {'x': txhalf, 'y': tyhalf},
                                      '0.333': {'x': txonethree, 'y': tyonethree},
                                      '0.143': {'x': txgold, 'y': tygold}}}

                finaldict['load_fsc'] = datadict

                plt.plot(xlist, ylist, label='FSC')
                #plt.plot(indiaxis, threesig, label='3 sigma')
                #plt.plot(indiaxis, halfbit, label='1/2 bit')
                #plt.plot(indiaxis, onebit, label='1 bit')
                plt.plot(xlist[:-1], len(xlist[:-1])*[0.5], label='0.5', linestyle=':')
                #plt.plot(indiaxis, g, label='0.333', linestyle='--')
                plt.plot(xlist[:-1], len(xlist[:-1])*[0.143], label='0.143', linestyle='-.')
                plt.legend()
                plt.savefig(self.workdir + self.mapname + '_fsc.png')
            except:
                err = 'FSC reading error: {}.'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            if errlist:
                finaldict['load_fsc'] = {'err': {'load_fsc_err': errlist}}

            try:
                with codecs.open(self.workdir + self.mapname + '_loadfsc.json', 'w', encoding='utf-8') as f:
                    json.dump(finaldict, f)

                return None
            except:
                sys.stderr.write('Saving loaded FSC to json error:{}.\n'.format(sys.exc_info()[1]))
        else:
            print('No fsc.xml file can be read for FSC information.')


    def fsc(self, mapodd, mapeven, asym=1.0):
        """

            Calculate FSC based on the two input half maps
            Results wrote to JSON file including resolution at 0.143, 0.333, 0.5 and noise
            level at 0.5-bit, 1-bit, 3-sigma. A corresponding plot is also save as PNG file.

        :param mapodd: TEMPy map instance
        :param mapeven: TEMPy map instance
        :return: None

        """


        assert mapodd.box_size() == mapeven.box_size(), 'The two half maps do not have same size.'
        assert mapodd.apix == mapeven.apix, 'The two half maps do not have same apix.'

        start = timeit.default_timer()
        errlist = []
        datadict = dict()
        finaldict = dict()
        try:
            mapodd.fullMap = fftshift(fftn(mapodd.fullMap))
            mapeven.fullMap = fftshift(fftn(mapeven.fullMap))

            start = timeit.default_timer() - start
            print(' -- FSC Fourier-transformation time: %s' % start)

            # Grid here to generate for tracing the indices of grids with in the shells.
            zgrid = np.arange(floor(mapodd.z_size() / 2.0) * -1, ceil(mapodd.z_size() / 2.0)) / float(
                floor(mapodd.z_size()))
            ygrid = np.arange(floor(mapodd.y_size() / 2.0) * -1, ceil(mapodd.y_size() / 2.0)) / float(
                floor(mapodd.y_size()))
            xgrid = np.arange(floor(mapodd.x_size() / 2.0) * -1, ceil(mapodd.x_size() / 2.0)) / float(
                floor(mapodd.x_size()))
            xdis = xgrid ** 2
            ydis = ygrid ** 2
            zdis = zgrid ** 2
            dist = np.sqrt(zdis[:, None, None] + ydis[:, None] + xdis)

            allaxis = np.array([zgrid, ygrid, xgrid])
            tmpindiaxis = max(allaxis, key=len)
            indiaxist = tmpindiaxis[tmpindiaxis >= 0]
            lindi = len(indiaxist)
            indiaxis = np.linspace(0, 1 / (2 * mapodd.apix), lindi)

            # Looping through all shells
            corrlist = []
            threesig = []
            halfbit = []
            onebit = []
            for i in range(len(indiaxis)):
                if i != len(indiaxis) - 1:
                    indices = np.argwhere((dist >= indiaxist[i]) & (dist < indiaxist[i + 1]))
                    oddring = mapodd.fullMap[tuple(indices.T)]
                    evenring = mapeven.fullMap[tuple(indices.T)]

                    corr = (oddring * np.conj(evenring)).sum()
                    norcorr = np.real(corr / np.sqrt((np.abs(oddring) ** 2).sum() * (np.abs(evenring) ** 2).sum()))
                    corrlist.append(norcorr)

                    volumediff = (4.0 / 3.0) * pi * ((i + 1) ** 3 - i ** 3)
                    nvoxring = volumediff / (1 ** 3)
                    effnvox = (nvoxring * ((1.5 * 0.66) ** 2)) / (2 * asym)
                    if effnvox < 1.0: effnvox = 1.0
                    sqreffnvox = np.sqrt(effnvox)

                    # 3-sigma curve
                    if i != 0:
                        sigvalue = 3 / (sqreffnvox + 3.0 - 1.0)
                    else:
                        sigvalue = 1
                    threesig.append(sigvalue)

                    # Half bit curve
                    if i != 0:
                        bitvalue = (0.2071 + 1.9102 / sqreffnvox) / (1.2071 + 0.9102 / sqreffnvox)
                    else:
                        bitvalue = 1
                    halfbit.append(bitvalue)

                    if i != 0:
                        onebitvalue = (0.5 + 2.4142 / sqreffnvox) / (1.5 + 1.4142 / sqreffnvox)
                    else:
                        onebitvalue = 1
                    onebit.append(onebitvalue)
                else:
                    indices = np.argwhere((dist==indiaxist[i]))
                    oddring = mapodd.fullMap[tuple(indices.T)]
                    evenring = mapeven.fullMap[tuple(indices.T)]

                    corr = (oddring * np.conj(evenring)).sum()
                    norcorr = np.real(corr / np.sqrt((np.abs(oddring) ** 2).sum() * (np.abs(evenring) ** 2).sum()))
                    corrlist.append(norcorr)

                    # 3-sigma curve
                    if i != 0:
                        sigvalue = 3 / (sqreffnvox + 3.0 - 1.0)
                    else:
                        sigvalue = 1
                    threesig.append(sigvalue)

                    # Half bit curve
                    if i != 0:
                        bitvalue = (0.2071 + 1.9102 / sqreffnvox) / (1.2071 + 0.9102 / sqreffnvox)
                    else:
                        bitvalue = 1
                    halfbit.append(bitvalue)

                    if i != 0:
                        onebitvalue = (0.5 + 2.4142 / sqreffnvox) / (1.5 + 1.4142 / sqreffnvox)
                    else:
                        onebitvalue = 1
                    onebit.append(onebitvalue)

            # corrlist.append(corrlist[-1])
            # threesig.append(threesig[-1])
            # halfbit.append(halfbit[-1])
            # onebit.append(onebit[-1])
            a = np.asarray(indiaxis)
            b = np.asarray(corrlist)
            c = np.asarray(threesig)
            d = np.asarray(halfbit)
            e = np.asarray(onebit)
            f = np.full((len(indiaxis)), 0.5)
            g = np.full((len(indiaxis)), 0.333)
            h = np.full((len(indiaxis)), 0.143)
            # use [:1] to ignore all the curves start from 0,1
            xthreesig, ythreesig = self.__interpolated_intercept(a, b[1:], c[1:])
            xhalfbit, yhalfbit = self.__interpolated_intercept(a, b[1:], d[1:])
            xonebit, yonebit = self.__interpolated_intercept(a, b[1:], e[1:])
            xhalf, yhalf = self.__interpolated_intercept(a, b, f)
            xonethree, yonethree = self.__interpolated_intercept(a, b, g)
            xgold, ygold = self.__interpolated_intercept(a, b, h)

            # Assign intersection value as None when there is no intersection
            if xthreesig.size == 0 and ythreesig.size == 0:
                print('No intersection between FSC and 3-sigma curves. Here use the last point.')
                xthreesig, ythreesig = None, None
            else:
                xthreesig = np.round(xthreesig[0][0], 4)
                ythreesig = np.round(ythreesig[0][0], 4)

            if xhalfbit.size == 0 and yhalfbit.size == 0:
                print('No intersection between FSC and 1/2-bit curves. Here use the last point.')
                xhalfbit, yhalfbit = None, None
            else:
                xhalfbit = np.round(xhalfbit[0][0], 4)
                yhalfbit = np.round(yhalfbit[0][0], 4)

            if xonebit.size == 0 and yonebit.size == 0:
                print('No intersection between FSC and 1-bit curves. Here use the last point.')
                xonebit, yonebit = None, None
            else:
                xonebit = np.round(xonebit[0][0], 4)
                yonebit = np.round(yonebit[0][0], 4)

            if xonethree.size == 0 and yonethree.size == 0:
                print('No intersection between FSC and 0.333 curves. Here use the last point')
                xonethree, yonethree = None, None
            else:
                xonethree = np.round(xonethree[0][0], 4)
                yonethree = np.round(yonethree[0][0], 4)

            if xhalf.size == 0 and yhalf.size == 0:
                print('!!! No intersection between FSC and 0.5 curves. Here use the last point')
                xhalf, yhalf = None, None
            else:
                xhalf = np.round(xhalf[0][0], 4)
                yhalf = np.round(yhalf[0][0], 4)
            if xgold.size == 0 and ygold.size == 0:
                print('!!! No intersection between FSC and 0.143 curves. Here use the last point')
                xgold, ygold = None, None
            else:
                xgold = np.round(xgold[0][0], 4)
                ygold = np.round(ygold[0][0], 4)


            datadict = {
                'curves': {'fsc': np.round(np.real(corrlist), 4).tolist(), 'threesigma': np.round(threesig, 4).tolist(),
                           'halfbit': np.round(halfbit, 4).tolist(),
                           'onebit': np.round(onebit, 4).tolist(), '0.5': f.tolist(), '0.333': g.tolist(),
                           '0.143': h.tolist(),
                           'level': np.round(indiaxis, 4).tolist()},
                'intersections': {'threesig': {'x': xthreesig, 'y': ythreesig},
                                  'halfbit': {'x': xhalfbit, 'y': yhalfbit},
                                  'onebit': {'x': xonebit, 'y': yonebit},
                                  '0.5': {'x': xhalf, 'y': yhalf},
                                  '0.333': {'x': xonethree, 'y': yonethree},
                                  '0.143': {'x': xgold, 'y': ygold}}}
            finaldict = dict()
            finaldict['fsc'] = datadict

            plt.plot(indiaxis, corrlist, label='FSC')
            plt.plot(indiaxis, threesig, label='3 sigma')
            plt.plot(indiaxis, halfbit, label='1/2 bit')
            plt.plot(indiaxis, onebit, label='1 bit')
            plt.plot(indiaxis, f, label='0.5', linestyle=':')
            plt.plot(indiaxis, g, label='0.333', linestyle='--')
            plt.plot(indiaxis, h, label='0.143', linestyle='-.')
            plt.legend()
            plt.savefig(self.workdir + self.mapname + '_fsc.png')
        except:
            err = 'FSC calculation error: {}'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')

        if errlist:
            datadict = {'err': {'fsc_error': errlist}}

        if bool(datadict) and bool(finaldict):
            try:
                with codecs.open(self.workdir + self.mapname + '_fsc.json', 'w', encoding='utf-8') as f:
                    json.dump(finaldict, f)
                print('FSC produced by two half maps.')
            except:
                sys.stderr.write('Writing FSC data to json file error: {}.'.format(sys.exc_info()[1]))
        else:
            sys.stderr.write('FSC calculation get none ')



        return None

    @staticmethod
    def mempred(resultfile, inputfilesize):
        """

            Produce memory prediction results using linear regression
            based on the data from previous entries.


        :param resultfile: Previous memory usage information in CSV file
        :param inputfilesize: The input density map size
        :return: 0 or y_pred (the predicted memory usage)
        """
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import mean_squared_error, r2_score
        from sklearn.model_selection import train_test_split
        from sklearn.model_selection import cross_val_score, cross_val_predict

        data = pd.read_csv(resultfile, header=0)
        data = data.dropna()
        if data.empty:
            print('No useful data in the dataframe.')
            return None
        else:
            newdata = data.iloc[:, 1:]
            sortdata = newdata.sort_values(newdata.columns[0])
            merdata = sortdata.groupby(sortdata.columns[0], as_index=False).mean()
            x = merdata['maprealsize']
            y = merdata['mem']
            X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)
            if X_train.empty or X_test.empty or y_train.empty or y_test.empty or len(x.index) < 30:
                print('Sparse data for memory prediction, result may not accurate.')
                return None
            else:
                lrmodel = LinearRegression(fit_intercept=False)
                # Perform CV
                scores = cross_val_score(lrmodel, x.values.reshape(-1, 1), y, cv=6)
                predictions = cross_val_predict(lrmodel, x.values.reshape(-1, 1), y, cv=6)

                lrmodel.fit(X_train.values.reshape(-1, 1), y_train)
                lrpredict = lrmodel.predict(X_test.values.reshape(-1, 1))
                print('6-Fold CV scores:%s' % scores)
                print('CV accuracy: %s' % (r2_score(y, predictions)))
                # print 'Score:%s' % (lrmodel.score(X_test.values.reshape(-1,1), y_test))
                print('Linear model coefficients: %s' % (lrmodel.coef_))
                print('MSE: %s' % (mean_squared_error(y_test, lrpredict)))
                print('Variance score(test accuracy): %s' % (r2_score(y_test, lrpredict)))
                y_pred = lrmodel.predict([[inputfilesize]])

                return y_pred

    @staticmethod
    def savepeakmemory(filename, maxmem):
        """

            Data collected and to be used for prediction for memory usage
            Memory saved as a comma separate CSV file.


        :param filename: String for file which used to collect data
        :param maxmem: Float number which gives peak memory usage of the finished job
        :return: None

        """

        columnname = 'mem'
        # dir = MAP_SERVER_PATH if self.emdid is not None else os.path.dirname(os.path.dirname(self.workdir))
        # filename = dir + 'input.csv'
        memresultfile = filename
        df = pd.read_csv(filename, header=0, sep=',', skipinitialspace=True)
        df[columnname][len(df.index) - 1] = maxmem
        df.to_csv(memresultfile, sep=',', index=False)

        return None

    def imgvariance(self):
        """

            Take the slice with the largest variance from each dimension


        :return: None
        """

        from scipy import ndimage
        map = self.map
        zlim, ylim, xlim = map.box_size()
        start = timeit.default_timer()

        xvar = [ndimage.variance(map.fullMap[:, :, i]) for i in range(0, xlim)]
        yvar = [ndimage.variance(map.fullMap[:, i, :]) for i in range(0, ylim)]
        zvar = [ndimage.variance(map.fullMap[i, :, :]) for i in range(0, zlim)]
        xlargeind = np.argmax(xvar)
        ylargeind = np.argmax(yvar)
        zlargeind = np.argmax(zvar)

        errlist = []

        xlargevar = map.fullMap[:, :, xlargeind]
        xdenom = (xlargevar.max() - xlargevar.min()) if xlargevar.max() != xlargevar.min() else 1
        xrescaled = (((xlargevar - xlargevar.min()) * 255.0) / xdenom).astype('uint8')
        xflipped = np.flipud(xrescaled)
        ximg = Image.fromarray(xflipped)
        try:
            ximg.save(self.workdir + self.mapname + '_xlargestvariance_slice.jpeg')
        except IOError as ioerr:
            xerr = 'Saving original x largest variance err: {}.'.format(ioerr)
            errlist.append(xerr)
            sys.stderr.write(xerr + '\n')

        width, height = ximg.size
        xscalename = self.workdir + self.mapname + '_scaled_xlargestvariance_slice.jpeg'

        try:
            if width > 300 and height > 300:
                if width >= height:
                    largerscaler = 300. / width
                    newheight = int(ceil(largerscaler * height))
                    imx = Image.fromarray(xflipped).resize((300, newheight), Image.ANTIALIAS)
                    imx.save(xscalename)
                else:
                    largerscaler = 300. / height
                    newwidth = int(ceil(largerscaler * width))
                    imx = Image.fromarray(xflipped).resize((newwidth, 300), Image.ANTIALIAS)
                    imx.save(xscalename)
                # imx = Image.fromarray(xflipped).resize((300, 300))
                # imx.save(xscalename)
            else:
                if width >= height:
                    scaler = 300. / width
                    newheight = int(ceil(scaler * height))
                    imx = Image.fromarray(xflipped).resize((newheight,300))
                    imx.save(xscalename)
                else:
                    scaler = 300. / height
                    newwidth = int(ceil(scaler * width))
                    imx = Image.fromarray(xflipped).resize((300, newwidth))
                    imx.save(xscalename)
        except:
            xerr = 'Saving scaled x largest variance err: {}.'.format(sys.exc_info()[1])
            errlist.append(xerr)
            sys.stderr.write(xerr + '\n')

        ylargevar = map.fullMap[:, ylargeind, :]
        ydenom = (ylargevar.max() - ylargevar.min()) if ylargevar.max() != ylargevar.min() else 1
        yrescaled = (((ylargevar - ylargevar.min()) * 255.0) / ydenom).astype('uint8')
        yrotate = np.rot90(yrescaled)
        yimg = Image.fromarray(yrotate)
        try:
            yimg.save(self.workdir + self.mapname + '_ylargestvariance_slice.jpeg')
        except IOError as ioerr:
            yerr = 'Saving original y largest variance err: {}.'.format(ioerr)
            errlist.append(yerr)
            sys.stderr.write(yerr + '\n')

        width, height = yimg.size
        yscalename = self.workdir + self.mapname + '_scaled_ylargestvariance_slice.jpeg'
        try:
            if width > 300 and height > 300:
                if width >= height:
                    largerscaler = 300. / width
                    newheight = int(ceil(largerscaler * height))
                    imy = Image.fromarray(yrotate).resize((300, newheight), Image.ANTIALIAS)
                    imy.save(yscalename)
                else:
                    largerscaler = 300. / height
                    newwidth = int(ceil(largerscaler * width))
                    imy = Image.fromarray(yrotate).resize((newwidth, 300), Image.ANTIALIAS)
                    imy.save(yscalename)
                # imy = Image.fromarray(yrotate).resize((300, 300))
                # imy.save(yscalename)
            else:
                if width >= height:
                    scaler = 300. / width
                    newheight = int(ceil(scaler * height))
                    imy = Image.fromarray(yrotate).resize((newheight, 300))
                    imy.save(yscalename)
                else:
                    scaler = 300. / height
                    newwidth = int(ceil(scaler * width))
                    imy = Image.fromarray(yrotate).resize((300, newwidth))
                    imy.save(yscalename)
        except:
            yerr = 'Saving scaled y largest variance err: {}.'.format(sys.exc_info()[1])
            errlist.append(yerr)
            sys.stderr.write(yerr + '\n')

        zlargevar = map.fullMap[zlargeind, :, :]
        zdenom = (zlargevar.max() - zlargevar.min()) if zlargevar.max() != zlargevar.min() else 1
        zrescaled = (((zlargevar - zlargevar.min()) * 255.0) / zdenom).astype('uint8')
        zflipped = np.flipud(zrescaled)
        zimg = Image.fromarray(zflipped)
        try:
            zimg.save(self.workdir + self.mapname + '_zlargestvariance_slice.jpeg')
        except IOError as ioerr:
            zerr = 'Saving original z largest variance err: {}.'.format(ioerr)
            errlist.append(zerr)
            sys.stderr.write(zerr + '\n')

        width, height = zimg.size
        zscalename = self.workdir + self.mapname + '_scaled_zlargestvariance_slice.jpeg'
        try:
            if width > 300 and height > 300:
                if width >= height:
                    largerscaler = 300. / width
                    newheight = int(ceil(largerscaler * height))
                    imz = Image.fromarray(zflipped).resize((300, newheight), Image.ANTIALIAS)
                    imz.save(zscalename)
                else:
                    largerscaler = 300. / height
                    newwidth = int(ceil(largerscaler * width))
                    imz = Image.fromarray(zflipped).resize((newwidth, 300), Image.ANTIALIAS)
                    imz.save(zscalename)
                # imz = Image.fromarray(zflipped).resize((300, 300))
                # imz.save(zscalename)
            else:
                if width >= height:
                    scaler = 300. / width
                    newheight = int(ceil(scaler * height))
                    imz = Image.fromarray(zflipped).resize((newheight, 300))
                    imz.save(zscalename)
                else:
                    scaler = 300. / height
                    newwidth = int(ceil(scaler * width))
                    imz = Image.fromarray(zflipped).resize((300, newwidth))
                    imz.save(zscalename)
        except:
            zerr = 'Saving scaled z largest variance err: {}.'.format(sys.exc_info()[1])
            errlist.append(zerr)
            sys.stderr.write(zerr + '\n')


        vslicejson = dict()
        vslicejson['x'] = os.path.basename(xscalename) if os.path.isfile(xscalename) else None
        vslicejson['y'] = os.path.basename(yscalename) if os.path.isfile(yscalename) else None
        vslicejson['z'] = os.path.basename(zscalename) if os.path.isfile(zscalename) else None
        vslicejson['indices'] = {'x': xlargeind, 'y': ylargeind, 'z': zlargeind}
        if errlist:
            vslicejson['err'] = {'largest_variance_err': errlist}
        finaldict = {'largest_variance_slice' : vslicejson}

        try:
            with codecs.open(self.workdir + self.mapname + '_largestvarianceslice.json', 'w',
                             encoding='utf-8') as f:
                json.dump(finaldict, f)
        except IOError as ioerr:
            sys.stderr.write('Saving largest variance to json err: {}.\n'.format(ioerr))

        end = timeit.default_timer()
        print('Variance time: %s' % (end - start))
        print('------------------------------------')

        return None

    def symmetry(self):
        """
            Produing symmetry information of the map by using Proshade
            This function using the binary proshade program  not the python api

        :return:  None
        """

        start = timeit.default_timer()
        errlist = []
        if self.met is not None and self.resolution is not None:
            if self.met != 'tomography' and self.met != 'helical':
                proshade = False
                if PROSHADEPATH:
                    proshadepath = PROSHADEPATH
                    proshade = True

                else:
                    try:
                        assert find_executable('proshade') is not None
                        proshadepath = find_executable('proshade')
                        proshade = True
                    except AssertionError:
                        # print('proshade executable is not there, please install proshade.', file=sys.stderr)
                        # print('Symmetry information will not be produced.', file=stys.stderr)
                        sys.stderr.write('proshade executable is not there, please install proshade.\n')
                        sys.stderr.write('Symmetry information will not be produced.\n')

                if proshade:
                    try:
                        fullmappath = '{}{}'.format(self.workdir, self.mapname)
                        cmd = (PROSHADEPATH + ' -S -f ' + self.map.filename + ' -s ' + str(float(self.resolution)*1.5)).split(' ')
                        print(cmd)
                        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                        code = process.wait()
                        output = process.stdout.read()
                        splstr = 'RESULTS'
                        # outputspl = output.split('Detected Cyclic symmetry', 1)
                        outputspl = re.split("RESULTS", output)
                        if splstr in output:
                            print(outputspl[1])
                        else:
                            print(outputspl[0])

                        end = timeit.default_timer()
                        print('Symmetry time: %s' % (end - start))
                        print('------------------------------------')

                        return None
                    except:
                        err = 'Symmetry calculation error: {}.'.format(sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')


                else:
                    # print('Proshade is not installed. There will be no symmetry information.', file=sys.stderr)
                    sys.stderr.write('Proshade is not installed. There will be no symmetry information.\n')
                    print('------------------------------------')

            else:
                # print('This is a {} entry, symmetry will not be calculated'.format(self.met), file=sys.stderr)
                sys.stderr.write('This is a {} entry, symmetry will not be calculated.\n'.format(self.met))
                print('------------------------------------')

        else:
            # print('EM method and resolution needed to calculated symmetry information!', file=sys.stderr)
            sys.stderr.write('EM method and resolution needed to calculated symmetry information!\n')
            print('------------------------------------')

        return None

    def symmetrytojson(self, output):
        """

            Convert the output of proshade symmetry calculation to json which can be used further

        :param output:
        :return:
        """

        pass


    def ccc(self):
        """

            Using the TEMPy function to calculate the cross-correlation score

        :return:
        """

        from TEMPy.ScoringFunctions import ScoringFunctions
        from TEMPy.StructureBlurrer import StructureBlurrer

        errlist = []
        try:
            scorer = ScoringFunctions()
            blurrer = StructureBlurrer()
            cccscoredict = {}
            for model in self.models:
                probe_map = blurrer.gaussian_blur_real_space(model, self.resolution, densMap=self.map)
                cccscoredict[os.path.basename(model)] = scorer.CCC_map(probe_map, self.map, self.cl, self.cl)
            return cccscoredict
        except:
            err = 'CCC calculation error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')



    def smoc(self):

        """

                Calculate SMOC score from TEMPy

        :return:
        """

        from TEMPy.ScoringFunctions import ScoringFunctions

        errlist = []
        try:
            chainscoredict = {}
            chainresdict = {}
            for model in self.models:
                name = os.path.basename(model.filename)
                chainscore[name], chainres[name] = ScoringFunctions.SMOC(self.map.filename, self.resolution, model,
                 win=11, rigid_body_file=None, sigma_map=0.225, write=False, c_mode=True)
            return chainscoredict, chainresdict
        except:
            err = 'SMOC calculation error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')






    def emringer(self):
        """

            Emringer score

        :return:
        """

        emringer = False
        try:
            assert find_executable('phenix.emringer') is not None
            emringerpath = find_executable('phenix.emringer')
            emringer = True
        except AssertionError:
            sys.stderr.write('emringer executable is not there.\n')

        errlist = []
        if emringer:
            for model in self.models:
                try:
                    subprocess.check_call(emringerpath + ' ' + model.filename + ' ' + self.map.filename,
                                          cwd=self.workdir, shell=True)
                except subprocess.CalledProcessError as suberr:
                    err = 'EMRinger calculation error: {}.'.format(suberr)
                    errlist.append(err)
                    sys.stderr.write(err + '\n')



    def emringerpkl_json(self):
        """

            Load EMRiinger output pickle file and write out to a JSON file

        :return:
        """

        pass