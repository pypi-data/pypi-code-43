from setuptools import setup, find_packages


def get_version():
    with open("./twelve_step/version.txt", "r") as version_file:
        return version_file.readline()


setup(
    name="twelve_step",
    packages=find_packages(exclude=["*test*"]),
    package_data={"twelve_step": ["version.txt"]},
    version=get_version(),
    license="MIT",
    description="A package to analyze project dependencies.",
    author="Olivier Beaulieu",
    author_email="beaulieu.olivier@hotmail.com",
    url="https://github.com/OLBEA20/twelve-step",
    keywords=["Dependency", "Analysis", "Dependencies", "Graph"],
    install_requires=["jivago-streams"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points={"console_scripts": ["twelve-step=twelve_step.main:main"]},
)
