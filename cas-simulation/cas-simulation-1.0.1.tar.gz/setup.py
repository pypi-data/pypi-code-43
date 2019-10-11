import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cas-simulation",
    version="1.0.1",
    author="James Macdonell",
    author_email="jmacdone@csusb.edu",
    description="Simulate an authentication workflow for CAS, particularly for service checks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/csusb/cas-simulation",
    packages=setuptools.find_packages(),
    install_requires=['mechanize>=0.3.7'],
    entry_points = {
        'console_scripts': ['check_cas_sp=cas_simulation.check_cas_sp:main'],
    }
)
