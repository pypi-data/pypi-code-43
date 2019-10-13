from setuptools import setup, find_packages

s = setup(
    name="MachineIt",
    version="1.0.1",
    license="MIT",
    description="MachineIt is a package which compares data...",
    url='https://github.com/gitnark/MachineIt.git',
    packages=find_packages(),
    install_requires=[],
    python_requires = ">= 3.4",
    author="Conor Venus",
    author_email="narktrading@gmail.com",
    )