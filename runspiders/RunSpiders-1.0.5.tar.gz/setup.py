# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="RunSpiders",
    version="1.0.5",
    description="Some predefined web crawlers",
    long_description=open('README.rst').read(),  # todo write README seriously
    author='Ijustwantyouhappy',
    author_email='',
    maintainer='',
    maintainer_email='',
    license='MIT',  # todo write LICENSE seriously
    packages=find_packages(),
    zip_safe=False,
    package_data = {
        '': ['*.recipe']
    },
    platforms=["all"],
    url='',
    install_requires=["requests>=2.14.2",
                      "beautifulsoup4>=4.5.1",
                      "jinja2>=2.10.1",
                      "pycryptodome>=3.8.2",
                      "gevent>=1.1.2",
                      "tqdm>=4.32.2"],
    classifiers=[
        "Environment :: Web Environment",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft',
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)