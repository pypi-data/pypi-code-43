#!/usr/bin/env python


"""
mainva.py

mainva class used to run the main function of validation
analysis

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



import timeit, os, sys
from memory_profiler import memory_usage
from validationanalysis import ValidationAnalysis
from preparation import PreParation as prep
try:
    from PATHS import MAP_SERVER_PATH
except ImportError:
    MAP_SERVER_PATH = None
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)


def allruns(validationobj, runs):
    """
        Each single run included here

    :param validationobj: validation object from ValidationAnalysis module
    :param runs: list of string which represent each of the function
    :return: None
    """

    # Projections
    if 'projection' in runs:
        validationobj.orthogonal_projections()

    # Central slice
    if 'central' in runs:
        validationobj.central_slice()

    # Largest variance
    if 'largestvariance' in runs:
        validationobj.imgvariance()

    # Sureface views
    if 'surface' in runs:
        validationobj.surfaces()

    # Masks views
    if 'mask' in runs:
        validationobj.masks()

    # Desnity distribution
    if 'density' in runs:
        validationobj.density_distribution()

    # Generate atom inclusion and residue inclusion json file
    if 'inclusion' in runs:
        validationobj.atom_inclusion()

    # Contour level verses volume
    if 'volume' in runs:
        validationobj.volumecontour()

    # RAPS
    if 'raps' in runs:
        validationobj.raps()
        # validationobj.pararaps()

    # FSC
    if 'fsc' in runs:
        validationobj.fscs()

    # Symmetry
    if 'symmetry' in runs:
        validationobj.symmetry()

    # CCC
    if 'ccc' in runs:
        validationobj.ccc()

    # SMOC
    if 'smoc' in runs:
        validationobj.smoc()

    # EMringer
    if 'emringer' in runs:
        validationobj.emringer()

    # Local resolution

    return None


def main():

    start_first = timeit.default_timer()

    # Preparation
    prepobj = prep()

    # Read map
    inputmap, mapsize, mapdimension = prepobj.read_map()

    # Read model
    inputmodel, pid, modelsize = prepobj.read_model()

    # Read half map
    halfeven, halfodd, halfmapsize = prepobj.read_halfmaps()

    # Contour level
    contourlevel = prepobj.contourlevel

    # Read run parameters
    runs = prepobj.runs()

    # EMDID
    emdid = prepobj.emdid
    dir = None if emdid is not None else prepobj.dir

    # Resolution and EM method
    resolution, emmethod = prepobj.resolution, prepobj.method

    # fscfile
    fscfile = prepobj.fscfile

    # Masks
    masks = prepobj.masks

    # Memory prediction
    memmsg = None
    # if len(runs) == 10 and 'mask' not in runs:
    memmsg = prepobj.memmsg(mapsize)


    # VA starts here on
    print('%sValidation Analysis%s' % (20*'=', 20*'='))
    validationobj = ValidationAnalysis(inputmap, inputmodel, pid, halfeven, halfodd,
                                       contourlevel, emdid, dir, emmethod, resolution, fscfile, masks)

    # Run all the validation piceces and give the peak memory consumption
    if len(runs) == 9 and 'mask' not in runs:
        mem = max(memory_usage((allruns, (validationobj, runs)), multiprocess=True, include_children=True))
        print('The memory peak is: {}.'.format(mem))
    else:
        allruns(validationobj, runs)
    # # Merge all jsons
    prepobj.finiliszejsons()

    stop = timeit.default_timer()
    alltime = stop - start_first
    # print('Memory usage peak: %s.' % mem)
    print('All time: %s' % alltime)


    # Save data for memory prediction
    #if runs['all'] is True:
    if len(runs) == 9 and 'mask' not in runs:
        if inputmodel is not None and modelsize is not None:
            modelout = sum(modelsize)/len(modelsize) if len(inputmodel) != 0 else 0
            vout = MAP_SERVER_PATH if emdid is not None else os.path.dirname(os.path.dirname(dir))
            with open(vout + '/input.csv', 'a+') as f:
                if os.stat(vout + '/input.csv').st_size == 0:
                    f.write('%s,%s,%s,%s,%s,%s,%s\n' % ('mapname', 'maprealsize', 'halfmapsize', 'modelrealsize', 'mapdimension', 'alltime', 'mem'))
                f.write('%s,%s,%s,%s,%s,%s,%s\n' % (prepobj.mapname, mapsize, halfmapsize, modelout, mapdimension, alltime, mem))
            f.close()
        else:
            vout = MAP_SERVER_PATH if emdid is not None else os.path.dirname(os.path.dirname(dir))
    else:
        vout = None




if __name__ == '__main__':
    main()

