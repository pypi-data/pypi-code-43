import setuptools


setuptools.setup(
    name="BDPapi",
    version="0.0.11",
    author="blue",
    author_email="xuguozheng@haizhi.com",
    description="BDP api",
    long_description="BDP api",
    long_description_content_type="text/markdown",
    url="https://github.com/haizhiml/BDP",
    packages=setuptools.find_packages(),
    install_requires=['numpy>=1.16.2', 'requests>=2.21.0'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
