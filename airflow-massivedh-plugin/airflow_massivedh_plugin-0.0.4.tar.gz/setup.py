import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "airflow_massivedh_plugin",
    version = "0.0.4",
    author = "Paolo Coletta",
    author_email = "paolo.coletta@massivedh.com",
    description = (
        "Apache-AirFlow items to support automation at Massive Data Heights" ),
    license = "BSD",
    keywords = "api automation",
    url = "http://packages.python.org/airflow_massivedh_plugin",
    packages=['airflow_massivedh_plugin'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    entry_points = {
        'airflow.plugins': [
            'airflow_massivedh_plugin = airflow_massivedh_plugin.massive_plugin:MassiveAirflowPlugin'
        ]
    }
)