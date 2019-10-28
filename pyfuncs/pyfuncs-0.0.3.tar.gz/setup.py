import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyfuncs",
    version="0.0.3",
    author="zhangzhch",
    author_email="zhangzhch2013@foxmail.com",
    description="common methods",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fishs-x/pyfuncs",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
