from pathlib import Path

from setuptools import find_packages, setup

import versioneer

rootpath = Path(__file__).parent.absolute()


def read(*parts):
    return open(rootpath.joinpath(*parts), "r").read()


with open("requirements.txt") as f:
    tests_require = f.readlines()
install_requires = [t.strip() for t in tests_require]


setup(
    name="ioos_tools",
    python_requires=">=3.5",
    version=versioneer.get_version(),
    description="Misc functions for IOOS notebooks",
    license="BSD-3-Clause",
    long_description=f'{read("README.md")}',
    long_description_content_type="text/markdown",
    author=["Rich Signell", "Filipe Fernandes"],
    author_email="ocefpaf@gmail.com",
    url="https://github.com/pyoceans/ioos_tools/",
    keywords=["oceanography", "data analysis", "IOOS"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    platforms="any",
    packages=find_packages(),
    extras_require={"testing": ["pytest"]},
    install_requires=install_requires,
    cmdclass=versioneer.get_cmdclass(),
    zip_safe=False,
)
