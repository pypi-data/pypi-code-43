
from setuptools import setup, find_packages            #这个包没有的可以pip一下

setup(
    name = "aios-test",      #这里是pip项目发布的名称
    version = "0.0.1",  #版本号，数值大的会优先被pip
    keywords = ("aios", "package"),
    description = "aios package",
    long_description="",
    license = "MIT Licence",

    url = "",     #项目相关文件地址，一般是github
    author = "",
    author_email="wang.xiao@intellif.com",

    packages = find_packages(exclude=["test.*"]),
    include_package_data = True,
    platforms = "any",
    install_requires=[
        'SQLAlchemy==1.3.1',
        'mxnet==1.3.1',
        'numpy==1.14.6',
        'opencv-python==4.1.1.26',
        'moment==0.8.2'
    ],  #这个项目需要的第三方库
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)