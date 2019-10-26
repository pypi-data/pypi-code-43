import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="elasticsearch_tool",
    version="0.9.8",
    author="haiton",
    author_email="642641850@qq.com",
    description="some like orm for elasticsearch, elasticsearch的辅助工具, 提供类似ORM的操作方式, 此版本提高了稳定性,解决了出现的bug",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=['elasticsearch==5.0.0', ],
    python_requires='>=3.6',
)
