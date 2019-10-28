import setuptools
from pkg_resources import DistributionNotFound, get_distribution

# The directory containing this file
with open("README.md", "r") as fh:
    long_description = fh.read()


def get_dist(pkgname):
    try:
        return get_distribution(pkgname)
    except DistributionNotFound:
        return None


install_deps = []

if get_dist('tensorflow') is None and get_dist('tensorflow_gpu') is None:
    install_deps.append('tensorflow>=2.0.0')
elif get_dist('tensorflow_gpu') is not None:
    install_deps.append('tensorflow-gpu>=2.0.0')

# This call to setup() does all the work
setuptools.setup(
    name="ganify",
    version="1.0.7",
    description="An Easy way to use GANs for data augmentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arnonbruno/ganify",
    author="Arnon Bruno",
    author_email="asantos.quantum@gmail.com",
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[install_deps[0], 'pandas>=0.25',
                      'numpy>=1.16', 'scikit-learn>=0.21', 'matplotlib>=3.1',
                      'tqdm>=4.15'],
)
