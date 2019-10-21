import setuptools
f = open('version.txt')
versions = f.read().replace('.','')
f.close()
v = int(versions)
v += 1
v = str(v).zfill(4)
version = f"{v[0]}.{v[1]}.{v[2]}{v[3]}"
f = open('version.txt','w')
f.write(version)
f.close()
print(version)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyzik",
    version=version,
    author="FJ",
    author_email="fredericboltzmann@gmail.com",
    description="functions packages for my physic's students",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=['uncertainties','astroquery','ezsheets','mendeleev==0.4.5',
                     'wget','chempy','sti-LabJackPython','art','cirpy','jcamp',
                     'websocket_client','sjcl'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)