from setuptools import setup
import os
import sys

os.system("pip install pylib3")
try:
    import pylib3
except ImportError as err:
    sys.exit(err)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_required_packages():
    """
    Reads the requirements packages from requirement.txt file

    :return list of package names and versions (i.e ['requests==2.19.1'])
    """
    file_name = 'requirements.txt'
    file_path = os.path.join(BASE_PATH, file_name)
    if not os.path.exists(file_path):
        sys.exit("The '{}' file is missing...".format(file_name))

    required_packages = open(file_path).readlines()
    return [package.rstrip() for package in required_packages]


with open("README.md") as ifile:
    long_description = ifile.read()

package_name = 'pygenerator3'
setup(
    name=package_name,
    version=pylib3.get_version(
        caller=__file__,
        version_file='{}_VERSION'.format(package_name.upper())
    ),
    include_package_data=True,
    packages=[package_name],
    install_requires=get_required_packages(),
    scripts=['{}/scripts/package-generator'.format(package_name)],
    data_files=[(os.path.join('docs', package_name), ['README.md'])],
    url='https://gitlab.com/shlomi.ben.david/{}'.format(package_name),
    author='Shlomi Ben-David',
    author_email='shlomi.ben.david@gmail.com',
    description='Python Package Generator',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
