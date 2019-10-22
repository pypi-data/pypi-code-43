import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="siot",
    version="0.0.7",
    author="luoyufenglalala",
    author_email="yufeng.luo@dfrobot.com",
    description="A package for siot publish and subscribe",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luoyufenglalala/DFRobot_siot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
)