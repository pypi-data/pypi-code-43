import setuptools


setuptools.setup(
    setup_requires=['pbr'],
    packages=setuptools.find_packages(),
    package_dir={'':'src'},
    pbr=True,
)
