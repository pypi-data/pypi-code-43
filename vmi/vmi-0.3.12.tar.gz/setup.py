import setuptools

name = 'vmi'
version = '0.3.12'

with open('README.md', 'r', encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name=name,
    version=version,
    author='sjtu_6547',
    author_email='88172828@qq.com',
    description='Visual Medical Innovation powered by WANGYiping',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='http://www.med-3d.top:1111/f/e386e5d3c12f4aaeb523/',
    keywords='Qt PySide2 SimpleITK itk vtk pythonocc-core OpenCASCADE CGAL',
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=['PySide2>=5.13',
                      'SimpleITK>=1.2',
                      'vtk>=8.1',
                      'pydicom>=1.3',
                      'numpy>=1.17',
                      'scipy'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
