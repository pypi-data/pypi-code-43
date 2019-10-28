import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.read().splitlines()

setuptools.setup(
    name="MESA_Plotter",
    version="0.1.9",
    author="Thomas Steindl",
    author_email="thomas.steindl@uibk.ac.at",
    description="Plot the evolution of pre-main sequence stars in various way. A tool for the asteroseismology group of the university of Innsbruck, Austria.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Steinerkadabra/MESA_Plotter",
    install_requires=requirements,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts':['MESA_Plotter = MESA_Plotter.__main__:main']
    }
)
