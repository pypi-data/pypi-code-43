from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="lmfinstall",
    version="1.4.6",
    author="lanmengfei",
    author_email="865377886@qq.com",
    description="安装东西如鱼得水",
    long_description=open("README.rst",encoding="utf8").read(),
 
    url="https://github.com/lanmengfei/testdm",
    packages=find_packages(),

    package_data={#"zhulong.hunan":["profile"]
   
    "lmfinstall.postgresql":["plpython/*.so",'plpython/*.txt'],
    "lmfinstall.v1":["plpython/*.so",'plpython/*.txt',"hadoopconf/*","hdprepo/*"],
    "lmfinstall.v2":["plpython/*.so",'plpython/*.txt',"hadoopconf/*","gpplpython/*"],


  
    },
    install_requires=[
        "fabric",
        "invoke"
        ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5"
    ],
)