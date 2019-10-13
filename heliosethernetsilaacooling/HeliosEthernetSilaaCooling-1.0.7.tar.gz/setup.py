import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="HeliosEthernetSilaaCooling",
    version="1.0.7",
    author=["Alexander Teubert", "Stefanie Fiedler"],
    packages=["HeliosEthernetSilaaCooling"],
    description="This package is designed to control a Helios KWL EC 170 W via Modbus TCP/IP",
    url="https://gogs.es-lab.de/SilaaCooling/Simulationsmodell_SilaaCooling/src/master/Helios%20Modbus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
    ],
    python_requires='>=3.5.2',
    install_requires=['EasyModbusSilaaCooling','pyserial'],
)
