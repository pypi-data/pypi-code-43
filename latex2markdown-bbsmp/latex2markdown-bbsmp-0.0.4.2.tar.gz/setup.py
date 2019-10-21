#coding=utf-8
# from distutils.core import setup
from setuptools import setup, find_packages

setup(
        name='latex2markdown-bbsmp',
        author="PengMo",
        author_email="qinmetec@163.com",
        version='0.0.4.2',
        py_modules=['latex2markdown-bbsmp'],
        include_package_data=True,
        packages=find_packages("."),
        install_requires=['distribute'],
        package_data={
            'latex2markdown-bbsmp': ['config/*.xml', 'config/*.tet', 'config/*.md'],
         },
        # scripts=['bin/converted_latex_sample.md', 'bin/latex_sample.tex'],
        url="https://github.com/bbsmp/LaTeX2Markdown.git",
        description="Forked from Andrew's masterpiece：https://github.com/ajtulloch/LaTeX2Markdown,  An AMS-LaTeX compatible converter that maps a subset of LaTeX to Markdown/MathJaX.",
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Programming Language :: Python",
            "Topic :: Scientific/Engineering :: Mathematics",
            "Topic :: Software Development :: Documentation",
            "Topic :: Text Processing :: Markup",
            "Topic :: Text Processing :: Markup :: LaTeX",
            "Topic :: Text Processing :: Markup :: HTML"
            ],
        long_description=open("README.txt").read()
        )
