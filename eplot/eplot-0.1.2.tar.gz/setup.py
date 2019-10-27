import setuptools

#with open("readme.rst", "r") as fh:
#    long_description = fh.read()

setuptools.setup(
    name="eplot",
    version="0.1.2",
    author="pipixiu",
    author_email="1783198484@qq.com",
    description="pandas interface for pyecharts",
#    long_description=long_description,
    #long_description_content_type="text/markdown",
    url="https://github.com/pjgao/eplot",
    install_requires=[
        "pandas",
        'pyecharts',
        'numpy'
        ],
    packages=setuptools.find_packages(),    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)