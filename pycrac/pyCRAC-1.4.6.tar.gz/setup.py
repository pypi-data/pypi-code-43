#!/usr/bin/python

__author__      = "Sander Granneman"
__copyright__   = "Copyright 2019"
__version__     = "1.4.6"
__credits__     = ["Sander Granneman","Grzegorz Kudla","Hywell Dunn Davies"]
__maintainer__  = ["Sander Granneman"]
__email__       = "sgrannem@staffmail.ed.ac.uk"
__status__      = "Production"


import re
import sys
import os
import platform
from os.path import expanduser

OSX = """
#######################################################################
#                                                                     #
#           You are about to install the pyCRAC on Mac OSX...         #
#                                                                     #
#                Please make sure you have Xcode and                  #
#                 the Command line tools installed!                   #
#                   Xcode can be obtained from the                    #
#                        Mac App store.                               #
#                                                                     #
#                 We also recommend installing the                    #
#                Enthought Canopy python distribution,                #
#                  which has most of the dependencies.                #
#             This distribution is also free for academics.           #
#                                                                     #
#######################################################################
"""

LINUX = """
########################################################################################
#                                                                                      #
#          You are about to install the pyCRAC on a Linux operating system...          #
#                                                                                      #
#                        This installer has been tested on:                            #
#                                                                                      #
#        Linux Mint 16, Ubuntu 13.04 and higher, Debian Wheezy/Sid and Fedora 20       #
#                                                                                      #
#      To install certain dependencies (such as the zlib libraries and python          #
#              development tools) you need to have root privileges.                    #
#                                                                                      #
########################################################################################
"""

ROOT_WARNING = """
#################################################################################################################
#                                                                                                               #
#                   !!WARNING!! You do not have root privileges on this machine !!WARNING!!                     #
#                                                                                                               #
#         This installation may abort if certain dependencies are not present or can not be installed.          #
#             Please contact the administrator if the zlib and python development tools are missing.            #
#        These are essential for pyCRAC to work. Without root privileges you can only install pyCRAC            #
#                               in a python installation on your home folder.                                   #
#                                                                                                               #
#              We recommend installing the Enthought Canopy python distribution in your home folder.            #
#                                                                                                               #
#################################################################################################################
"""

DIST_WARNING = """
#####################################################################################
#                                                                                   #
# !!WARNING Could not determine what Linux distribution you are running !!WARNING!! #
#   For this installer to run properly, you need to have python developer tools,    #
#          python setuptools, numpy,  pysam and cython installed.                   #
#	Please e-mail the developer %s (%s)  #
#                  if you run into any problems.                                    #
#                                                                                   #
#####################################################################################
""" % (__author__,__email__)

sys.stdout.write("\nInstalling pyCRAC version %s...\n" % __version__)
supported = False
supported_systems = ["Linux","Darwin"]
if platform.system() == "Darwin":			  # only works on OS X
	sys.stdout.write("%s\n" % OSX)
elif platform.system() == "Linux":
	sys.stdout.write("%s\n" % LINUX)
	supported_distros = ["debian","ubuntu","mint","linuxmint","redhat","centos","fedora"]
	sys.stdout.write("\nChecking distribution...\n\n")
	distribution = platform.dist()
	flavor = distribution[0].lower()
	if flavor and flavor in supported_distros:
		supported = True
		sys.stdout.write("\tYou are running %s Linux version %s...\n\tInstalling dependencies...\n" % (distribution[0],distribution[1]))
	else:
		sys.stderr.write("%s\n" % DIST_WARNING)
	if os.getuid() == 0:
		if supported:
			if flavor in supported_distros[0:4]:		# distro = 'ubuntu' or 'debian'
				sys.stdout.write("\nInstalling python setup and development tools...\n")
				os.system("apt-get install python-setuptools")
				os.system("apt-get install python-dev")
				sys.stdout.write("\nChecking for other dependencies...\n")
				sys.stdout.write("zlib library..\n")
				os.system("apt-get install zlibc")
				os.system("apt-get install zlib1g-dev")
			elif flavor in supported_distros[4:]:		# distro = 'redhat' or 'centos' or 'fedora'
				sys.stdout.write("Checking for gcc and installing python setup and development tools...\n\n")
				os.system("yum install gcc")
				os.system("yum install python-setuptools")
				os.system("yum install python-devel")
				sys.stdout.write("Checking for other dependencies...\n")
				sys.stdout.write("zlib library..\n")
				os.system("yum install zlib-devel")
	else:
		sys.stderr.write("%s\n" % ROOT_WARNING)
