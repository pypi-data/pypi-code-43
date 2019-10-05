from setuptools import find_packages, setup
import jelm

pkg_name = 'jelm'

version = jelm.__version__


with open("README.md") as fp:
    long_description = fp.read()

setup(
    name=pkg_name,
    version=version,
    description="python graph description",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
    url='https://github.com/endremborza/{}'.format(pkg_name),
    keywords='network graph json edgelist framework',
    author='Endre Márk Borza',
    author_email='endremborza@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
)
