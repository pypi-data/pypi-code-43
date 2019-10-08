from distutils.core import setup

setup(
    name="dockhere",
    version="0.0.4",
    description="Run a container in the current directory",
    author="Ian Norton",
    author_email="inorton@gmail.com",
    url="https://gitlab.com/cunity/dockhere",
    packages=["dockhere"],
    platforms=["any"],
    license="License :: OSI Approved :: MIT License",
    long_description="Run docker using the current directory"
)
