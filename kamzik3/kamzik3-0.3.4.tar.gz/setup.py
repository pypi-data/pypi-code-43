import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kamzik3",
    version="0.3.4",
    author="Martin Domaracky",
    author_email="martin.domaracky@desy.de",
    description="Device controlling framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
    ],
    install_requires=[
        "numpy>=1.16.4",
        "pyzmq>=18.0.2",
        "pint>=0.9",
        "bidict>=0.18.1",
        "natsort>=6.0.0",
        "pyqt5>=5.13.0",
        "pyqtgraph>=0.10.0",
        "pyserial>=3.4",
        "oyaml>=0.9",
        "pydaqmx>=1.4.2",
    ],
    python_requires='>=3.6',
)