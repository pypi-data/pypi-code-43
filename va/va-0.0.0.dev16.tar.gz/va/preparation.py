"""

preparation.py

preparation class is used to initialize the input and working
environment for validation analysis.

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

from TEMPy.MapParser import MapParser
from TEMPy.StructureParser import mmCIFParser
from TEMPy.EMMap import Map
# from TEMPy.protein.structure_parser import mmCIFParser
# from TEMPy.maps.map_parser import MapParser
from validationanalysis import ValidationAnalysis
import os, sys
import timeit
import json
import glob
from va import __version__

try:
    from PATHS import MAP_SERVER_PATH
except ImportError:
    MAP_SERVER_PATH = None


class PreParation:

    def __init__(self):
        """

            Initialization of objects for Validation analysis

        """
        self.args = self.read_para()
        self.emdid = self.args.emdid
        self.json = self.args.j
        if self.emdid:
            self.mapname = 'emd_{}.map'.format(self.emdid)
            self.subdir = self.folders(self.emdid)
            self.dir = '{}{}/va/'.format(MAP_SERVER_PATH, self.subdir)
            filepath = '{}{}/va/{}'.format(MAP_SERVER_PATH, self.subdir, self.mapname)
            try:
                inputdict = self.read_header()
                if os.path.isfile(filepath):
                    # Read header file
                    inputdict = self.read_header()
                    self.model = inputdict['fitmodels']
                    self.contourlevel = inputdict['reccl']
                    if len(inputdict['halfmaps']) == 2:
                        self.evenmap = inputdict['halfmaps'][0]
                        self.oddmap = inputdict['halfmaps'][1]
                    else:
                        self.evenmap = None
                        self.oddmap = None
                    self.pid = inputdict['fitpid']
                self.method = inputdict['method']
                self.resolution = inputdict['resolution']
                self.masks = inputdict['masks']
            except:
                print('No proper header information.')


            self.run = self.args.run
            self.fscfile = self.findfscxml()

        elif self.json:
            self.mapname, self.dir, self.model, self.contourlevel, self.evenmap, self.oddmap, \
                self.fscfile, self.method, self.resolution, self.masks, self.run = self.read_json(self.json)

        else:

            self.mapname = self.args.m
            self.model = self.args.f
            self.pid = self.args.pid
            self.emdid = self.args.emdid
            self.evenmap = self.args.hmeven
            self.oddmap = self.args.hmodd
            #self.contourlevel = float(self.args.cl) if self.args.cl else None
            self.contourlevel = self.read_contour()
            self.run = self.args.run
            self.dir = self.args.d + '/'
            self.method = self.args.met
            self.resolution = self.args.s

            # self.masks = self.collectmasks()
            if self.args.ms is not None:
                self.masks = {self.dir + i: float(j) for i, j in zip(self.args.ms, self.args.mscl)}
            else:
                self.masks = None
            self.fscfile = self.findfscxml()


    def findfscxml(self):
        """

            Find the fsc.xml file if exist

        :return:
        """

        fscxmlre = '*_fsc.xml'
        fscxmlarr = glob.glob(self.dir + fscxmlre)
        if not fscxmlarr:
            print('No fsc.xml file can be read for FSC information.')
            return None
        elif len(fscxmlarr) > 1:
            print('There are more than one FSC files in the folder. Please make sure only one exist.')
            return None
        else:
            filefsc = os.path.basename(fscxmlarr[0])
            return filefsc



    def read_json(self, injson):
        """

            Load input arguments from JSON file

        :return: dictornary which contains correspdong parameters for the pipeline
        """

        if injson:
            with open(injson, 'r') as f:
                args = json.load(f)
            argsdata = args['inputs']
            map = argsdata['map']
            assert map is not None, "There must be a map needed in the input JSON file."
            assert argsdata['workdir'] is not None, "Working directory must be provided in the input JSON file."
            workdir = argsdata['workdir'] + '/'
            if 'contour_level' in argsdata and argsdata['contour_level'] is not None:
                cl = argsdata['contour_level']
            else:
                print('There is no contour level.')
                cl = None

            if 'evenmap' in argsdata and argsdata['evenmap'] is not None:
                evenmap = argsdata['evenmap']
            else:
                print('There is no evnemap.')
                evenmap = None

            if 'oddmap' in argsdata and argsdata['oddmap'] is not None:
                oddmap = argsdata['oddmap']
            else:
                print('There is no oddmap.')
                oddmap = None

            if 'fscfile' in argsdata and argsdata['fscfile'] is not None:
                fscfile = argsdata['fscfile']
            else:
                print('There is no fsc file.')
                fscfile = None

            if 'method' in argsdata and argsdata['method'] is not None:
                method = argsdata['method']
            else:
                print('There is no method information.')
                method = None
            if 'resolution' in argsdata and argsdata['resolution'] is not None:
                resolution = argsdata['resolution']
            else:
                print('There is no resolution information.')
                resolution = None

            if 'runs' in argsdata and argsdata['runs'] is not None:
                runs = argsdata['runs']
            else:
                runs = 'all'

            if 'models' in argsdata and argsdata['models'] is not None:
                models = [argsdata['models'][item]['name'] for item in argsdata['models'] if item is not None ]
            else:
                models = None


            if  'masks' in argsdata and argsdata['masks'] is not None:
                masks = { workdir + argsdata['masks'][item]['name']: argsdata['masks'][item]['contour']
                          for item in argsdata['masks']}
            else:
                masks = {}

            # masks = { workdir + argsdata['masks'][item]['name']: argsdata['masks'][item]['contour'] for item in argsdata['masks']}

            return (map, workdir, models, cl, evenmap, oddmap, fscfile, method, resolution, masks, runs)
        else:
            print('Input JSON needed.')


    def runs(self):
        """

            Check parameters for -run

        :return: dictornary contains binary value of each parameter of -run
        """

        # If only one argument, it will be string type and should be converted to lower letters directly
        # For more than one arguments, it will be list type
        if isinstance(self.run, str):
            runs = self.run.lower()
        else:
            runs = [ x.lower() for x in self.run ]
        if runs[0] == 'validation':
            return ['projection', 'central', 'surface', 'volume', 'density', 'raps', 'largestvariance', 'mask',
                    'inclusion','fsc']
        else:
            resdict = {'all': False, 'projection': False, 'central': False, 'surface': False, 'density': False,
                       'volume': False, 'fsc': False, 'raps': False, 'mapmodel': False, 'inclusion': False,
                       'largestvariance': False, 'mask': False, 'symmetry': False, 'ccc':False, 'smoc':False ,
                       'emrigner': False}
            for key in resdict.keys():
                if key in runs:
                    resdict[key] = True
            # If -run has arguments but do not fit with any above, set to all to True
            if True not in resdict.values():
                resdict['all'] = False

            runlist = []
            if self.mapname is not None:
                runlist.extend(['projection', 'central', 'surface', 'volume', 'density', 'raps', 'largestvariance',
                                'mask', 'fsc'])

            if self.masks is None:
                runlist.remove('mask')

            if self.model is not None and self.contourlevel is not None:
                runlist.extend(['inclusion'])
            else:
                sys.stderr.write('Contour level or model needed for atom and residue inclusion.\n')


            # if self.evenmap is not None and self.oddmap is not None:
            #     runlist.extend(['fsc'])

            # if self.method is not None and self.resolution is not None:
            #     runlist.extend(['symmetry'])

            if runs[0] == 'all' or runs == 'all':
                finallist = runlist
            else:
                finallist = list(set(runlist) & set(runs))

            return finallist


    @staticmethod
    def folders(emdid):
        """

            Folders' path for the one entry with its ids

        :return: Dictionary key: id value: subpath of that entry
        """


        breakdigits = 2
        emdbidmin = 4
        if len(emdid) >= emdbidmin and isinstance(emdid, str):
            topsubpath = emdid[:breakdigits]
            middlesubpath = emdid[breakdigits:-breakdigits]
            subpath = os.path.join(topsubpath, middlesubpath, emdid)

            return subpath
        else:
            return None

    def read_header(self):
        """

            When "-emdid" is give, we search the input information for validation analysis
            inside the header file and return a dictionary

        :return:
        """

        import xml.etree.ElementTree as ET
        headerfile = '{}{}/va/emd-{}.xml'.format(MAP_SERVER_PATH, self.subdir, self.emdid)
        headerdict = {}
        if os.path.isfile(headerfile):
            tree = ET.parse(headerfile)
            root = tree.getroot()

            # Fitted models
            deposition = root.find('deposition')
            title = deposition.find('title').text
            fitlist = deposition.find('fittedPDBEntryIdList')
            fitmodel = []
            modelcount = 0
            fitpid = []
            if fitlist is not None:
                for child in fitlist.iter('fittedPDBEntryId'):
                    fitmodel.append(child.text + '.cif')
                    fitpid.append(child.text)

            # Recommended contour level
            map = root.find('map')
            contourtf = map.find('contourLevel')
            reccl = None
            if contourtf is not None:
                reccl = "{0:.3f}".format(float(map.find('contourLevel').text))

            # Half maps
            halfmapsfolder = '{}{}/va/*_half_map_*.map'.format(MAP_SERVER_PATH, self.subdir)
            halfmaps = glob.glob(halfmapsfolder)

            # check when there is fitted models for tomography data, do not count the fitted model
            # for calculating atom inclusion, residue inclusion or map model view
            processing = root.find('processing')
            method = processing.find('method').text
            headerdict['fitmodels'] = None if method == 'tomography' else fitmodel


            # Got the resolution value from the header
            reconstruction = processing.find('reconstruction')
            preresolution = reconstruction.find('resolutionByAuthor')
            if preresolution is None:
                resolution = None
            else:
                resolution = preresolution.text


            # Masks
            supplement = root.find('supplement')
            maskset = supplement.find('maskSet') if supplement is not None else None
            masks = {}
            if maskset is not None:
                for child in maskset.iter('mask'):
                    # masks.append(self.dir + child.find('file').text)
                    # Here as there is no mask value from the header, I use 1.0 for all masks
                    masks[self.dir + child.find('file').text] = 1.0
            methoddict = {'tomography': 'tomo', 'twoDCrystal': '2dcrys', 'singleParticle': 'sp',
                          'subtomogramAveraging': 'subtomo', 'helical': 'heli'}

            headerdict['fitmodels'] = fitmodel if fitmodel else None
            headerdict['fitpid'] = fitpid
            headerdict['reccl'] = reccl
            headerdict['halfmaps'] = halfmaps
            headerdict['method'] = methoddict[method]
            headerdict['resolution'] = resolution
            headerdict['masks'] = masks if masks else None


            return headerdict

        else:
            print('Header file: %s does not exit.' % headerfile)
            raise OSError('Header file does not exist.')


    @staticmethod
    def read_para():
        """

            Read arguments


        """

        import argparse
        assert len(sys.argv) > 1, ('There has to be arguments for the command.\n \
               Usage: mainva.py [-h] [-m [M]] [-d [D]] [-f [F]] [-pid [PID]] [-hm [HM]] [-cl [CL]]\n \
               or:    mainva.py [-emdid [EMDID]]')

        parser = argparse.ArgumentParser(description='Input density map(name) for Validation Analysis')
        #parser = mainparser.add_mutually_exclusive_group(required = True)
        parser.add_argument('--version', '-V', action='version', version='va: {version}'.format(version=__version__),
                            help='Version')
        parser.add_argument('-f', nargs='*',
                            help='Structure model file names. Multiple model names can be used with space separated.')
        parser.add_argument('-pid', nargs='?', help='PDB ID which needed while "-f" in use.')
        parser.add_argument('-hmeven', nargs='?', help='Half map.')
        parser.add_argument('-hmodd', nargs='?', help='The other half map.')
        parser.add_argument('-cl', nargs='?', help='The recommended contour level .')
        parser.add_argument('-run', nargs='*', help='Run customized validation analysis.', default='all')
        parser.add_argument('-met', nargs='?', help='EM method')
        parser.add_argument('-s', nargs='?', help='Resolution of the map.')
        parser.add_argument('-ms', nargs='*', help='All masks')
        parser.add_argument('-mscl', nargs='*', help='Contour level corresponding to the masks.')
        requiredname = parser.add_argument_group('required arguments')
        requiredname2 = parser.add_argument_group('alternative required arguments')
        requiredname3 = parser.add_argument_group('alternative required arguments')
        requiredname.add_argument('-m', nargs='?', help='Density map file')
        requiredname.add_argument('-d', nargs='?', help='Directory of all input files')
        requiredname2.add_argument('-emdid', nargs='?', help='EMD ID with which can run without other parameters.')
        requiredname3.add_argument('-j', nargs='?', help='JSON file which has all arguments.')
        args = parser.parse_args()
        checkpar = (isinstance(args.m, type(None)) and isinstance(args.f, type(None)) and
                    isinstance(args.pid, type(None)) and isinstance(args.hmeven, type(None)) and
                    isinstance(args.cl, type(None)) and isinstance(args.hmodd, type(None)) and
                    isinstance(args.emdid, type(None)) and isinstance(args.run, type(None)) and
                    isinstance(args.j) and isinstance(args.ms, type(None)) and isinstance(args.mscl, type(None)))

        if checkpar:
            print('There has to be arguments for the command. \n \
                  usage: mainva.py [-h] [-m [M]] [-d [D]] [-f [F]] [-pid [PID]] [-hm [HM]] [-cl [CL]] [-run [all]/[central...]]\n \
                  or   : mainva.py [-emdid [EMDID]] [-run [-run [all]/[central...]]]')
            sys.exit()
        return args


    def collectmasks(self):
        """
            todo: Collect masks information if exist return list of mask with full path
            else None(This can be used for unittest, here as the each masks need to corresponding to a contour level
            so the masks' full path and its corresponding contour level need to be generated by reading mmcif file
            and put into a dictionary.

        :return:
        """
        maskstr = ['mask', 'msk']
        globresult = glob.glob(self.dir+'*.map')
        maskresult = [s for s in globresult for b in maskstr if b in s]



        # Function inside here should do:
        # 1) look for mmcif file from self.workdir ( are their only one mmcif even for multiple fitted model)
        # 2) put mask full path and its corresponding contour level into a dictionary
        # For ccpem and individual user put either contour level contained inside a single file with certain name
        # or make it readable from the file name

        return maskresult

    def read_contour(self):
        """

            If contour level is not offer,  we need either pid or emdid to get the recommended contour level info
            If contour level is not given by user, estimate a reasonable contour level (Todo)

        :return: contour level

        """

        # if self.emdid:
        #     headfile = '{}EMD-{}/header/emd-{}.xml'.format(HEADER_PATH, self.emdid, self.emdid)
        #     tree = ET.parse(headfile)
        #     root = tree.getroot()
        #     map = root.find('map')
        #     reccl = float(map.find('contourLevel').text)
        #
        #     return reccl
        # elif self.args.cl:
        if self.args.cl:

            return float(self.args.cl)

        else:
            # Todo: Add a estimated contour level function here
            return None


    def swap_axes(self, header):
        """

            Swap the axes to make the data arranged as z, y, z by indices

        :param header:
        :return:
        """



    def frommrc_totempy(self, fullmapname):
        """
            Transfer the mrcfile map object to TEMPy map object

        :param fullmapname:
        :return: TEMPy map object
        """

        import mrcfile
        import numpy as np

        mrcmap = mrcfile.mmap(fullmapname, mode='r')
        mrcheader = mrcmap.header
        mapdata = mrcmap.data
        crs = (mrcheader.mapc, mrcheader.mapr, mrcheader.maps)
        reversecrs = crs[::-1]
        nstarts = (mrcheader.nxstart, mrcheader.nystart, mrcheader.nzstart)
        stdcrs = (1, 2, 3)
        diffcrs = tuple(x-y for x,y in zip(reversecrs, stdcrs))
        if diffcrs != (0, 0, 0):
            if 1 in diffcrs and -1 in diffcrs:
                mapdata = np.swapaxes(mapdata, diffcrs.index(-1), diffcrs.index(1))
            if -2 in diffcrs and 2 in diffcrs:
                mapdata = np.swapaxes(mapdata, diffcrs.index(-2), diffcrs.index(2))
            if 1 in diffcrs and -2 in diffcrs:
                mapdata = np.swapaxes(np.swapaxes(mapdata, 1, 2), 0, 1)
            if -1 in diffcrs and 2 in diffcrs:
                mapdata = np.swapaxes(np.swapaxes(mapdata, 0, 1), 1, 2)
            mapdata = np.swapaxes(mapdata, 0, 2)

        # mapdata = np.swapaxes(np.swapaxes(mapdata, 0, 2), 1, 2)
        tempyheader = MapParser.readMRCHeader(fullmapname)
        # nx, ny, nz and nxstart, nystart, nzstart haver to be changed accordingly to the data
        tempyheader = list(tempyheader)
        tempyheader[0] = mapdata.shape[2]
        tempyheader[1] = mapdata.shape[1]
        tempyheader[2] = mapdata.shape[0]
        # here also keep the nstarts position according to original crs order as in __getindices it automaticlly
        # adjust the calculation based on the
        # tempyheader[4] = int(nstarts[crs.index(1)])
        # tempyheader[5] = int(nstarts[crs.index(2)])
        # tempyheader[6] = int(nstarts[crs.index(3)])
        tempyheader = tuple(tempyheader)
        origin = (float(mrcheader.origin.x), float(mrcheader.origin.y), float(mrcheader.origin.z))
        apix = (mrcheader.cella.x/mrcheader.mx, mrcheader.cella.y/mrcheader.my, mrcheader.cella.z/mrcheader.mz)

        finalmap = Map(mapdata, origin, apix, fullmapname, header=tempyheader)

        # inputmap.fullMap = np.swapaxes(np.swapaxes(mrcfile.mmap(fullmapname).data, 0, 2), 1, 2)
        # print(inputmap.fullMap.shape)
        # print(inputmap.fullMap[1, 3, 66])

        return finalmap

    def read_map(self):
        """

            Read maps

        """

        start = timeit.default_timer()

        try:
            if self.emdid:
                #fullmapname = '{}EMD-{}/map/{}'.format(MAP_SERVER_PATH, self.emdid, self.mapname)
                fullmapname = '{}{}/va/{}'.format(MAP_SERVER_PATH, self.subdir, self.mapname)
                mapsize = os.stat(fullmapname).st_size
                # TEMPy way of reading MRC file which does not work well with the 2D crystall data, switch off
                # for now, when it is updated could be changed back

                # inputmap = MapParser.readMRC(fullmapname)

                # Use mrcfile to load all map related data
                inputmap = self.frommrc_totempy(fullmapname)
                mapdimension = inputmap.map_size()
                end = timeit.default_timer()

                print('Read map time: %s' % (end - start))
                print('------------------------------------')

                return inputmap, mapsize, mapdimension
            elif os.path.exists(self.dir) and self.mapname is not None:
                #print "selfmap:%s" % (self.mapname)
                fullmapname = self.dir + self.mapname
                if not os.path.isfile(fullmapname):
                    fullmapname = self.mapname
                mapsize = os.stat(fullmapname).st_size
                # Swith off using the TEMPy to read map and using the mrcfile loaded information for reading map
                # inputmap = MapParser.readMRC(fullmapname)
                inputmap = self.frommrc_totempy(fullmapname)
                mapdimension = inputmap.map_size()

                end = timeit.default_timer()
                print('Read map time: %s' % (end - start))
                print('------------------------------------')

                return inputmap, mapsize, mapdimension
            else:
                print('------------------------------------')
                print('Folder: %s does not exist.' % self.dir)
                exit()
        except:
            print('Map does not exist or corrupted.')
            sys.stderr.write('Error: {} \n'.format(sys.exc_info()[1]))
            print('------------------------------------')
            exit()



    def read_model(self):
        """

            Read models if '-f' argument is used

        """

        start = timeit.default_timer()
        if self.model is not None:
            modelname = self.model
            # Todo: 1)modelname could be multiple models here using just the first model
            #       2)after 'else', the path should be a path on server or a folder I ust to store all files
            #         right now just use the same value as before 'else'
            ## commented area can be deleted after fully test (below)
            # if self.emdid:
            #     # Real path is comment out for the reason that the folder on server is not ready yet
            #     # Here use the local folder VAINPUT_DIR for testing purpose
            #     #fullmodelname = MAP_SERVER_PATH + modelname[0] if self.emdid is None else MAP_SERVER_PATH + modelname[0]
            #     fullmodelname = [ VAINPUT_DIR + curmodel if self.emdid is None else MAP_SERVER_PATH + self.subdir + '/va/' + curmodel for curmodel in modelname ]
            # else:
            #     fullmodelname = [ VAINPUT_DIR + curmodel if self.emdid is None else VAINPUT_DIR + curmodel for curmodel in modelname ]
            # fullmodelname = [ self.dir + curmodel if self.emdid is None else MAP_SERVER_PATH + self.subdir + '/va/' + curmodel for curmodel in modelname ]
            fullmodelname = []
            if self.emdid is None:
                for curmodel in modelname:
                    if not os.path.isfile(self.dir + curmodel) and os.path.isfile(curmodel):
                        fullmodelname.append(curmodel)
                    elif os.path.isfile(self.dir + curmodel):
                        fullmodelname.append(self.dir + curmodel)
                    else:
                        print('Something wrong with the input model name or path.')
            else:
                fullmodelname =[ MAP_SERVER_PATH + self.subdir + '/va/' + curmodel for curmodel in modelname ]

            try:
                modelsize = [ os.stat(curmodelname).st_size for curmodelname in fullmodelname ]
                #pid = self.pid
                pids = [ os.path.basename(model)[:-4] for model in fullmodelname ]
                inputmodel = [ mmCIFParser.read_mmCIF_file(pid, curmodelname, hetatm=True) for pid, curmodelname in zip(pids, fullmodelname) ]

                end = timeit.default_timer()
                print('Read model time: %s' % (end - start))
                print('------------------------------------')

                return inputmodel, pids, modelsize
            except:
                print('File: %s does not exist or corrupted.' % fullmodelname)
                print('------------------------------------')
                exit()
        else:
            print('No model is given.')
            inputmodel = None
            pid = None
            modelsize = None

            return inputmodel, pid, modelsize

    def read_halfmaps(self):
        """

            Read two half maps for FSC calculation

        :return:
        """

        halfeven = None
        halfodd = None
        twomapsize = 0.
        if self.emdid:
            mapone = MAP_SERVER_PATH + self.subdir + '/va/' + 'emd_' + self.emdid + '_half_map_1.map'
            maptwo = MAP_SERVER_PATH + self.subdir + '/va/' + 'emd_' + self.emdid + '_half_map_2.map'
            if os.path.isfile(mapone) and os.path.isfile(maptwo):
                try:
                    halfodd = MapParser.readMRC(mapone)
                    halfeven = MapParser.readMRC(maptwo)
                    twomapsize = halfodd.map_size() + halfeven.map_size()
                except IOError as e:
                    print(e)
                    exit()
            else:
                halfeven = None
                halfodd = None
                twomapsize = 0.
                print('No half maps for this entry.')
        else:
            if self.evenmap is not None and self.oddmap is not None:
                try:
                    halfeven = MapParser.readMRC(self.dir + self.evenmap)
                    halfodd = MapParser.readMRC(self.dir + self.oddmap)
                    twomapsize = halfodd.map_size() + halfeven.map_size()
                except IOError as maperr:
                    print(maperr)
                    exit()
            elif self.evenmap is None and self.oddmap is None:
                print('REMINDER: Both half maps needed for FSC calculation!')
                halfeven = None
                halfodd = None
                twomapsize = 0.
            else:
                raise IOError('Another half map is needed for FSC calculation.')

        return halfeven, halfodd, twomapsize







        # if self.evenmap is not None and self.oddmap is not None and self.emdid is None:
        #     try:
        #         halfeven = MapParser.readMRC(VAINPUT_DIR + self.evenmap)
        #         halfodd = MapParser.readMRC(VAINPUT_DIR + self.oddmap)
        #     except IOError as maperr:
        #         print maperr
        #         exit()
        # elif self.evenmap is not None and self.oddmap is not None and self.emdid:
        #     try:
        #         halfeven = MapParser.readMRC(self.evenmap)
        #         halfodd = MapParser.readMRC(self.oddmap)
        #     except IOError as maperr:
        #         print maperr
        #         exit()
        # elif self.evenmap is None and self.oddmap is None:
        #     print 'REMINDER: Both half maps needed for FSC calculation!'
        #     halfeven = None
        #     halfodd = None
        # elif self.emdid:
        #     halfeven = MapParser.readMRC(MAP_SERVER_PATH + 'EMD_' + self.emdid + '/other/' + 'emd_'+ self.emdid + '_half_map_1.map')
        #     halfodd = MapParser.readMRC(MAP_SERVER_PATH + 'EMD_' + self.emdid + '/other/' + 'emd_'+ self.emdid + '_half_map_2.map')
        # else:
        #     raise IOError('Another half map is needed for FSC calculation.')
        #
        # return halfeven, halfodd


    def merge_jsons(self):
        """

            Merge all generated json files to one file

        :return: None
        """

        import glob
        import json

        # workdir = '{}{}/va/'.format(MAP_SERVER_PATH, self.subdir())
        jsonfiles = glob.glob(self.dir + '*.json')
        jsonfiles = [jfile for jfile in jsonfiles if 'all.json' not in jfile]

        fuldata = {}

        filename = os.path.basename(self.mapname) if self.emdid is None else self.emdid

        for tfile in jsonfiles:
            if os.path.getsize(tfile) > 0:
                with open(tfile, 'r') as f:
                    if f is not None:
                        data = json.load(f)
                        datakeys = list(data.keys())
                        if datakeys[0] != filename:
                            fuldata[datakeys[0]] = data.values()[0]
            else:
                sys.stderr.write('The {} is empty!\n'.format(tfile))

        finaldata = dict()
        if self.emdid is not None:
            finaldata[self.emdid] = fuldata
            output = '{}emd_{}_all.json'.format(self.dir, self.emdid)
        else:
            finaldata[filename] = fuldata
            output = '{}{}_all.json'.format(self.dir, filename)
        with open(output, 'w') as out:
            json.dump(finaldata, out)

        return None

    def write_recl(self):
        """

            Write recl into a json file

        :return: None
        """

        if self.contourlevel is not None:
            dictrecl = dict()
            dictrecl['recl'] = self.contourlevel
            lastdict = dict()
            lastdict['recommended_contour_level'] = dictrecl
            # filename = self.mapname if self.emdid is None else self.emdid
            filename = self.mapname
            # if self.emdid is not None:
            #     output = '{}emd_{}_recl.json'.format(self.workdir, filename)
            # else:
            #     output = '{}{}_recl.json'.format(self.workdir, filename)
            output = '{}{}_recl.json'.format(self.dir, os.path.basename(filename))
            with open(output, 'w') as out:
                json.dump(lastdict, out)

        return None

    def finiliszejsons(self):
        """



        :return:
        """

        start = timeit.default_timer()
        self.write_recl()
        self.merge_jsons()
        stop = timeit.default_timer()
        print('Merge JSONs: %s' % (stop - start))
        print('------------------------------------')

    #@staticmethod
    def memmsg(self, mapsize):
        """

            Memory usage reminder based on memory prediction

        :return:
        """
        # When there is no emdid given, we use one level above the given "dir" to save the memory prediction file
        # input.csv. If emdid is given, we use the. self.dir is like /abc/cde/ so it needs to used os.path.dirname()
        # twice.

        import psutil
        if self.emdid:
            vout = MAP_SERVER_PATH
        else:
            vout = os.path.dirname(os.path.dirname(self.dir)) + '/'
        if os.path.isfile(vout + 'input.csv') and os.path.getsize(vout + 'input.csv') > 0:
            mempred = ValidationAnalysis.mempred(vout + 'input.csv', 2 * mapsize)
            if mempred == 0:
                print('No memory prediction.')
                return None
            else:
                print('The memory you may need is %s M' % mempred)
                assert mempred < psutil.virtual_memory().total / 1024 / 1024, \
                    'The memory needed to run may exceed the total memory you have on the machine.'
                return mempred
        else:
            print('No memory data available for prediction yet')
            return None



