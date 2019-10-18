import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dict_wrapper",
    version="0.0.3",
    packages=['dict_wrapper'],
    author="duanyongqiang",
    author_email="sysuduanyongqiang@163.com",
    description="A userful package to use '.' to visit value of dict",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yyonging/dict_wrapper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
)
