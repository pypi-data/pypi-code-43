import pathlib
from setuptools import setup, find_packages
from mifaser import __version__, name

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name=name,
    version=__version__,
    keywords="microbiome, metagenome,function annotation",
    description="""a python package for super-fast and accurate annotation of molecular functionality
    using read data without prior assembly or gene finding""",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/bromberglab/mifaser",
    author="Chengsheng Zhu, Maximilian Miller",
    author_email="mmiller@bromberglab.com",
    license="NPOSL-3.0",
    python_requires='>=3.6',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
    ],
    entry_points = {
        'console_scripts': ['mifaser=mifaser.__main__:main'],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Natural Language :: English",
        "Operating System :: OS Independent"
    ],  
    project_urls={
        "Bug Tracker": "https://bitbucket.org/bromberglab/mifaser/issues",
        "Documentation": "https://bitbucket.org/bromberglab/mifaser/wiki/docs",
        "Source Code": "https://bitbucket.org/bromberglab/mifaser",
    }
)
