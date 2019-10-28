"""Setup file for the project.

Most of the static configuration is in "setup.cfg".
"""


from setuptools import setup, find_packages
import versioneer


setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={"console_scripts": ["ptvpy = ptvpy.__main__:main"]},
)
