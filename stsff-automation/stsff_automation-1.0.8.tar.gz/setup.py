import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stsff_automation",
    version="1.0.8",
    author="StepToSky & FlightFactor",
    author_email="technical@flightfactor.aero",
    description="A Python library with some stsff stuff for automation, utils, vcs_info, helpers, build systems and etc",
    long_description=long_description,
    url="https://git.flightfactor.aero/dev-ops/stsff-automation-lib-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Development Status :: 4 - Beta",
    ],
    install_requires=[
        "semantic_version>=2, <3",
        #'conan>=3.11',
    ],
    entry_points={
        'console_scripts': [
            'stsff_automation_gen_cmake_desc = stsff_automation.generate_description:main'
        ]
    },
)