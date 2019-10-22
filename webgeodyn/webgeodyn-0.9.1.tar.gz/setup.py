from setuptools import setup, find_packages
import os.path


def local_file(name):
    return os.path.relpath(os.path.join(os.path.dirname(__file__), name))


# Get version number from _version.py
__version__ = None
with open(local_file("webgeodyn/_version.py")) as o:
    exec(o.read())
assert __version__ is not None

with open(local_file('AUTHORS.txt')) as authors_file:
    authors = authors_file.read().replace('\n', ', ')

setup(
    name='webgeodyn',
    version=__version__,
    packages=find_packages(),
    author=authors,
    author_email='loic.huder@univ-grenoble-alpes.fr',
    url='https://gricad-gitlab.univ-grenoble-alpes.fr/Geodynamo/webgeodyn',
    description="A web-based plot tool to visualize Earth core flows",
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    install_requires=["tornado", "numpy", "scipy>1.1", "h5py"],
    test_suite="webgeodyn.tests",
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: JavaScript',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization'
    ]
)

