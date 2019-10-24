import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="airsimneurips",
    version="1.1.0",
    author="Ratnesh Madaan, Matthew Brown, Nicholas Gyde, Sai Vemprala, Shital Shah",
    author_email="ratnesh.madaan@microsoft.com, v-mattbr@microsoft.com, v-nigyde@microsoft.com, sai.vemprala@microsoft.com, shitals@microsoft.com",
    description="Python package for Game of Drones - A NeurIPS 2019 Competition, built on Microsoft AirSim - an open source simulator based on Unreal Engine for autonomous vehicles from Microsoft AI & Research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/microsoft/AirSim-NeurIPS2019-Drone-Racing",
    packages=setuptools.find_packages(),
	license='MIT',
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
          'msgpack-rpc-python', 'numpy <= 1.16'
    ]
)
