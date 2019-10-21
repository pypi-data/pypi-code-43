from setuptools import setup

setup(
    name="pycws",
    version='0.2',
    description="A python api to cws",
    url="http://github.com/javadogs/pycws",
    author="Alexander Pilz",
    author_email="info@syslab.com",
    license="APACHE 2.0",
    zip_safe=False,
    packages=["pycws", "pycws.tests"],
    install_requires=["zeep", "pytest", "requests"],
)
