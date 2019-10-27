"""\
Python package to get data about arXiv preprints in certain math
research fields and study some trends in hyper-specialization and growth rate
increase of scientific production in those fields.

Collected data for each preprint:
    year,
    authors,
    number of pages (PDF format).
"""

import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    sys.exit("""Error: Setuptools is required for installation.
    -> http://pypi.python.org/pypi/setuptools""")

setup(
    name = "Arxivtrends",
    version = "0.0.2",
    description = "An ArXiV scraper to retrieve records from given research areas in mathematics and detect some trends in hyper-specialization and growth rate increase of scientific production in those fields.",
    author = "Alessandro Marinelli",
    author_email = "alessandromarinelli7@gmail.com",
    url = "https://github.com/amarine7/Arxivtrends",
    #download_url = "",
    py_modules = [""],
    packages=['arxivtrends'],
    include_package_data = True,
    keywords = ["hyper-specialization", "scraper", "api", "arXiv"],
    license = "MIT",
    classifiers = ["Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research"],
)
