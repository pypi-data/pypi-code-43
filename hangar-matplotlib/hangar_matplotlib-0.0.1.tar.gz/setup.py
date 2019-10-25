import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hangar_matplotlib",
    version="0.0.1",
    author="hhsecond",
    author_email="sherin@tensorwerk.com",
    description="Matplotlib plugin for hangar",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hhsecond/hangar_matplotlib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['matplotlib'],
    entry_points={'hangar.external.plugins': 'matplotlib = hangar_pil:HangarMatplotlib'}
)
