# (1)export PATH=$PATH:$HOME/.local/bin
# (2)python3 setup.py sdist bdist_wheel
#
# run Twine to upload all of the archives under dist:
# (3)twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
# sudo pip install mmWave -U
#
# vitalSign.py v0.0.8
#
# highAccuracy v0.0.4
#       v0.0.4 fix for Jetson nano
#
# peopleMB : v0.0.3
#      upgrade 0.0.18 :2019/07/03
#
# srradar.py : v0.0.1 :2019/10/03
# v0.1.19 : add srradar.py
#
# people3D.py : v0.0.1 :2019/10/22
#


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mmWave",
    version="0.1.20",
    author="Bighead Chen",
    author_email="zach_chen@joybien.com",
    description="Joybien mmWave (Batman-101/301) Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.joybien.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