else:
	sys.stderr.write("%s\n" % DIST_WARNING)

try:
	from setuptools import setup
	from setuptools.command import easy_install
	sys.stdout.write("Python development and setuptools have been installed...\n")
except:
	sys.stderr.write("Python development and setuptools have not been installed on this machine\nPlease contact the admin of this computer to install these modules\n")
	exit()

setup(name='pyCRAC',
	version='%s' % __version__,
	description='Python NextGen sequencing data processing software',
	author='Sander Granneman',
	author_email='sgrannem@staffmail.ed.ac.uk',
	url='http://sandergranneman.bio.ed.ac.uk/Granneman_Lab/pyCRAC_software.html',
	packages=['pyCRAC','pyCRAC.Parsers','pyCRAC.Classes','pyCRAC.Methods'],
	install_requires=['numpy >= 1.5.1', 'cython >=0.19', 'pysam >= 0.6','six >= 1.9.0'],
	scripts=[
					'pyCRAC/pyReadAligner.py',
					'pyCRAC/pyMotif.py',
					'pyCRAC/pyPileup.py',
					'pyCRAC/pyBarcodeFilter.py',
					'pyCRAC/pyReadCounters.py',
					'pyCRAC/pyBinCollector.py',
					'pyCRAC/pyCalculateFDRs.py',
					'pyCRAC/pyClusterReads.py',
					'pyCRAC/pyCalculateMutationFrequencies.py',
					'pyCRAC/scripts/pyCalculateChromosomeLengths.py',
					'pyCRAC/scripts/pyFastqDuplicateRemover.py',
					'pyCRAC/scripts/pyAlignment2Tab.py',
					'pyCRAC/scripts/pyGetGTFSources.py',
					'pyCRAC/scripts/pySelectMotifsFromGTF.py',
					'pyCRAC/scripts/pyFasta2tab.py',
					'pyCRAC/scripts/pyFastqJoiner.py',
					'pyCRAC/scripts/pyFastqSplitter.py',
					'pyCRAC/scripts/pyExtractLinesFromGTF.py',
					'pyCRAC/scripts/pyGetGeneNamesFromGTF.py',
					'pyCRAC/scripts/pyCheckGTFfile.py',
					'pyCRAC/scripts/pybed2GTF.py',
					'pyCRAC/scripts/pyGTF2sgr.py',
					'pyCRAC/scripts/pyGTF2bed.py',
					'pyCRAC/scripts/pyGTF2bedGraph.py',
					'pyCRAC/scripts/pyFilterGTF.py',
					'pyCRAC/scripts/pyNormalizeIntervalLengths.py',
				],
	classifiers=[   'Development Status :: 5 - Production/Stable',
					'Environment :: Console',
					'Intended Audience :: Education',
					'Intended Audience :: Developers',
					'Intended Audience :: Science/Research',
					'License :: Freeware',
					'Operating System :: MacOS :: MacOS X',
					'Operating System :: POSIX',
					'Programming Language :: Python :: 3.6',
					'Topic :: Scientific/Engineering :: Bio-Informatics',
					'Topic :: Software Development :: Libraries :: Application Frameworks'
				],
	data_files=[    ('pyCRAC/db/',[
					'pyCRAC/db/Saccharomyces_cerevisiae.EF2.59.1.0_chr_lengths.txt',
					'pyCRAC/db/Saccharomyces_cerevisiae.EF2.59.1.3.gtf',
					'pyCRAC/db/Saccharomyces_cerevisiae.EF2.59.1.0.fa',
					'pyCRAC/db/Saccharomyces_cerevisiae.EF2.59.1.0.fa.tab']),
					('pyCRAC/tests/',[
					'tests/test.novo',
					'tests/test.sh',
					'tests/test_coordinates.txt',
					'tests/test.gtf',
					'tests/test_f.fastq',
					'tests/test_f.fastq.gz',
					'tests/test_f_dm.fastq',
					'tests/test_r.fastq',
					'tests/test_r.fastq.gz',
					'tests/test_r_dm.fastq',
					'tests/indexes.txt',
					'tests/barcodes.txt',
					'tests/genes.list']),
					('pyCRAC',[
					'The_pyCRAC_Manual.pdf'])
				]
			  )
