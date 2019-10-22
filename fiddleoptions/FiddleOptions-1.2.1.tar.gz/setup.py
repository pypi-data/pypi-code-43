# coding: utf-8

"""
    Fiddle Options Platform
    
"""


from setuptools import setup, find_packages  # noqa: H301
# To upload the library to pypi:
# python3 setup.py sdist bdist_wheel
# twine upload dist/*
#
#
#

REQUIRES = ["urllib3 < 1.23, >=1.15", "six >= 1.10", "certifi", "python-dateutil", "gym >= 0.15.3", "cachetools >=3.1.1"]

setup(
    name='FiddleOptions',
    version='1.2.1',
    description="Fiddle Options Platform",
    author_email="dovlex@gmail.com",
    url="https://github.com/vblagoje",
    keywords=["Fiddle Options Platform"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
)
