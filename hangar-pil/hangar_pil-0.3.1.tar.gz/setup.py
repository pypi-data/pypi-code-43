import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hangar_pil",
    version="0.3.1",
    author="hhsecond",
    author_email="sherin@tensorwerk.com",
    description="PIL plugin for hangar",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hhsecond/hangar_pil",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['Pillow'],
    entry_points={'hangar.external.plugins': 'pil = hangar_pil:HangarPIL'}
)
