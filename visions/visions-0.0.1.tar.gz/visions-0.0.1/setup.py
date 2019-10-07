from setuptools import setup
from os.path import basename, splitext
from glob import glob
from setuptools import find_packages


setup(
    name="visions",
    version="0.0.1",
    description="Visions",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    install_requires=[],
    include_package_data=True,
    python_requires=">=3.5",
)
