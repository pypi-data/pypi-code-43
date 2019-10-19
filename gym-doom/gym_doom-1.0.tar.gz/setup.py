from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name='gym_doom',
    version='1.0',
    author="Sergiy Isakov",
    author_email="marvine.si@gmail.com",
    description="Gym environment for VizDoom",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MarvineGothic/gym_doom",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
