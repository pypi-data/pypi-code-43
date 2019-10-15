import setuptools

REQUIRES = [
    'biopython==1.73',
    'ete2==2.3.10',
]

__version__ = "Undefined"
for line in open('mitos/__init__.py'):
    if (line.startswith('__version__')):
        exec(line.strip())

setuptools.setup(
    name="mitos",
    version=__version__,
    author="Matthias Bernt",
    author_email="bernt@informatik.uni-leipzig.de",
    description="MITOS: de novo annotation of metazoan mitochondrial genomes",
    long_description="This package contains MITOS. A tool for the de novo annotation of metazoan mitochondrial genomes and some auxilliary tools for the handling of mitochondrial genome data.",
    url="http://mitos.bioinf.uni-leipzig.de",
    download_url="https://gitlab.com/Bernt/MITOS",
    packages=setuptools.find_packages(),
    scripts=["runmitos.py", "analyse.py", "gcpp.py", "geneorder.py",
             "getfeatures.py", "getinfo.py", "refseqsplit.py", "subseq.py",
             "taxtree.py", "mitos/plotprot.R", "mitos/plotstst.R", "mitos/plotrna.R"],
    include_package_data=True,
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    install_requires=REQUIRES,
)
