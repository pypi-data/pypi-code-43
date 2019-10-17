import setuptools
from distutils.core import setup
from pathlib import Path

thisdir = Path(__file__).parent
readme = thisdir / 'README.md'
with open(readme, encoding='utf-8') as f:
    long_description = f.read()



setup(
    name="urlunshort3",  # How you named your package folder (MyLib)
    packages=setuptools.find_packages(),
    version="0.3",  # Start with a small number and increase it with every change you make
    license="BSD",  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description="Take a URL, compare to known shortening services, and expand it. A python3 rewrite of https://pypi.org/project/urlunshort/",  # Give a short description about your library
    long_description=long_description,
    author="remotephone",  # Type in your name
    author_email="remotephone@gmail.com",  # Type in your E-Mail
    url="https://github.com/user/reponame",  # Provide either the link to your github or to your website
    keywords=["urlshorten", "expand", "security"],  # Keywords that define your package best
    install_requires=["requests>=2.22.0"],  # I get to this in a second
    classifiers=[
        "Development Status :: 3 - Alpha",  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Intended Audience :: Information Technology",  # Define that your audience are developers
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: BSD License",  # Again, pick a license
        "Programming Language :: Python :: 3.6",
    ],
)
