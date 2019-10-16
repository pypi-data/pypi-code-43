from setuptools import setup
import versioneer

requirements = [
    'numpy', 'vtk', 'jupyter', 'pandas', 'requests', 'seaborn', 'versioneer'
]

setup(
    name='smlmvis',
    license='GPLv3',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Superresolution visualization of 3D protein localization data from a range of microscopes",
    author="Ben Cardoen",
    author_email='bcardoen@sfu.ca',
    url='https://github.com/bencardoen/smlmvis',
    download_url='https://github.com/bencardoen/smlmvis/archive/v0.0.5.tar.gz',
    packages=['smlmvis'],
    install_requires=requirements,
    keywords='smlmvis',
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ]
)
