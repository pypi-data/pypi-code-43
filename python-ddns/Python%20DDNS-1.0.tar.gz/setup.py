# pylint: disable=invalid-name, missing-docstring, line-too-long
import os
from setuptools import setup
# https://medium.com/@pypripackages/using-gitlab-pipelines-to-deploy-python-packages-in-production-and-staging-environments-8ab7dc979274
if os.environ.get('CI_COMMIT_TAG'):
    v = os.environ['CI_COMMIT_TAG']
else:
    try:
        v = os.environ['CI_JOB_ID']
    except KeyError as ke:
        v = "local_build"

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="Python DDNS",
    version=v,
    author="Jacob White",
    author_email="jake@jwhite.network",
    install_requires=['requests'],
    package_data={'': ['*.conf']},
    description="A DDNS client written in python that updates the A record on Cloudflare with the current IP of this device.",
    url="https://gitlab.com/jwhite1st/python-ddns",
    project_urls={
        "Issues": "https://gitlab.com/jwhite1st/python-ddns/issues",
    },
    license='GPL-3.0',
    packages=['python_ddns'],
    python_requires='>=3',
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: System :: Installation/Setup",
        "Development Status :: 2 - Pre-Alpha"
    ],
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    entry_points={
        "console_scripts": ['python-ddns=python_ddns.python_ddns:main',]
        },

)
