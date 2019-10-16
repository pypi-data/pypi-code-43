from setuptools import setup, find_packages

setup(
    name="zhangyx_test_1",
    version="0.50",
    keywords=("test", "zhangyx_test_1"),
    description="My test module",
    long_description="My test module for Jupyter notebook call external python file",
    license="MIT Licence",

    url="http://www.csdn.net",
    author="Zhang Yexing",
    author_email='1207979407@qq.com',

    packages=find_packages(),
    # packages=['zhangyx_test_1', 'zhangyx_test_1.example_pkg'],
    include_package_data=True,
    platforms="any",
    py_modules=["foo", "sunflower"],

    install_requires=[
        'setuptools>=16.0',
        'turtle>=0.0.2',
    ],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    python_requires='>=3.6',
    scripts=[],

    # 此项需要，否则卸载时报 windows error
    zip_safe=False
)
