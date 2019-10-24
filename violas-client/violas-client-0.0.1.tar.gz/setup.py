import setuptools
import hashlib

with open("README.md", "r") as fh:
    content = fh.read()
    arr = content.split("\n")
    long_description = "\n".join(arr[3:])

install_requires=[
        'canoser>=0.5.2',
        'protobuf',
        'grpcio',
        'more-itertools',
        'PyNaCl',
        'pygments',
        'requests',
        "toml",
        'mnemonic'
    ]

if not 'sha3_256' in hashlib.algorithms_available:
    #only exec under sdist, not bdist_wheel
    #if add pysha3 always, it will be failed under windows without c++ compiler installed.
    install_requires.append("pysha3")

setuptools.setup(
    name="violas-client",
    version="0.0.1",
    author="Xing-Huang",
    author_email="hxg@palliums.org",
    description="A CLI inteface Violas client and Python API for Violas blockchain.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/violas-project/violas-client.git",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts':[
            'violas = libra.cli.main:main',
            'violas_shell = libra.shell.libra_shell:main'
        ]
    },
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
