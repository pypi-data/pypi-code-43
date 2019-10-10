from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="zlparse",
    version="1.5.1",
    author="lanmengfei",
    author_email="865377886@qq.com",
    description="深圳市筑龙科技的工作-筑龙解析包",
    long_description=open("README.txt", encoding="utf8").read(),

    url="https://github.com/lanmengfei/testdm",

    packages=find_packages(),

    package_data={  # "zhulong.hunan":["profile"]
        "zlparse.parse_diqu": ['list.json', 'list2.json'],
        "zlparse.parse_time": ['quyu_time_func.json','Readme.txt'],
        "zlparse.parse_project_code": ['patterns.json'],
        "zlparse.zlshenpi": ['shenpi_func.json']
    },

    install_requires=[
        "jieba",
        "beautifulsoup4>=4.6.3",
        "lmfscrap>=1.1.0",
        "lmf>=2.1.6",
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
