# -*- coding: utf-8 -*-
import setuptools
import os
import glob
import io
import numpy.distutils.core
# noinspection PyProtectedMember
from numpy.distutils.fcompiler import get_default_fcompiler

# this is to get the __version__ from version.py
with open('src/jscatter/version.py', 'r') as f:  exec(f.read())

with io.open('README.rst', encoding='utf-8') as readme_file:
    long_description = readme_file.read()

# find fortran files
fs = glob.glob(os.path.join('src', 'jscatter', 'source', '*.f9[05]'))
fs.sort()
EXTENSIONS = []
if get_default_fcompiler(requiref90=True):
    EXTENSIONS.append(numpy.distutils.core.Extension(name='jscatter.fscatter',
                                                     sources=fs,
                                                     extra_f90_compile_args=['-fopenmp'],
                                                     libraries=['gomp'],
                                                     # extra_f90_compile_args=['--debug','-fbounds-check'],
                                                     # f2py_options=['--debug-capi']
                                                     ))


def getfilenamelist(destination, exfolder, path):
    """create list of tuple of later destination with actual path"""
    llist = []
    for dp, dn, filenames in os.walk(os.path.join(exfolder, path)):
        for f in filenames:
            newdp = ''.join(dp.split(exfolder)[1:])
            if newdp[0] == '/': newdp = newdp[1:]
            llist.append((os.path.join(destination, newdp), [os.path.join(dp, f)]))
    return llist


# create the tuples for the data_files
#datafiles = []
#datafiles += getfilenamelist('jscatter', 'src/jscatter/doc', 'html')


description=("Combines dataArrays with attributes for fitting, plotting" 
             "and analysis including models for Xray and neutron scattering")

fileext=['*.txt', '*.rst', '*.dat', '*.html',  '*.ipynb', '*.md', '*.f95', '*.f90',
         '*.tiff', '*.png', '*.jpg', '*.agr', '*.gif',
         '*.Dq', '*.pdb', '*.pdh']

numpy.distutils.core.setup(name='jscatter',
                           version=__version__,
                           description=description,
                           long_description=long_description,
                           author='Ralf Biehl',
                           author_email='ra.biehl@fz-juelich.de',
                           url='https://gitlab.com/biehl/jscatter',
                           project_urls={"Documentation": "http://jscatter.readthedocs.io/",
                                         "Source Code": "https://gitlab.com/biehl/jscatter",
                                         "Live Demo": "https://mybinder.org/v2/gl/biehl%2Fjscatter/master?filepath="
                                                      "src%2Fjscatter%2Fexamples%2Fnotebooks"},
                           platforms=["linux", "osx", "windows"],
                           classifiers=[
                               'Development Status :: 5 - Production/Stable',
                               'Intended Audience :: Science/Research',
                               'Operating System :: POSIX :: Linux',
                               'Operating System :: MacOS :: MacOS X',
                               'Operating System :: Microsoft :: Windows :: Windows 10',
                               'Programming Language :: Python :: 3.5',
                               'Programming Language :: Python :: 3.6',
                               'Programming Language :: Python :: 3.7',
                               'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                               'Programming Language :: Python',
                               'Topic :: Scientific/Engineering :: Physics'],
                           include_package_data=True,
                           package_dir={'': 'src'},
                           py_modules=[],
                           packages=setuptools.find_packages('src'),
                           package_data={'': fileext},
                           #data_files=datafiles,
                           dependency_links=[''],
                           install_requires=["numpy >= 1.8 ",
                                             "scipy >= 0.13",
                                             "matplotlib",
                                             "Pillow >= 5.2"],
                           ext_modules=EXTENSIONS,
                           test_suite='jscatter.test.suite'
                           )
