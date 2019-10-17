from setuptools import setup
from setuptools import find_packages

from coderadio import __version__


def readme():
    with open("README.md") as f:
        return f.read()


required = [
    "prompt-toolkit==2.0.5",
    "python-vlc==3.0.102",
    "pyradios==0.0.17",
    "notify-send==0.0.13",
    "pygments==2.4.2",
    "streamscrobbler3==0.0.4",
]


setup(
    name="coderadio",
    version=__version__,
    description="Terminal radio for geeks.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    keywords="radio browser web terminal",
    author="André P. Santos",
    author_email="andreztz@gmail.com",
    url="https://github.com/andreztz/coderadio",
    license="MIT",
    packages=find_packages(),
    install_requires=required,
    entry_points={"console_scripts": ["coderadio=coderadio.__main__:main"]},
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Programming Language :: Python :: 3.7",
    ],
)
