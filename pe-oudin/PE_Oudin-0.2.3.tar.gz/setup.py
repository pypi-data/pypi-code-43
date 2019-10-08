import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PE_Oudin",
    version="0.2.3",
    author="Dror Paz",
    author_email="pazdror@gmail.com",
    description="Calculate potential evapotranspiration from temperature",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/pazdror/potEvap",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Topic :: Scientific/Engineering :: Atmospheric Science"
    ],
    python_requires='>=3.6',
)
