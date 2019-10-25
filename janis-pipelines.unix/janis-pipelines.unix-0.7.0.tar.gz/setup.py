from setuptools import setup, find_packages

# Version information is found in the __init__ file of `janiscore/`
DESCRIPTION = "Unix tools and data types for Janis"

######## SHOULDN'T NEED EDITS BELOW THIS LINE ########

with open("./README.md") as readme:
    long_description = readme.read()

vsn = {}
with open("./janis_unix/__meta__.py") as fp:
    exec(fp.read(), vsn)
__version__ = vsn["__version__"]

setup(
    name="janis-pipelines.unix",
    version=__version__,
    description=DESCRIPTION,
    url="",
    author="Michael Franklin, Evan Thomas, Mohammad Bhuyan",
    author_email="michael.franklin@petermac.org",
    license="GNU",
    keywords=["pipelines", "bioinformatics", "workflows"],
    packages=["janis_unix"]
    + ["janis_unix." + p for p in sorted(find_packages("./janis_unix"))],
    install_requires=["janis-pipelines.core >= 0.7.0"],
    entry_points={
        "janis.extension": ["unix=janis_unix"],
        "janis.tools": ["unix=janis_unix.tools"],
        "janis.types": ["unix=janis_unix.data_types"],
    },
    zip_safe=False,
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
