from setuptools import setup

setup(
    name='isomut2py',
    version='2.0.5',
    description='A mutation detection software from NGS data with multiple filtering and plotting features',
    url='http://github.com/pipekorsi/isomut2',
    author='Orsolya Pipek',
    author_email='pipeko@caesar.elte.hu',
    license='MIT',
    packages=['isomut2py'],
    package_data={'isomut2py': ['alexandrovSignatures/*.csv', 'C/*']},
    install_requires=['matplotlib>=2.0.0',
                      'pandas>=0.20.3',
                      'Theano>=1.0.4',
                      'pymc3==3.1',
                      'setuptools>=33.1.1',
                      'seaborn>=0.8',
                      'scipy==0.19.1',
                      'numpy==1.12.1',
                      'biopython']
)

##### THIS DOES NOT SEEM TO WORK...
##### (when packaged with wheel, it runs, but not at the installation, and this is also mentioned as a problem on SO)

# import atexit
# import os
# import sys
# from setuptools import setup
# from setuptools.command.install import install
# import subprocess
#
#
# class CustomInstall(install):
#     def run(self):
#         def _post_install():
#             def find_module_path():
#                 for p in sys.path:
#                     if os.path.isdir(p) and 'isomut2py' in os.listdir(p):
#                         return os.path.join(p, 'isomut2py')
#
#             install_path = find_module_path()
#
#             # Add your post install code here
#
#             for __fname in os.listdir(install_path + '/C'):
#                 if __fname.split('.')[-1] != 'h' and __fname.split('.')[-1] != 'c':
#                     subprocess.call('rm ' + install_path + '/C/' + __fname, shell=True)
#
#             print('Compiling C scripts...')
#             cwd = os.getcwd()
#             __compiled = []
#             os.chdir(install_path + '/C')
#             __cmd = 'gcc -c -O3 isomut2_lib.c fisher.c  -W -Wall'
#             __compiled.append(subprocess.call(__cmd, shell=True))
#             __cmd = 'gcc -O3 -o isomut2 isomut2.c isomut2_lib.o fisher.o -lm -W -Wall'
#             __compiled.append(subprocess.call(__cmd, shell=True))
#             __cmd = 'gcc -O3 -o PEprep PEprep.c isomut2_lib.o fisher.o -lm -W -Wall'
#             __compiled.append(subprocess.call(__cmd, shell=True))
#             __cmd = 'gcc -O3 -o checkPileup checkPileup.c isomut2_lib.o fisher.o -lm -W -Wall'
#             __compiled.append(subprocess.call(__cmd, shell=True))
#             os.chdir(cwd)
#
#             if 1 in __compiled:
#                 print('WARNING: C scripts were not compiled correctly, some functions will not work.')
#                 print('Try compiling manually to ' + install_path + '/C')
#             else:
#                 print('Done.')
#
#         atexit.register(_post_install)
#         install.run(self)
#
#
# setup(
#     cmdclass={'install': CustomInstall},
#     name='isomut2py',
#     version='2.0.2',
#     description='A mutation detection software from NGS data with multiple filtering and plotting features',
#     url='http://github.com/pipekorsi/isomut2',
#     author='Orsolya Pipek',
#     author_email='pipeko@caesar.elte.hu',
#     license='MIT',
#     packages=['isomut2py'],
#     package_data={'isomut2py': ['alexandrovSignatures/*.csv', 'C/*']},
#     install_requires=['matplotlib>=2.0.0',
#                       'pandas>=0.20.3',
#                       'Theano>=0.9.0',
#                       'pymc3>=3.1',
#                       'setuptools>=33.1.1',
#                       'seaborn>=0.8',
#                       'scipy>=0.19.1',
#                       'numpy>=1.12.1',
#                       'biopython']
# )
