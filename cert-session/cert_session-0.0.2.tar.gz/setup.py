'''Used by distutils'''

import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="cert_session",
    version="0.0.2",
    author="Lawrence Siden",
    author_email="lsiden@gmail.com",
    description="'requests' session that appends custom certificate authority",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/lsiden/cert_session",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['requests']
)
